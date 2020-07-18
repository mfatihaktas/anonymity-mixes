import numpy as np

from sim_objs import *

# *************************************  Batch Mix  ****************************************** #
# n servers with Poisson arrivals, once any k servers are busy, Hol is immediately released.
class BatchMix(object):
	def __init__(self, env, _id, n, k, adversary=None):
		self.env = env
		self._id = _id
		self.n = n
		self.k = k
		self.adversary = adversary

		self.i_q_l = []
		for i in range(self.n):
			self.i_q_l.append(SlaveQ(_id=i, env=env) )

		self.start_time = env.now
		self.q = simpy.Store(env)
		self.wait_for_attack = env.process(self.listen_adversary() )
		self.num_batch_departures_wtarget = 0

	def __repr__(self):
		return "BatchMix[_id= {}, n={}, k={}]".format(self._id, self.n, self.k)

	def state(self):
		ql_l = [self.i_q_l[i].length() for i in range(self.n) ]
		return ','.join(map(str, ql_l) )

	def qt_l(self):
		l = []
		for q in self.i_q_l:
			l.extend(q.qt_l)
		return l

	def ET_ET2(self):
		ET_l, ET2_l = [], []
		for q in self.i_q_l:
			ET_l.append(q.Eqt() )
			ET2_l.append(q.Eqt2() )
		return np.mean(ET_l), np.mean(ET2_l)

	def throughput(self):
		n_released = sum([q.n_released for _, q in enumerate(self.i_q_l) ] )
		return n_released/(self.env.now - self.start_time)

	def put(self, m):
		slog(DEBUG, self.env, self, "recved", m)
		self.i_q_l[m.flow_id].put(m)

		o_l = []
		for i, q in enumerate(self.i_q_l):
			if q.length():
				o_l.append(i)

		if len(o_l) >= self.k:
			for i in o_l:
				self.i_q_l[i].release()

			if self.adversary is not None:
				if 0 in o_l: # 0 is the target
					self.num_batch_departures_wtarget += 1
					self.adversary.batch(o_l)
					self.q.put("")

	def listen_adversary(self):
		while True:
			yield self.q.get()

			# log(INFO, "adversary.state= {}".format(self.adversary.state()))
			if self.adversary.is_complete():
				break

"""
Treat the participants as n bins.
For each observed participant, place a ball in its corresponding bin.
Target is revealed as soon as the height of a bin is greater than the rest.
"""
class IntersectionAttack(object):
	def __init__(self, n, k):
		self.n = n
		self.k = k

		# 0th index points to target
		self.bin_l = [0 for _ in range(n)]
		self.second_max_bin_height = 0 # target_bin will always have the max height

	def __repr__(self):
		return 'IntersectionAttack[n={}, k={}]'.format(self.n, self.k)

	def state(self):
		return 'target_bin= {}, second_max_bin_height= {}'.format(self.bin_l[0], self.second_max_bin_height)

	def batch(self, i_l):
		for i in i_l:
			self.bin_l[i] += 1
			if i:
				if self.bin_l[i] > self.second_max_bin_height:
					self.second_max_bin_height = self.bin_l[i]

	def is_complete(self):
		return self.bin_l[0] > self.second_max_bin_height;

# *************************************  SamplekMix  ****************************************** #
## n servers with Poisson arrivals, every time a message arrives, k queues are selected at uniformly random and released.
class SamplekMix(BatchMix):
	def __init__(self, env, n, k, pd=None):
		super().__init__(env, _id, n, k)
		self.pd = pd if pd is not None else 1/n

	def __repr__(self):
		return 'SamplekMix[n={}, k={}]'.format(self.n, self.k)

	def put(self, p):
		slog(DEBUG, self.env, self, "recved", p)
		self.i_q_l[p.flow_id].put(p)

		l = list(range(self.n) )
		l.remove(p.flow_id)
		if np.random.uniform(0, 1) <= self.pd:
			i_l = [p.flow_id] + [l[i] for i in np.random.choice(self.n-1, self.k-1, replace=False) ]
		else:
			i_l = [l[i] for i in np.random.choice(self.n-1, self.k, replace=False) ]
		# print("i_l= {}".format(i_l) )
		for i in i_l:
			self.i_q_l[i].release()

# *************************************  True_SamplekMix  ****************************************** #
## n servers with Poisson arrivals.
## Every time a message arrives, *and if all queues are non-empty*, then k queues are selected at uniformly random and released.
class True_SamplekMix(BatchMix):
	def __init__(self, env, _id, n, k):
		super().__init__(env, _id, n, k)

	def __repr__(self):
		return 'True_SamplekMix[n={}, k={}]'.format(self.n, self.k)

	def put(self, p):
		slog(DEBUG, self.env, self, "recved", p)
		self.i_q_l[p.flow_id].put(p)

		if any(q.length() == 0 for q in self.i_q_l):
			slog(DEBUG, self.env, self, "There is an empty q, won't release any. Received:", p)
			return

		i_l = np.random.choice(self.n, self.k, replace=False)
		slog(DEBUG, self.env, self, "will release q's:", i_l)
		for i in i_l:
			self.i_q_l[i].release()

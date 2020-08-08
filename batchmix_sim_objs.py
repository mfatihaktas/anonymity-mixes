import numpy as np

from sim_objs import *

# *************************************  Batch Mix  ****************************************** #
# n servers with independent arrivals, once any k servers are busy, Hol is immediately released.
class BatchMix(Mix):
  def __init__(self, env, _id, n, k, adversary=None):
    super().__init__(env, _id, n, k)
    self.adversary = adversary

    self.q = simpy.Store(env)
    self.wait_for_attack = env.process(self.listen_adversary() )
    self.num_batch_departures_wtarget = 0

  def __repr__(self):
    return "BatchMix[_id= {}, n={}, k={}]".format(self._id, self.n, self.k)

  def put(self, m):
    slog(DEBUG, self.env, self, "recved", m)
    self.i_q_l[m.flow_id].put(m)

    i_l = []
    for i, q in enumerate(self.i_q_l):
      if q.length():
        i_l.append(i)

    if len(i_l) >= self.k:
      for i in i_l:
        self.i_q_l[i].release()

      if self.adversary is not None and m.flow_id == self.adversary.target_i:
        self.num_batch_departures_wtarget += 1
        self.adversary.batch(i_l)
        self.q.put("")

  def listen_adversary(self):
    while True:
      yield self.q.get()

      # log(INFO, "adversary.state= {}".format(self.adversary.state()))
      if self.adversary.is_complete():
        break

# *************************************  SamplekMix  ****************************************** #
## n servers with independent arrivals, every time a message arrives, k queues are selected at uniformly random and released.
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
## n servers with independent arrivals.
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

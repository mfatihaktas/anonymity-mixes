from log_utils import *
from plot_utils import *
from rvs import Exp

import simpy, heapq, queue, collections, random
import numpy as np

# *******************************  Msg  ****************************** #
class Msg(object):
  def __init__(self, _id, flow_id):
    self._id = _id
    self.flow_id = flow_id

    self.entrance_time = None
    self.delivery_time = None

  def __repr__(self):
    return 'Msg[_id= {}, flow_id= {}]'.format(self._id, self.flow_id)

  def __lt__(self, other):
    return self.delivery_time < other.delivery_time

# ********************************  Intersection attack  ************************************ #
"""
Observe a set of candidates for the target's true recipient at target's each attack window
and keep intersecting them until the true recipient is revealed.
 
Attack window: The time interval between a message generated at the target
and the time it reached its recipient.
m: Min delivery time
M: Max delivery time
"""
class AttackWindow(object):
  def __init__(self, start_time, end_time):
    self.start_time = start_time
    self.end_time = end_time

    self.candidate_s = set()

class IntersectionAttack(object):
  def __init__(self, env, n, m, M, target_i=0):
    self.env = env
    self.n = n
    self.m = m
    self.M = M
    self.target_i = target_i

    self.bin_l = [0 for _ in range(n)]
    self.second_max_bin_height = 0 # target_bin will always have the max height

    self.window_q = collections.deque()
    self.new_window_event = None
    self.msg_delivered_event = None
    self.delivered_msg_i = None
    self.wait = env.process(self.run() )

    self.num_attack_windows = 0
  
  def __repr__(self):
    return 'IntersectionAttack[n= {}, m= {}, M= {}, target_i= {}]'.format(self.n, self.m, self.M, self.target_i)
  
  def state(self):
    return 'target_bin= {}, second_max_bin_height= {}'.format(self.bin_l[self.target_i], self.second_max_bin_height)
  
  def is_complete(self):
    return self.bin_l[self.target_i] > self.second_max_bin_height
  
  def get_candidate_l(self):
    l = []
    for i in range(n):
      if self.bin_l[i] == self.bin_l[self.target_i]:
        l.append(i)
    return l
  
  def msg_generated(self, i):
    slog(DEBUG, self.env, self, "a message originated at id", i)
    if i == self.target_i:
      t = self.env.now
      self.window_q.appendleft(AttackWindow(t + self.m, t + self.M) )
      if self.new_window_event is not None:
        self.new_window_event.succeed()
  
  def msg_delivered(self, i):
    slog(DEBUG, self.env, self, "a message is delivered at id", i)
    if self.msg_delivered_event is not None:
      self.delivered_msg_i = i
      self.msg_delivered_event.succeed()
  
  def run(self):
    while 1:
      if len(self.window_q) == 0:
        slog(DEBUG, self.env, self, "there is no window, will wait for one", "")
        self.new_window_event = self.env.event()
        yield (self.new_window_event)
        self.new_window_event = None
        continue
      
      t = self.window_q[-1].end_time - self.env.now
      self.msg_delivered_event = self.env.event()
      slog(DEBUG, self.env, self, "waiting for window", "time= {}".format(t))
      yield (self.msg_delivered_event | self.env.timeout(t))
      self.msg_delivered_event = None
      
      if self.delivered_msg_i is not None:
        slog(DEBUG, self.env, self, "message will be added as candidate", self.delivered_msg_i)
        for w in self.window_q:
          if self.env.now >= w.start_time and self.env.now <= w.end_time:
            w.candidate_s.add(self.delivered_msg_i)
        self.delivered_msg_i = None
        continue
      
      w = self.window_q.pop()
      slog(INFO, self.env, self, "w.candidate_s", w.candidate_s)
      for i in w.candidate_s:
        self.bin_l[i] += 1
        if i != self.target_i:
          if self.bin_l[i] > self.second_max_bin_height:
            self.second_max_bin_height = self.bin_l[i]
      
      self.num_attack_windows += 1
      if self.is_complete():
        break

# ****************************  Single Target Many Receivers  *************************** #
"""
gen_rate: Rate at which messages are generated at the Target
Delta: Length of the attack window
n: Number of receivers
recv_rate: Rate at which receivers receives messages
"""
class SingleTargetNReceivers():
  def __init__(self, env, _id, gen_rate, Delta, n, recv_rate, adversary):
    self.env = env
    self._id = _id
    self.gen_rate = gen_rate
    self.Delta = Delta
    self.n = n
    self.recv_rate = recv_rate
    self.adversary = adversary

    self.msg_gen = env.process(self.run_msg_gen() )
    self.wait_for_attack = env.process(self.run_msg_recv() )
    
    self.start_time = self.env.now
    self.D = None

  def __repr__(self):
    return "SingleTargetNReceivers[gen_rate= {}, Delta= {}, n= {}, recv_rate= {}]".format(self.gen_rate, self.Delta, self.n, self.recv_rate)

  def run_msg_gen(self):
    inter_gen_rv = Exp(self.gen_rate)
    counter = 0
    while 1:
      yield self.env.timeout(inter_gen_rv.sample() )
      counter += 1
      m = Msg(_id=counter, flow_id=0)
      
      slog(DEBUG, self.env, self, "generated", m)
      self.adversary.msg_generated(m.flow_id)
      
      slog(DEBUG, self.env, self, "received", m)
      self.adversary.msg_delivered(m.flow_id)
  
  def run_msg_recv(self):
    inter_recv_rv = Exp(self.recv_rate*(self.n - 1))
    counter = 0
    while 1:
      yield self.env.timeout(inter_recv_rv.sample() )
      counter += 1
      m = Msg(_id=counter, flow_id=random.randint(1, self.n-1) )
      
      slog(DEBUG, self.env, self, "received", m)
      self.adversary.msg_delivered(m.flow_id)
      
      if self.adversary.is_complete():
        slog(DEBUG, self.env, self, "is complete", self.adversary)
        self.D = self.env.now - self.start_time
        break
  
def sim_N_D_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate):
  env = simpy.Environment()
  adv = IntersectionAttack(env, n, 0, Delta, target_i=0)
  stmr = SingleTargetNReceivers(env, 'stmr', gen_rate, Delta, n, recv_rate, adv)
  env.run(until=stmr.wait_for_attack)
  return adv.num_attack_windows, stmr.D

def sim_EN_ED_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate, num_sim_runs=1000):
  N_total, D_total = 0, 0
  for _ in range(num_sim_runs):
    N, D = sim_N_D_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate)
    # log(INFO, "N= {}".format(N) )
    N_total += N
    D_total += D
  return N_total/num_sim_runs, D_total/num_sim_runs

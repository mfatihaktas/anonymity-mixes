from log_utils import *
from plot_utils import *
from sim_objs import MsgGen

import simpy, heapq, queue, collections
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
 Observe a set of candidates for the target's true recipient at each vulnerability window of target
 and keep intersecting them until the true recipient is revealed.
 
 Vulnerability window: The time interval between a message generated at the target
 and the time it reached its recipient.
 m: Min delivery time
 M: Max delivery time
"""
class VulnerabilityWindow(object):
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

    self.num_vulnerability_windows = 0
    
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
      self.window_q.appendleft(VulnerabilityWindow(t + self.m, t + self.M) )
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

      self.num_vulnerability_windows += 1
      if self.is_complete():
        break

# *************************************  Time Mix  ****************************************** #
# Each received message is held in the mix for a random amount of time T \in [d, D].
class TimeMix():
  def __init__(self, env, _id, n, T, out=None, adversary=None):
    self.env = env
    self._id = _id
    self.n = n
    self.T = T
    self.out = out
    self.adversary = adversary

    self.q = [] # min-heap w.r.t. message delivery times

    self.adversary_q = simpy.Store(env)
    self.wait_for_attack = env.process(self.run() )
    self.msg_recved_event = None

  def __repr__(self):
    return "TimeMix[_id= {}, n= {}, T= {}]".format(self._id, self.n, self.T)

  def put(self, m):
    slog(DEBUG, self.env, self, "recved", m)
    m.delivery_time = self.env.now + self.T.sample()
    
    heapq.heappush(self.q, m)

    self.adversary.msg_generated(m.flow_id)
    
    if self.msg_recved_event is not None:
      self.msg_recved_flag = True
      self.msg_recved_event.succeed()
    
  def run(self):
    while 1:
      if len(self.q) == 0:
        self.msg_recved_event = self.env.event()
        yield (self.msg_recved_event)
        self.msg_recved_event = None
        continue
      
      t = self.q[0].delivery_time - self.env.now
      self.msg_recved_event = self.env.event()
      yield (self.msg_recved_event | self.env.timeout(t))
      
      if self.msg_recved_flag:
        self.msg_recved_flag = False
        self.msg_recved_event = None
        continue
      
      m_out = heapq.heappop(self.q)
      if self.out is not None:
        self.out.put(m_out)

      if self.adversary is not None:
        self.adversary.msg_delivered(m_out.flow_id)

        if self.adversary.is_complete():
          slog(DEBUG, self.env, self, "is complete", self.adversary)
          break

def sim_N_TimeMix(n, T):
  env = simpy.Environment()
  adv = IntersectionAttack(env, n, T.m, T.M, target_i=0)
  mix = TimeMix(env, 'tm', n, T, out=None, adversary=adv)
  ar = 1
  mg = MsgGen(env, 'mg', ar*n, n, out=mix,
              generator=lambda _id, flow_id: Msg(_id, flow_id) )
  env.run(until=mix.wait_for_attack)
  return adv.num_vulnerability_windows

def sim_EN_TimeMix(n, T, num_sim_runs=1000):
  N_total = 0
  for _ in range(num_sim_runs):
    N = sim_N_TimeMix(n, T)
    # log(INFO, "N= {}".format(N) )
    N_total += N
  return N_total/num_sim_runs

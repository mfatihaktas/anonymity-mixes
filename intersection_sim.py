from log_utils import *
from plot_utils import *
from sim_objs import Msg, MsgGen, FCFS_wZeroDelayStartForBusyPeriod
from rvs import Exp, RV_wValsWeights

import simpy, heapq, queue, collections, random
import numpy as np

# *******************************  Msg  ****************************** #
class Msg_wTarget(Msg):
  def __init__(self, _id, flowId, target=False):
    super().__init__(_id, flowId)
    self.target = target

# ********************************  Msg gen  *********************************** #
class MsgGen_wTarget(object):
  def __init__(self, env, _id, genRate_l, targetPercRate, out):
    self.env = env
    self._id = _id
    self.genRate_l = genRate_l
    self.targetPercRate = targetPercRate
    self.out = out

    self.action = self.env.process(self.run() )
  
  def __repr__(self):
    return 'MsgGen_wTarget[_id={}, genRate_l= {}, targetPercRate= {}]'.format(self._id, self.genRate_l, self.targetPercRate)
  
  def run(self):
    interArrRV = Exp(sum(self.genRate_l))
    flowIdRV = RV_wValsWeights(list(range(len(self.genRate_l))), self.genRate_l)
    counter = 0
    while 1:
      yield self.env.timeout(interArrRV.sample() )
      counter += 1
      
      flowId = flowIdRV.sample()
      isTarget = False
      if (flowId == 0) and (random.random() <= self.targetPercRate):
        isTarget = True
        
      m = Msg_wTarget(counter, flowId, isTarget)
      self.out.msg_generated(m)
      yield self.env.timeout(0.000001)
      self.out.msg_delivered(m)

# *****************************  Traffic Mixer  ******************************** #
class TrafficMixer(object):
  def __init__(self, env, _id, n, V, out):
    self.env = env
    self._id = _id
    self.n = n
    
    self.q_l = [FCFS_wZeroDelayStartForBusyPeriod(i, env, V, out) for i in range(self.n) ]
  
  def __repr__(self):
    return 'TrafficMixer[_id={}, n= {}, V= {}]'.format(self._id, self.n, self.V)
  
  def put(self, m):
    slog(DEBUG, self.env, self, "recved", m)
    self.q_l[m.flowId].put(m)

# ****************************  Intersection attack  ****************************** #
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
    self.wait = None

    self.numAttackWindows = 0
    self.start_time = self.env.now
    self.D = None
  
  def __repr__(self):
    return 'IntersectionAttack[n= {}, m= {}, M= {}, target_i= {}]'.format(self.n, self.m, self.M, self.target_i)

  def start(self):
    self.wait = self.env.process(self.run() )
  
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
  
  def msg_generated(self, m):
    slog(DEBUG, self.env, self, "originated", m)
    if m.target:
      t = self.env.now
      # if len(self.window_q) == 0:
      self.window_q.appendleft(AttackWindow(t + self.m, t + self.M) )
      if self.new_window_event is not None:
        self.new_window_event.succeed()
  
  def msg_delivered(self, m):
    slog(DEBUG, self.env, self, "delivered", m)
    if self.msg_delivered_event is not None:
      self.delivered_msg_i = m.flowId
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
      
      self.numAttackWindows += 1
      if self.is_complete():
        self.D = self.env.now - self.start_time
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
  
  def __repr__(self):
    return "SingleTargetNReceivers[gen_rate= {}, Delta= {}, n= {}, recv_rate= {}]".format(self.gen_rate, self.Delta, self.n, self.recv_rate)
  
  def msg_generated(self, m):
    slog(DEBUG, self.env, self, "generated", m)
    self.adversary.msg_generated(m)
  
  def msg_delivered(self, m):
    slog(DEBUG, self.env, self, "delivered", m)
    self.adversary.msg_delivered(m)

def sim_N_D_SingleTargetNReceivers(targetRate, Delta, n, recvRate, V=None):
  env = simpy.Environment()
  adv = IntersectionAttack(env, n, 0, Delta, target_i=0)
  stmr = SingleTargetNReceivers(env, 'stmr', targetRate, Delta, n, recvRate, adv)
  msgGenOut = stmr
  if V is not None:
    tm = TrafficMixer(env, 'tm', n, V, out=stmr)
    msgGenOut = tm
  mg = MsgGen_wTarget(env, 'mg', [recvRate]*n, targetPercRate=targetRate/recvRate, out=msgGenOut)
  adv.start()
  env.run(until=adv.wait)
  return adv.numAttackWindows, adv.D

def sim_EN_ED_SingleTargetNReceivers(targetRate, Delta, n, recvRate, V=None, num_sim_runs=1000):
  N_total, D_total = 0, 0
  for _ in range(num_sim_runs):
    N, D = sim_N_D_SingleTargetNReceivers(targetRate, Delta, n, recvRate, V)
    # log(INFO, "N= {}".format(N) )
    N_total += N
    D_total += D
  return N_total/num_sim_runs, D_total/num_sim_runs

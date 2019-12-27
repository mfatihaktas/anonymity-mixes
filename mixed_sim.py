from sim import *
from patch import *
from rvs import *
from mixed_models import *

class Attacker(object):
  def __init__(self, env, n, k):
    self.env = env
    self.n = n
    self.k = k

class AttackOne(Attacker):
  def __init__(self, env, n, k):
    Attacker.__init__(self, env, n, k)
    
    self.num_inpack_sofar = 0
    self.possibleo_l = [o for o in range(n) ]
  
  def reset(self):
    self.num_inpack_sofar = 0
    self.possibleo_l = [o for o in range(self.n) ]
  
  def in_packet(self, i):
    if i == 0:
      self.num_inpack_sofar += 1
  
  def out_frame(self, o_l):
    if self.num_inpack_sofar == 0:
      return
    
    for o in self.possibleo_l:
      if o not in o_l:
        self.possibleo_l.remove(o)

class StateSniffer(Attacker):
  def __init__(self, env, n, k):
    Attacker.__init__(self, env, n, k)
    self.i_ql_map = [0]*self.n
  
  def state(self):
    return ','.join(map(str, self.i_ql_map) )
  
  def reset(self):
    self.i_ql_map = [0]*self.n
  
  def in_packet(self, i):
    self.i_ql_map[i] += 1
  
  def out_frame(self, o_l):
    for o in o_l:
      _l = self.i_ql_map[o]
      self.i_ql_map[o] = max(_l-1, 0)

'''
class Deanonymizer(object):
  def __init__(self, env, n, k):
    self.env = env
    self.n = n
    self.k = k
    
    self.deanont_l = []
    
    self.attack_on = False
    self.empty = None
    self.success = None
    env.process(self.run() )
    
    self.deanon_startt = None
    self.i__o_l_m = {i:None for i in range(self.n) }
    self.in_frame = []
  
  def run(self):
    while True:
      yield self.env.timeout(5000)
      
      self.attack_on = True
      self.deanon_startt = self.env.now
      for i in self.i__o_l_m:
        self.i__o_l_m[i] = [j for j in range(self.n) ]
      
      self.empty = self.env.event()
      yield (self.empty)
      
      self.success = self.env.event()
      yield (self.success)
  
  def in_packet(self, i):
    if self.attack_on:
      self.in_frame.append(i)
  
  def out_frame(self, o_l):
    if not self.attack_on:
      return
    
    if len(self.in_frame) < self.k: # not empty yet
      self.in_frame.clear()
      return
    elif self.empty is not None and len(self.in_frame) == self.k: # now empty
      self.empty.succeed()
      self.empty = None
    # else:
      for i in self.in_frame:
        for o in self.i__o_l_m[i]:
          if o not in o_l:
            self.i__o_l_m[i].remove(o)
      self.in_frame.clear()
      
      for i, o_l in self.i__o_l_m.items():
        if len(o_l) > 1:
          return
      self.deanont_l.append(self.env.now - self.deanon_startt)
      self.attack_on = False
      self.success.succeed()
'''

class MNMonitor(object):
  def __init__(self, env, mn, poll_interval):
    self.env = env
    self.mn = mn
    self.poll_interval = poll_interval
    
    self.qid__scounter_map_map = {}
    for i in range(self.mn.n):
      self.qid__scounter_map_map[i] = {}
    env.process(self.run() )
  
  def __repr__(self):
    return "Monitor:{}".format(self.mn)
  
  def ss_prob_map(self):
    # Assuming each q is identical
    scounter_map = {}
    for i in range(self.mn.n):
      for s, c in self.qid__scounter_map_map[i].items():
        if s not in scounter_map:
          scounter_map[s] = 0
        scounter_map[s] += c
    
    sum_c = sum([c for s,c in scounter_map.items() ] )
    return {s:c/sum_c for s,c in scounter_map.items() }
  
  def EL_EL2(self):
    # Assuming each q is identical
    scounter_map = {}
    for i in range(self.mn.n):
      for s, c in self.qid__scounter_map_map[i].items():
        if s not in scounter_map:
          scounter_map[s] = 0
        scounter_map[s] += c
    
    sum_c, sum_s, sum_s2 = 0, 0, 0
    for s, c in scounter_map.items():
      sum_c += c
      sum_s += c*s
      sum_s2 += c*s**2
    return sum_s/sum_c, sum_s2/sum_c
  
  def run(self):
    while True:
      yield self.env.timeout(self.poll_interval)
      
      for i in range(self.mn.n):
        scounter_map = self.qid__scounter_map_map[i]
        s = self.mn.id_q_map[i].length()
        # print("polled s= {}".format(s) )
        if s not in scounter_map:
          scounter_map[s] = 0
        scounter_map[s] += 1
  
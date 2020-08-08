import numpy as np

from sim_objs import *

# *************************************  AdjustableMix  ****************************************** #
"""
n servers with independent arrivals, batch departures of k-messages.
R: # of candidates that are dropped after a single batch departure
Mix waits until the current R can be realized. After that the batch is immediately released.
"""
class RMix(Mix):
  def __init__(self, env, _id, n, k, r_weight_l):
    super().__init__(env, _id, n, k)
    self.r_weight_l = r_weight_l

    self.attacker = IntersectionAttack(n, k)
    self.candidate_l = None
    self.next_r = None

  def __repr__(self):
    return 'RMix[n={}, k={}]'.format(self.n, self.k)

  def sample_r(self):
    max_r = len(self.candidate_l) - 1
    r = RV_wValsWeights(v_l=list(range(max_r + 1)), w_l= self.r_weight_l[:max_r + 1])
    return r.sample()

  def put(self, p):
    slog(DEBUG, self.env, self, "recved", p)
    self.i_q_l[p.flow_id].put(p)

    if self.candidate_l is None:
      i_l = []
      for i, q in enumerate(self.i_q_l):
        if q.length():
          i_l.append(i)

      if len(i_l) >= self.k:
        for i in i_l:
          self.i_q_l[i].release()

      self.attacker.batch(i_l)
      self.candidate_l = self.attacker.get_candidate_l()
    else:

    candidate_l = self.attacker.get_candidate_l()


    self.attacker.batch(i_l)

    if any(q.length() == 0 for q in self.i_q_l):
      slog(DEBUG, self.env, self, "There is an empty q, won't release any. Received:", p)
      return

    i_l = np.random.choice(self.n, self.k, replace=False)
    slog(DEBUG, self.env, self, "will release q's:", i_l)
    for i in i_l:
      self.i_q_l[i].release()

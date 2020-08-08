from log_utils import *
from math_utils import *

# ##############################  Random  ############################### #
"""
Intersection attack:
  The target is observed together with k - 1 others at each time step.
  For tractability, k - 1 others are sampled independently and uniformly at random.
  Adversary intersects all observed k-sets until the intersection contains the target.
  Or, thinks of the participants as n bins and places a ball in each bin within the observed k-set.
  Target is revealed as soon as the height of a bin is greater than all the other bins.

  k := Size of observed sets
  n := Total number of participants
  N := Number of intersection steps to de-anonymize the target
"""

"""
For a given n
  E[N_k] = 1 + \sum_{r = 0}^{min(n-k, k-1)} Pr{R = r} * E[N_{k-r}]
where N_1 = 0 and R is the number of candidates that are learned not to be the target
after observing one batch.

We also have
  Pr{R = r} = C(k, k-r) * C(n-k, r) / C(n, k)
Note that R >= 1.
"""

def Pr_R_eq_r_given_R_leq_k_minus_1(n, k, k_, r):
  if r < 0 or r > k_-1:
    return 0
  
  # k_: current number of candidates for the target
  '''
  def Pr_R_eq_r(k_, r):
    return C(k_, k_-r) * C(n-k_, k-k_+r) / C(n, k)
  
  # print("Pr_R_eq_r(k_= {}, r= {})= {}".format(k_, r, Pr_R_eq_r(k_, r) ) )
  # print("n= {}, k= {}".format(n, k) )
  return Pr_R_eq_r(k_, r) / (1 - Pr_R_eq_r(k_, k_) )
  '''
  return C(k_-1, k_-r-1) * C(n-k_, k-k_+r) / C(n-1, k-1)

def perfect_Pr_R_eq_r_given_R_leq_k_minus_1(n, k, k_, r):
  if k_ != 2:
    log(ERROR, "implemented only for k_ = 2.")
    return
  
  if r == 0:
    return C(n-2, k-2)/C(n-1, k-1)
  elif r == 1:
    return C(n-2, k-1)/C(n-1, k-1)
  else:
    return 0

def E_N(n, k):
  m = {}
  def E(k_):
    # sum_Pr_R_eq_r_given_R_leq_k_minus_1 = sum(Pr_R_eq_r_given_R_leq_k_minus_1(k_, r) for r in range(k_) )
    # log(INFO, "k_= {}, sum_Pr_R_eq_r_given_R_leq_k_minus_1= {}".format(k_, sum_Pr_R_eq_r_given_R_leq_k_minus_1) )
    if k_ == 1:
      return 0
    
    if k_ in m:
      return m[k_]
    
    # print(">> k_= {}".format(k_) )
    # for r in range(k_):
    #   p = Pr_R_eq_r_given_R_leq_k_minus_1(k_, r)
    #   print("r= {}, p= {}".format(r, p) )
    
    result = (1 + sum(Pr_R_eq_r_given_R_leq_k_minus_1(n, k, k_, r) * E(k_-r) for r in range(1, k_) ) ) \
              / (1 - Pr_R_eq_r_given_R_leq_k_minus_1(n, k, k_, 0) )
    m[k_] = result
    return result
  return 1 + E(k)

if __name__ == "__main__":
  n = 10
  # for k in range(2, n):
  #   EN = E_N(n, k)
  #   print("k= {}, n= {}, EN= {}".format(k, n, EN) )
  
  k, k_ = 5, 2
  print(">> n= {}, k= {}, k_= {}".format(n, k, k_) )
  for r in [0, 1]:
    p = Pr_R_eq_r_given_R_leq_k_minus_1(n, k, k_, r)
    perfect_p = perfect_Pr_R_eq_r_given_R_leq_k_minus_1(n, k, k_, r)
    print("r= {}, p= {}, perfect_p= {}".format(r, p, perfect_p) )
  

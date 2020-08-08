from log_utils import *
from plot_utils import *
from batchmix_sim_objs import *

import random
import simpy

# ##############################  Random  ############################### #
def sim_N_random(n, k):
  if k == n:
    log(ERROR, "Intersection attack will never deanonymize; k = n = {}".format(k))
    return

  target_bin = 0
  bin_l = [0 for _ in range(n-1)]

  second_max_bin_height = 0 # target_bin will always have the max height
  def update_second_max(m):
    nonlocal second_max_bin_height
    if m > second_max_bin_height:
      second_max_bin_height = m

  range_l = list(range(n-1))
  step = 0
  while target_bin == second_max_bin_height:
    target_bin += 1
    for o in random.sample(range_l, k-1):
      bin_l[o] += 1
      update_second_max(bin_l[o])
    step += 1
    # print("target_bin= {}, second_max_bin_height= {}".format(target_bin, second_max_bin_height) )
  return step

# #############################  Batch mix  ############################# #
def sim_N_BatchMix(n, k):
  if k == n:
    log(ERROR, "Intersection attack will never deanonymize; k = n = {}".format(k))
    return

  env = simpy.Environment()
  adv = IntersectionAttack(n, k)
  mix = BatchMix(env, 'bm', n, k, adv)
  ar = 1
  mg = MsgGen(env, 'mg', ar, n, out=mix)
  env.run(until=mix.wait_for_attack)
  return mix.num_batch_departures_wtarget

def sim_EN(n, k, mix_type, num_sim_runs=1000):
  N_total = 0
  for _ in range(num_sim_runs):
    if mix_type == 'random':
      N = sim_N_random(n, k)
    elif mix_type == 'batch':
      N = sim_N_BatchMix(n, k)
    else:
      log(ERROR, "Unrecognized mix_type= {}".format(mix_type))
      return
    # log(INFO, "N= {}".format(N) )
    N_total += N
  return N_total/num_sim_runs

if __name__ == "__main__":
  # plot_batchmix_EQt_vs_k()
  n, k = 100, 10
  EN = sim_EN(n, k, mix_type='random')
  print("EN= {}".format(EN))

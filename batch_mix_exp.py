import simpy
import numpy as np

from plot_utils import *
from batch_mix_sim_objs import *

def sim(n, k, ar):
  log(INFO, "started;", n=n, k=k, ar=ar)
  
  env = simpy.Environment()
  bm = BatchMix(env, 'bm', n, k)
  mg = MsgGen(env, 'mg', ar, n, out=bm)
  env.run(until=50000*1)
  ET, ET2 = bm.ET_ET2()
  return ET, ET2

def plot_EQt_vs_k():
  n = 100
  
  def plot_(ar):
    k_l, ET_l = [], []
    for _k in np.linspace(1, n, 10):
      k = int(_k)
      k_l.append(k)
      ET, ET2 = sim(n, k, ar)
      ET_l.append(ET)
    plot.plot(k_l, ET_l, label=r'$\lambda= {}$'.format(ar), color=next(darkcolor_c), marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
  
  plot_(ar=1)
  
  plot.legend()
  plot.xlabel(r'$\lambda$', fontsize=14)
  plot.ylabel(r'$E[T]$', fontsize=14)
  plot.title(r'Batch mix, $n= {}$'.format(n) )
  fig = plot.gcf()
  fig.set_size_inches(6, 5)
  fig.tight_layout()
  plot.savefig("plot_EQt_vs_k_n_{}.pdf".format(n) )
  log(WARNING, "done; n= {}".format(n) )

if __name__ == "__main__":
  plot_EQt_vs_k()

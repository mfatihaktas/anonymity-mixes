import simpy
import numpy as np

from plot_utils import *
from batchmix_sim_objs import *
from randmix_sim_objs import *

def sim(n, k, ar, t='bm'):
  log(INFO, "started;", n=n, k=k, ar=ar, t=t)
  
  env = simpy.Environment()
  if t == 'bm':
    mix = BatchMix(env, 'bm', n, k)
  elif t == 'tsm':
    mix = True_SamplekMix(env, 'tsm', n, k)
  mg = MsgGen(env, 'mg', ar, n, out=mix)
  env.run(until=50000*1)
  ET, ET2 = mix.ET_ET2()
  return ET, ET2

def plot_batchmix_EQt_vs_k():
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
  plot.savefig("plot_batchmix_EQt_vs_k_n_{}.pdf".format(n) )
  log(WARNING, "done; n= {}".format(n) )

def plot_batch_vs_samplek_mix():
  n = 100
  
  def plot_EQt_vs_k(ar):
    k_l, ET_bm_l, ET_tsm_l = [], [], []
    for _k in np.linspace(1, n, 10):
      k = int(_k)
      k_l.append(k)
      print(">> k= {}".format(k) )
      
      ET_bm, ET2_bm = sim(n, k, ar, t='bm')
      ET_bm_l.append(ET_bm)
      
      ET_tsm, ET2_tsm = sim(n, k, ar, t='tsm')
      ET_tsm_l.append(ET_tsm)
      
      print("ET_bm= {}, ET_tsm= {}".format(ET_bm, ET_tsm) )
    plot.plot(k_l, ET_bm_l, label=r'Batch-mix, $\lambda= {}$'.format(ar), color=next(darkcolor_c), marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    plot.plot(k_l, ET_tsm_l, label=r'True-Samplek-mix, $\lambda= {}$'.format(ar), color=next(darkcolor_c), marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
  
  plot_EQt_vs_k(ar=1)
  
  plot.legend()
  plot.xlabel(r'$\lambda$', fontsize=14)
  plot.ylabel(r'$E[T]$', fontsize=14)
  plot.title(r'Batch mix, $n= {}$'.format(n) )
  fig = plot.gcf()
  fig.set_size_inches(6, 5)
  fig.tight_layout()
  plot.savefig("plot_batch_vs_samplek_mix.pdf")
  log(WARNING, "done; n= {}".format(n) )

if __name__ == "__main__":
  # plot_batchmix_EQt_vs_k()
  plot_batch_vs_samplek_mix()

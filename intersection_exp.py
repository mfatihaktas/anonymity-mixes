from log_utils import *
from plot_utils import *
from sim_objs import *
from intersection_sim import *
from intersection_model import *

def plot_EN_vs_Delta_SingleTargetNReceivers():
  gen_rate, recv_rate = 1, 1
  def plot_(n):
    log(INFO, ">> n= {}".format(n) )
    Delta_l = []
    EN_sim_l, EN_l = [], []
    # for Delta in np.linspace(1, 10, 10):
    for Delta in np.linspace(1, 3, 4):
      print("\n**n= {}, Delta= {}".format(n, Delta) )
      Delta_l.append(Delta)

      EN_sim, _ = sim_EN_ED_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate, num_sim_runs=1000)
      print("EN_sim= {}".format(EN_sim))
      EN_sim_l.append(EN_sim)

      EN_ = EN(gen_rate, Delta, n, recv_rate)
      print("EN= {}".format(EN_))
      EN_l.append(EN_)

    c = next(darkcolor_c)
    # plot.plot(Delta_l, EN_sim_l, label=r'Sim, $n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    plot.plot(Delta_l, EN_l, label=r'$n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='--')
    plot.yscale('log')

  plot_(n=10)
  # for n in range(10, 50, 10):
  # for n in [10, 100, 1000, 10000]:
  #   plot_(n)
  
  plot.legend()
  plot.xlabel(r'$\Delta$', fontsize=14)
  plot.ylabel(r'$E[N]$', fontsize=14)
  plot.title('Single target, n receivers')
  plot.gcf().set_size_inches(6, 5)
  plot.savefig("plot_EN_vs_Delta_SingleTargetNReceivers.pdf", bbox_inches='tight')
  log(WARNING, "done.")

def plot_ED_vs_Delta_SingleTargetNReceivers():
  gen_rate, recv_rate = 1, 1
  def plot_(n):
    log(INFO, ">> n= {}".format(n) )
    Delta_l = []
    ED_sim_l, ED_l, ED_UB_l = [], [], []
    ED_sim_wMixerWFCFS_l = []
    ED_wMixerWMaxDelay_l, ED_sim_wMixerWMaxDelay_l = [], []
    for Delta in np.linspace(0.5, 5, 10):
      print("\n** Delta= {}".format(Delta) )
      Delta_l.append(Delta)

      # _, ED_sim = sim_EN_ED_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate, num_sim_runs=1000)
      # print("ED_sim= {}".format(ED_sim))
      # ED_sim_l.append(ED_sim)

      ED_ = ED(gen_rate, Delta, n, recv_rate)
      print("ED= {}".format(ED_) )
      ED_l.append(ED_)

      # ED_UB_ = ED_UB(gen_rate, Delta, n, recv_rate)
      # print("ED_UB= {}".format(ED_UB_) )
      # ED_UB_l.append(ED_UB_)
      
      # _, ED_sim_wMixerWFCFS = \
      #   sim_EN_ED_SingleTargetNReceivers(
      #     gen_rate, Delta, n, recv_rate,
      #     trafficMixer_m={'type': 'wFCFS_wZeroDelayStartForBusyPeriod', 'V': Constant(0.95)}, num_sim_runs=1000)
      # print("ED_sim_wMixerWFCFS= {}".format(ED_sim_wMixerWFCFS) )
      # ED_sim_wMixerWFCFS_l.append(ED_sim_wMixerWFCFS)

      maxDelay = 0.5 # Delta/2
      ED_wMixerWMaxDelay_ = ED_wMixerWMaxDelay(gen_rate, Delta, n, recv_rate, maxDelay)
      print("ED_wMixerWMaxDelay= {}".format(ED_wMixerWMaxDelay_) )
      ED_wMixerWMaxDelay_l.append(ED_wMixerWMaxDelay_)
      
      # _, ED_sim_wMixerWMaxDelay = \
      #   sim_EN_ED_SingleTargetNReceivers(
      #     gen_rate, Delta, n, recv_rate,
      #     trafficMixer_m={'type': 'wMaxDelay', 'maxDelay': maxDelay}, num_sim_runs=1000)
      # print("ED_sim_wMixerWMaxDelay= {}".format(ED_sim_wMixerWMaxDelay) )
      # ED_sim_wMixerWMaxDelay_l.append(ED_sim_wMixerWMaxDelay)
    
    c = next(darkcolor_c)
    # plot.plot(Delta_l, ED_sim_l, label=r'Sim, $n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    plot.plot(Delta_l, ED_l, label=r'$n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle=':')
    # plot.plot(Delta_l, ED_UB_l, label=r'Upper-Bound, $n= {}$'.format(n), color=c, marker='^', mew=mew, ms=ms, linestyle='--')
    # plot.plot(Delta_l, ED_sim_wMixerWFCFS_l, label=r'Sim-wMixerWFCFS, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    # c = next(darkcolor_c)
    # plot.plot(Delta_l, ED_sim_wMixerWMaxDelay_l, label=r'Sim-wMixerWMaxDelay, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    plot.plot(Delta_l, ED_wMixerWMaxDelay_l, label=r'wMixerWMaxDelay, $n= {}$'.format(n), color=c, marker='x', mew=mew, ms=ms, linestyle='-')
    plot.yscale('log')

  # for n in range(10, 40, 10):
  # plot_(n=10)
  for n in [10, 100, 1000, 10000]:
    plot_(n)
  
  plot.legend()
  plot.xlabel(r'$\Delta$', fontsize=14)
  plot.ylabel(r'$E[D]$', fontsize=14)
  plot.title('Single target, n receivers')
  plot.gcf().set_size_inches(6, 5)
  plot.savefig("plot_ED_vs_Delta_SingleTargetNReceivers.pdf", bbox_inches='tight')
  log(WARNING, "done.")

if __name__ == "__main__":
  # plot_EN_vs_Delta_SingleTargetNReceivers()
  plot_ED_vs_Delta_SingleTargetNReceivers()
  
  # n = 10
  # T = TPareto(0.1, 5, 2)
  # EN_sim = sim_EN_TimeMix(n, T, num_sim_runs=1)
  # print("EN_sim= {}".format(EN_sim))


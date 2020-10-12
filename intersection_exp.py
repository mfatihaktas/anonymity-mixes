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
    EN_sim_l, EN_lb_l, EN_ub_l = [], [], []
    EN_wMixerWMaxDelay_sim_l, EN_wMixerWMaxDelay_lb_l, EN_wMixerWMaxDelay_ub_l = [], [], []
    for Delta in np.linspace(1, 10, 10):
    # for Delta in np.linspace(1, 5, 4):
      print("\n**n= {}, Delta= {}".format(n, Delta) )
      Delta_l.append(Delta)

      # EN_sim, _ = sim_EN_ED_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate, num_sim_runs=10)
      # print("EN_sim= {}".format(EN_sim))
      # EN_sim_l.append(EN_sim)

      EN_lb = EN(gen_rate, Delta, n, recv_rate)
      print("EN_lb= {}".format(EN_lb))
      EN_lb_l.append(EN_lb)

      EN_ub = EN(gen_rate, Delta, n, recv_rate, upperBound=True)
      print("EN_ub= {}".format(EN_ub))
      EN_ub_l.append(EN_ub)

      maxDelay = Delta/2
      # _, ED_sim_wMixerWMaxDelay = \
      #   sim_EN_ED_SingleTargetNReceivers(
      #     gen_rate, Delta, n, recv_rate,
      #     trafficMixer_m={'type': 'wMaxDelay', 'maxDelay': maxDelay}, num_sim_runs=1000)
      # print("ED_sim_wMixerWMaxDelay= {}".format(ED_sim_wMixerWMaxDelay) )
      # ED_sim_wMixerWMaxDelay_l.append(ED_sim_wMixerWMaxDelay)

      EN_wMixerWMaxDelay_lb = EN_wMixerWMaxDelay(gen_rate, Delta, n, recv_rate, maxDelay)
      print("EN_wMixerWMaxDelay_lb= {}".format(EN_wMixerWMaxDelay_lb) )
      EN_wMixerWMaxDelay_lb_l.append(EN_wMixerWMaxDelay_lb)

      EN_wMixerWMaxDelay_ub = EN_wMixerWMaxDelay(gen_rate, Delta, n, recv_rate, maxDelay, upperBound=True)
      print("EN_wMixerWMaxDelay_ub= {}".format(EN_wMixerWMaxDelay_ub) )
      EN_wMixerWMaxDelay_ub_l.append(EN_wMixerWMaxDelay_ub)

    c = next(darkcolor_c)
    # plot.plot(Delta_l, EN_sim_l, label=r'Sim, $n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    # plot.plot(Delta_l, EN_lb_l, label=r'Lower bound, $n= {}$'.format(n), color=c, marker='v', mew=mew, ms=ms, linestyle='--')
    # plot.plot(Delta_l, EN_ub_l, label=r'Upper bound, $n= {}$'.format(n), color=c, marker='^', mew=mew, ms=ms, linestyle='--')
    plot.plot(Delta_l, EN_wMixerWMaxDelay_lb_l, label=r'Lower bound, $n= {}$'.format(n), color=c, marker='v', mew=mew, ms=ms, linestyle='--')
    plot.plot(Delta_l, EN_wMixerWMaxDelay_ub_l, label=r'Upper bound, $n= {}$'.format(n), color=c, marker='^', mew=mew, ms=ms, linestyle='--')
    
    plot.yscale('log')

  # plot_(n=10)
  # for n in range(10, 50, 10):
  for n in [10, 100, 1000, 10000]:
    plot_(n)
  
  plot.legend(fontsize=8)
  plot.xlabel(r'$\Delta$', fontsize=14)
  plot.ylabel(r'$E[N]$ with ideal mix', fontsize=14)
  # plot.title('Single target, n recipient candidates')
  # plot.title(r'$\lambda = {}$, $\mu = {}$'.format(gen_rate, recv_rate))
  plot.title(r'$\lambda = {}$, $\mu = {}$, $\delta = \Delta/2$'.format(gen_rate, recv_rate))
  plot.gcf().set_size_inches(6, 5)
  plot.savefig("plot_EN_vs_Delta_SingleTargetNReceivers.pdf", bbox_inches='tight')
  log(WARNING, "done.")

def plot_ED_vs_Delta_SingleTargetNReceivers():
  gen_rate, recv_rate = 1, 1
  def plot_(n):
    log(INFO, ">> n= {}".format(n) )
    Delta_l = []
    ED_sim_l, ED_lb_l, ED_ub_l = [], [], []
    ED_sim_wMixerWFCFS_l = []
    ED_sim_wMixerWMaxDelay_l, ED_wMixerWMaxDelay_lb_l, ED_wMixerWMaxDelay_ub_l = [], [], []
    for Delta in np.linspace(0.5, 5, 10):
      print("\n** Delta= {}".format(Delta) )
      Delta_l.append(Delta)
      
      # _, ED_sim = sim_EN_ED_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate, num_sim_runs=1000)
      # print("ED_sim= {}".format(ED_sim))
      # ED_sim_l.append(ED_sim)

      # ED_lb = ED(gen_rate, Delta, n, recv_rate)
      # print("ED_lb= {}".format(ED_lb))
      # ED_lb_l.append(ED_lb)

      # ED_ub = ED(gen_rate, Delta, n, recv_rate, upperBound=True)
      # print("ED_ub= {}".format(ED_ub))
      # ED_ub_l.append(ED_ub)
      
      # _, ED_sim_wMixerWFCFS = \
      #   sim_EN_ED_SingleTargetNReceivers(
      #     gen_rate, Delta, n, recv_rate,
      #     trafficMixer_m={'type': 'wFCFS_wZeroDelayStartForBusyPeriod', 'V': Constant(0.95)}, num_sim_runs=1000)
      # print("ED_sim_wMixerWFCFS= {}".format(ED_sim_wMixerWFCFS) )
      # ED_sim_wMixerWFCFS_l.append(ED_sim_wMixerWFCFS)

      maxDelay = Delta/2
      # _, ED_sim_wMixerWMaxDelay = \
      #   sim_EN_ED_SingleTargetNReceivers(
      #     gen_rate, Delta, n, recv_rate,
      #     trafficMixer_m={'type': 'wMaxDelay', 'maxDelay': maxDelay}, num_sim_runs=1000)
      # print("ED_sim_wMixerWMaxDelay= {}".format(ED_sim_wMixerWMaxDelay) )
      # ED_sim_wMixerWMaxDelay_l.append(ED_sim_wMixerWMaxDelay)

      ED_wMixerWMaxDelay_lb = ED_wMixerWMaxDelay(gen_rate, Delta, n, recv_rate, maxDelay)
      print("ED_wMixerWMaxDelay_lb= {}".format(ED_wMixerWMaxDelay_lb) )
      ED_wMixerWMaxDelay_lb_l.append(ED_wMixerWMaxDelay_lb)

      ED_wMixerWMaxDelay_ub = ED_wMixerWMaxDelay(gen_rate, Delta, n, recv_rate, maxDelay, upperBound=True)
      print("ED_wMixerWMaxDelay_ub= {}".format(ED_wMixerWMaxDelay_ub) )
      ED_wMixerWMaxDelay_ub_l.append(ED_wMixerWMaxDelay_ub)
    
    c = next(darkcolor_c)
    # plot.plot(Delta_l, ED_sim_l, label=r'Sim, $n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    # plot.plot(Delta_l, ED_lb_l, label=r'Lower bound, $n= {}$'.format(n), color=c, marker='v', mew=mew, ms=ms, linestyle='--')
    # plot.plot(Delta_l, ED_ub_l, label=r'Upper bound, $n= {}$'.format(n), color=c, marker='^', mew=mew, ms=ms, linestyle='--')
    # plot.plot(Delta_l, ED_sim_wMixerWFCFS_l, label=r'Sim-wMixerWFCFS, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    # c = next(darkcolor_c)
    # plot.plot(Delta_l, ED_sim_wMixerWMaxDelay_l, label=r'Sim-wMixerWMaxDelay, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    plot.plot(Delta_l, ED_wMixerWMaxDelay_lb_l, label=r'Lower bound, $n= {}$'.format(n), color=c, marker='v', mew=mew, ms=ms, linestyle='--')
    plot.plot(Delta_l, ED_wMixerWMaxDelay_ub_l, label=r'Upper bound, $n= {}$'.format(n), color=c, marker='^', mew=mew, ms=ms, linestyle='--')
    plot.yscale('log')

  # for n in range(10, 40, 10):
  # plot_(n=10)
  for n in [10, 100, 1000, 10000]:
    plot_(n)
  
  plot.legend(fontsize=8)
  plot.xlabel(r'$\Delta$', fontsize=14)
  plot.ylabel(r'$E[D]$ with ideal mix', fontsize=14)
  # plot.title(r'Single target, n receivers, $\delta = \Delta/2$')
  plot.title(r'$\lambda = {}$, $\mu = {}$, $\delta = \Delta/2$'.format(gen_rate, recv_rate))
  
  plot.gcf().set_size_inches(6, 5)
  plot.savefig("plot_ED_vs_Delta_SingleTargetNReceivers.pdf", bbox_inches='tight')
  log(WARNING, "done.")

if __name__ == "__main__":
  plot_EN_vs_Delta_SingleTargetNReceivers()
  # plot_ED_vs_Delta_SingleTargetNReceivers()
  
  # n = 10
  # T = TPareto(0.1, 5, 2)
  # EN_sim = sim_EN_TimeMix(n, T, num_sim_runs=1)
  # print("EN_sim= {}".format(EN_sim))


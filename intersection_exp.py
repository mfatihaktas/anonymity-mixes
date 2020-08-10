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
    for Delta in np.linspace(1, 3, 5):
      print("\n** Delta= {}".format(Delta) )
      Delta_l.append(Delta)

      EN_sim, _ = sim_EN_ED_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate, num_sim_runs=1000)
      print("EN_sim= {}".format(EN_sim))
      EN_sim_l.append(EN_sim)

      # ar = 1
      # EN_IndWin = EN_IndependentWindows(n, ar, T)
      # print("EN_IndWin= {}".format(EN_IndWin))
      # EN_IndWin_l.append(EN_IndWin)

    c = next(darkcolor_c)
    plot.plot(Delta_l, EN_sim_l, label=r'Sim, $n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    # plot.plot(Delta_l, EN_IndWin_l, label=r'Ind-Win, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    # plot.yscale('log')

  # for n in range(10, 40, 10):
  for n in [10]:
    plot_(n)
  
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
    ED_sim_l, ED_l = [], []
    for Delta in np.linspace(1, 3, 5):
      print("\n** Delta= {}".format(Delta) )
      Delta_l.append(Delta)

      _, ED_sim = sim_EN_ED_SingleTargetNReceivers(gen_rate, Delta, n, recv_rate, num_sim_runs=1000)
      print("ED_sim= {}".format(ED_sim))
      ED_sim_l.append(ED_sim)

      # ED_IndWin = ED_IndependentWindows(n, ar, T)
      # print("ED_IndWin= {}".format(ED_IndWin))
      # ED_IndWin_l.append(ED_IndWin)
    c = next(darkcolor_c)
    plot.plot(Delta_l, ED_sim_l, label=r'Sim, $n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    # plot.plot(Delta_l, ED_IndWin_l, label=r'Ind-Win, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    # plot.yscale('log')

  # for n in range(10, 40, 10):
  for n in [10]:
    plot_(n)
  
  plot.legend()
  plot.xlabel(r'$\Delta$', fontsize=14)
  plot.ylabel(r'$E[D]$', fontsize=14)
  plot.title('Single target, n receivers')
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


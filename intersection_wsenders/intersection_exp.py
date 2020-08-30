from log_utils import *
from plot_utils import *
from sim_objs import *
from intersection_sim import *
from intersection_model import *

def plot_EN_vs_Delta_in_TimeMix():
  def plot_(n):
    log(INFO, ">> n= {}".format(n) )
    Delta_l = []
    EN_sim_l, EN_IndWin_l = [], []
    for Delta in np.linspace(1, 3, 5):
      print("\n** Delta= {}".format(Delta) )
      Delta_l.append(Delta)

      T = TPareto(0.0001, Delta, 1)
      EN_sim, _ = sim_EN_ED_TimeMix(n, T, num_sim_runs=1000)
      print("EN_sim= {}".format(EN_sim))
      EN_sim_l.append(EN_sim)

      ar = 1
      EN_IndWin = EN_IndependentWindows(n, ar, T)
      print("EN_IndWin= {}".format(EN_IndWin))
      EN_IndWin_l.append(EN_IndWin)

    c = next(darkcolor_c)
    plot.plot(Delta_l, EN_sim_l, label=r'Sim, $n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    plot.plot(Delta_l, EN_IndWin_l, label=r'Ind-Win, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    # plot.yscale('log')

  # for n in range(10, 40, 10):
  for n in [10]:
    plot_(n)
  
  plot.legend()
  plot.xlabel(r'$\Delta$', fontsize=14)
  plot.ylabel(r'$E[N]$', fontsize=14)
  plot.title(r'Time-Mix')
  plot.gcf().set_size_inches(6, 5)
  plot.savefig("plot_EN_vs_Delta_in_TimeMix.pdf", bbox_inches='tight')
  log(WARNING, "done.")

def plot_ED_vs_Delta_in_TimeMix():
  def plot_(n):
    log(INFO, ">> n= {}".format(n) )
    Delta_l = []
    ED_sim_l, ED_IndWin_l, ED_lb_l = [], [], []
    for Delta in np.linspace(1, 3, 5):
      print("\n** Delta= {}".format(Delta) )
      Delta_l.append(Delta)

      T = TPareto(0.0001, Delta, 1)
      _, ED_sim = sim_EN_ED_TimeMix(n, T, num_sim_runs=1000)
      print("ED_sim= {}".format(ED_sim))
      ED_sim_l.append(ED_sim)

      ar = 1
      ED_IndWin = ED_IndependentWindows(n, ar, T)
      print("ED_IndWin= {}".format(ED_IndWin))
      ED_IndWin_l.append(ED_IndWin)
      
      ED_lb = ED_LB(n, ar, T)
      print("ED_lb= {}".format(ED_lb))
      ED_lb_l.append(ED_lb)

    c = next(darkcolor_c)
    plot.plot(Delta_l, ED_sim_l, label=r'Sim, $n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
    plot.plot(Delta_l, ED_IndWin_l, label=r'Ind-Win, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    plot.plot(Delta_l, ED_lb_l, label=r'LB, $n= {}$'.format(n), color=c, marker='.', mew=mew, ms=ms, linestyle='-')
    # plot.yscale('log')

  # for n in range(10, 40, 10):
  for n in [10]:
    plot_(n)
  
  plot.legend()
  plot.xlabel(r'$\Delta$', fontsize=14)
  plot.ylabel(r'$E[D]$', fontsize=14)
  plot.title(r'Time-Mix')
  plot.gcf().set_size_inches(6, 5)
  plot.savefig("plot_ED_vs_Delta_in_TimeMix.pdf", bbox_inches='tight')
  log(WARNING, "done.")

if __name__ == "__main__":
  # plot_EN_vs_Delta_in_TimeMix()
  plot_ED_vs_Delta_in_TimeMix()
  
  # n = 10
  # T = TPareto(0.1, 5, 2)
  # EN_sim = sim_EN_TimeMix(n, T, num_sim_runs=1)
  # print("EN_sim= {}".format(EN_sim))


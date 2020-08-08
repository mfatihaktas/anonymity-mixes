from log_utils import *
from plot_utils import *
from sim_objs import *
from intersection_sim import *

def plot_EN_vs_Delta_in_TimeMix():
	def plot_(n):
		log(INFO, ">> n= {}".format(n) )
		Delta_l = []
		EN_sim_l = []
		for Delta in np.linspace(1, 5, 5):
			print("Delta= {}".format(Delta) )
			Delta_l.append(Delta)

			T = TPareto(0.1, Delta, 1)
			EN_sim = sim_EN_TimeMix(n, T, num_sim_runs=1000)
			print("EN_sim= {}".format(EN_sim))
			EN_sim_l.append(EN_sim)

		c = next(darkcolor_c)
		plot.plot(Delta_l, EN_sim_l, label=r'$n= {}$'.format(n), color=c, marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
		# plot.yscale('log')

	for n in range(10, 40, 10):
    plot_(n)
  
  plot.legend()
	plot.xlabel(r'$\Delta$', fontsize=14)
	plot.ylabel(r'$E[N]$', fontsize=14)
	plot.title(r'Time-Mix')
	plot.gcf().set_size_inches(6, 5)
	plot.savefig("plot_EN_vs_Delta_in_TimeMix.pdf", bbox_inches='tight')
	log(WARNING, "done.")

if __name__ == "__main__":
	plot_EN_vs_Delta_in_TimeMix()

	# n = 10
	# T = TPareto(0.1, 5, 2)
	# EN_sim = sim_EN_TimeMix(n, T, num_sim_runs=1)
	# print("EN_sim= {}".format(EN_sim))


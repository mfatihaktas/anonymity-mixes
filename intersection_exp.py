from intersection_sim import *

def plot_EN_vs_k(n):
	k_l, EN_sim_random_l, EN_sim_BatchMix_l = [], [], []

	for k in range(2, n, 2):
		print("k= {}".format(k))

		EN_sim_random = sim_EN(n, k, mix_type='random', num_sim_runs=1000)
		print("  EN_sim_random= {}".format(EN_sim_random))
		EN_sim_BatchMix = sim_EN(n, k, mix_type='batch', num_sim_runs=1000)
		print("  EN_sim_BatchMix= {}".format(EN_sim_BatchMix))

		k_l.append(k)
		EN_sim_random_l.append(EN_sim_random)
		EN_sim_BatchMix_l.append(EN_sim_BatchMix)
	plot.plot(k_l, EN_sim_random_l, label=r'Random', color=next(darkcolor_c), marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
	plot.plot(k_l, EN_sim_BatchMix_l, label=r'Batch', color=next(darkcolor_c), marker=next(marker_c), mew=mew, ms=ms, linestyle=':')
	plot.yscale('log')

	plot.legend()
	plot.xlabel(r'$k$', fontsize=14)
	plot.ylabel(r'$E[N]$', fontsize=14)
	plot.title(r'$n= {}$'.format(n) )
	plot.gcf().set_size_inches(6, 5)
	plot.savefig("plot_EN_vs_k_n={}.pdf".format(n), bbox_inches='tight')
	log(WARNING, "done; n= {}".format(n) )

if __name__ == "__main__":
	n = 50
	plot_EN_vs_k(n)

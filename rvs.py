import math, random, numpy, csv
from scipy.stats import *

from math_utils import *

class RV(): # Random Variable
  def __init__(self, m, M):
    self.m = m
    self.M = M

class Constant(RV):
  def __init__(self, c):
    RV.__init__(self, m=c, M=c)
    self.c = c

  def sample(self):
    return self.c

class Exp(RV):
  def __init__(self, mu, D=0):
    RV.__init__(self, m=D, M=float("inf") )
    self.D = D
    self.mu = mu

  def __str__(self):
    # return "Exp(D={}, mu={})".format(self.D, self.mu)
    return r'Exp(\mu={})'.format(self.mu)

  def tail(self, x):
    if x <= self.m:
      return 1
    return math.exp(-self.mu*(x - self.D) )

  def cdf(self, x):
    if x <= self.m:
      return 0
    return 1 - math.exp(-self.mu*(x - self.D) )

  def pdf(self, x):
    if x <= self.m:
      return 0
    return self.mu*math.exp(-self.mu*(x - self.D) )

  def mean(self):
    return self.D + 1/self.mu
  
  def mean_given_g_x(self, x):
    if x < self.m:
      return self.mean()
    return x + 1/self.mu

  def mean_given_leq_x(self, x):
    if x <= self.m:
      return 0
    return (self.mean() - self.mean_given_g_x(x)*self.tail(x) )/self.cdf(x)

  def var(self):
    return 1/self.mu**2

  def sample(self):
    return self.D + random.expovariate(self.mu)

class Pareto(RV):
  def __init__(self, loc, a):
    RV.__init__(self, m=loc, M=float("inf") )
    self.loc = loc
    self.a = a

  def __str__(self):
    # return "Pareto(loc= {}, a= {})".format(self.loc, self.a)
    return r'Pareto(s= {}, \alpha= {})'.format(self.loc, self.a)

  def to_latex(self):
    return r"${}(\min= {}, \alpha= {})$".format(r'\mathrm{Pareto}', round(self.loc, 2), round(self.a, 2) )

  def tail(self, x):
    if x <= self.m:
      return 1
    return (self.loc/x)**self.a

  def cdf(self, x):
    if x <= self.m:
      return 0
    return 1 - (self.loc/x)**self.a

  def pdf(self, x):
    if x <= self.m:
      return 0
    return self.a*self.loc**self.a / x**(self.a+1)

  def dpdf_dx(self, x):
    if x <= self.m:
      return 0
    return sympy.mpmath.diff(lambda y: self.a*self.loc**self.a / y**(self.a+1), x)

  def mean(self):
    if self.a <= 1:
      log(WARNING, "Mean is Infinity; a= {} <= 1".format(self.a) )
      return float("inf")
    else:
      return self.loc*self.a/(self.a-1)

  def var(self):
    if self.a <= 2:
      log(WARNING, "Variance is Infinity; a= {} <= 2".format(self.a) )
      return float("inf")
    else:
      return self.a*self.loc**2 / (self.a-1)**2/(self.a-2)

  def sample(self):
    return ((numpy.random.pareto(self.a, 1) + 1)*self.loc)[0]
    # return pareto.ppf(numpy.random.uniform(0, 1), b=self.a, scale=self.loc)

class TPareto(): # Truncated
  def __init__(self, l, u, a):
    RV.__init__(self, m=l, M=u)
    self.l = l
    self.u = u
    self.a = a

  def __str__(self):
    return "Pareto(l= {}, u= {}, a= {})".format(self.l, self.u, self.a)

  def to_latex(self):
        return r"${}(\min= {}, \max= {}, \alpha= {})$".format(r'\mathrm{TPareto}', round(self.l, 2), round(self.u, 2), round(self.a, 2) )

  def cdf(self, x):
    if x < self.l: return 0
    elif x >= self.u: return 1
    else:
      return (1 - (self.l/x)**self.a)/(1 - (self.l/self.u)**self.a)

  def tail(self, x):
    return 1 - self.cdf(x)

  def mean(self):
    return self.moment(1)

  def moment(self, k):
    if k == self.a:
      return math.log(self.M/self.l)
    else:
      return self.a*self.l**k/(self.a-k) * \
             (1 - (self.l/self.u)**(self.a-k))/(1 - (self.l/self.u)**self.a)

  def sample(self):
    u = random.uniform(0, 1)
    return self.l*(1 - u*(1-(self.l/self.u)**self.a) )**(-1/self.a)

def plot_gensample_check():
  l, u, a = 1, 10**5, 2
  rv = TPareto(l, u, a)

  x_l = []
  for i in range(10**5):
          x_l.append(rv.sample() )
  x_l = numpy.sort(x_l)
  x_l = x_l[::-1]
  # i_ = None
  # for i in range(len(x_l)-1, 0, -1):
  #   if x_l[i] > 1.01: i_ = i; break
  # x_l = x_l[:i_]
  y_l = numpy.arange(x_l.size)/x_l.size
  plot.plot(x_l, y_l, marker=next(marker), color=next(dark_color), linestyle=':', mew=mew, ms=ms)

  y_l = []
  for x in x_l:
          y_l.append(rv.tail(x) )
  plot.plot(x_l, y_l, label=r'$Pareto(l= %.2f, u= %.2f, \alpha= %.2f)$' % (l, u, a), color=next(dark_color), linestyle='-')
  plot.legend()
  plot.xscale('log')
  plot.yscale('log')
  plot.xlabel(r'$x$', fontsize=13)
  plot.ylabel(r'$p(X > x)$', fontsize=13)
  plot.title(r'$X \sim$ {}'.format(rv) )
  plot.savefig("plot_gensample_check.png")
  plot.gcf().clear()

class Google(RV):
  def __init__(self, k):
    RV.__init__(self, m=0, M=float("inf") )

    self.k = k
    self.sample_l = []
    # with open("filtered_task_lifetimes_for_jobs_w_num_task_{}.dat".format(k), mode="rt") as f:
    with open("task_lifetimes_for_jobs_w_num_task_{}.dat".format(k), mode="rt") as f:
      reader = csv.reader(f)
      for line in reader:
        self.sample_l.append(float(line[0] ) )
    self.sample_l.sort()
    self.num_sample = len(self.sample_l)

  def __str__(self):
    return "Google(k= ".format(self.k)

  def mean(self):
    return sum(self.sample_l)/self.num_sample

  def sample(self):
    return self.sample_l[math.floor(self.num_sample*random.random() ) ]

class SimRV(RV):
  def __init__(self, sample_l):
    RV.__init__(self, m=min(sample_l), M=max(sample_l) )
    self.sample_l = sample_l

    self.num_sample = len(self.sample_l)

  def __str__(self):
    return "SimRV"

  def mean(self):
    return sum(self.sample_l)/self.num_sample

  def sample(self):
    return self.sample_l[math.floor(self.num_sample*random.random() ) ]

class RV_wValsProbs(RV):
  def __init__(self, v_l, p_l):
    RV.__init__(self, m=min(v_l), M=max(v_l) )
    self.v_l = v_l
    self.p_l = p_l

    self.dist = scipy.stats.rv_discrete(name='rv_wValsProbs', values=(v_l, p_l) )

  def __repr__(self):
    return "RV_wValsProbs[\n\tv_l= {}, \n\tp_l= {}]".format(self.v_l, self.p_l)

  def sample(self):
    return self.dist.rvs()

class RV_wValsWeights(RV):
  def __init__(self, v_l, w_l):
    RV.__init__(self, m=min(v_l), M=max(v_l) )
    self.v_l = v_l
    self.w_l = w_l

    total_w = sum(w_l)
    p_l = [w / total_w for w in w_l]
    self.dist = scipy.stats.rv_discrete(name='rv_wValsWeights', values=(v_l, p_l) )

  def __repr__(self):
    return "RV_wValsWeights[\n\tv_l= {}, \n\tw_l= {}]".format(self.v_l, self.w_l)

  def sample(self):
    return self.dist.rvs()

class Dolly(RV):
  ## Kristen et al. A Better Model for Job Redundancy: Decoupling Server Slowdown and Job Size
  def __init__(self):
    RV.__init__(self, m=1, M=12)

    self.v = numpy.arange(1, 13)
    self.p = [0.23, 0.14, 0.09, 0.03, 0.08, 0.1, 0.04, 0.14, 0.12, 0.021, 0.007, 0.002]
    self.dist = scipy.stats.rv_discrete(name='dolly', values=(self.v, self.p) )

  def __str__(self):
    return "Dolly[{}, {}]".format(self.m, self.M)

  def pdf(self, x):
    return self.dist.pmf(x) if (x >= self.m and x <= self.M) else 0

  def cdf(self, x):
    if x < self.m:
      return 0
    elif x > self.M:
      return 1
    return float(self.dist.cdf(x) )

  def sample(self):
    u = random.uniform(0, 1)
    # if u <= 0.23: return 1 + u/100
    # u -= 0.23
    # if u <= 0.14: return 2 + u/100
    # u -= 0.14
    # if u <= 0.09: return 3 + u/100
    # u -= 0.09
    # if u <= 0.03: return 4 + u/100
    # u -= 0.03
    # if u <= 0.08: return 5 + u/100
    # u -= 0.08
    # if u <= 0.1: return 6 + u/100
    # u -= 0.1
    # if u <= 0.04: return 7 + u/100
    # u -= 0.04
    # if u <= 0.14: return 8 + u/100
    # u -= 0.14
    # if u <= 0.12: return 9 + u/100
    # u -= 0.12
    # if u <= 0.021: return 10 + u/100
    # u -= 0.021
    # if u <= 0.007: return 11 + u/100
    # u -= 0.007
    # if u <= 0.002: return 12 + u/100
    # return 12 + u/100 # for safety
    return self.dist.rvs() + u/100

class Bern(RV):
  def __init__(self, L, U, p):
    RV.__init__(self, m=L, M=U)

    self.p = p

  def __str__(self):
    return "Bern(l= {}, u= {}, p= {})".format(self.m, self.M, self.p)

  def mean(self):
    return (1 - self.p)*self.m + self.p*self.M

  def sample(self):
    u = random.uniform(0, 1)
    return self.M + u/100 if u <= self.p else self.m + u/100

if __name__ == "__main__":
  plot_gensample_check()

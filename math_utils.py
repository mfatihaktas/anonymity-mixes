import inspect, math, mpmath, scipy, itertools
from scipy import special
import numpy as np

# def list_to_str(l):
#   return ",".join("%s" % e for e in l)

def H_cont(n):
  return mpmath.quad(lambda x: (1-x**n)/(1-x), [0, 1] )

def H(n):
  if n == 0:
    return 0
  sum_ = 0
  for i in range(1, n+1):
    sum_ += float(1/i)
  return sum_

def H_2(n):
  sum_ = 0
  for i in range(1, n+1):
    sum_ += float(1/(i**2) )
  return sum_

def gen_H(n, k):
  sum_ = 0
  for i in range(1, n+1):
    if (i - k) == 0:
      continue
    sum_ += float(1/(i*(i - k) ) )
  return sum_

# def C(n, k):
#   return scipy.special.binom(n, k)

def C(x, y):
  try:
    binom = math.factorial(x) // math.factorial(y) // math.factorial(x - y)
  except ValueError:
    binom = 0
  return binom

def I(u_l, m, n):
  # den = B(m, n)
  # if den == 0:
  #   return None
  # return B(m, n, u_l=u_l)/den
  return scipy.special.betainc(m, n, u_l)

def B(m, n, u_l=1):
  # return mpmath.quad(lambda x: x**(m-1) * (1-x)**(n-1), [0, u_l] )
  if u_l == 1:
    return scipy.special.beta(m, n)
  else:
    return I(u_l, m, n)*B(m, n)

def G(z):
  return scipy.special.gamma(z)
  # return mpmath.quad(lambda x: x**(z-1) * math.exp(-z), [0, mpmath.inf] )

# Order stats
def cdf_n_k(n, k, X, x): # Pr{X_n:k < x}
  cdf = 0
  for i in range(k, n+1):
    cdf += C(n, i) * X.cdf(x)**i * X.tail(x)**(n-i)
  return cdf

def moment_i_n_k(i, n, k, X): # E[X_n:k]
  return mpmath.quad(lambda x: i*x**(i-1) * (1 - cdf_n_k(n, k, X, x) ), [0, mpmath.inf] )

# Qing
def PK(EV, EV_2, ar):
  if ar*EV >= 1:
    return None
  ET = EV + ar*EV_2/2/(1 - ar*EV)
  if ET > 100: return None
  return ET

def fit_pareto(s_l):
  n = len(s_l)
  
  fit_upper_tail = False # True
  if not fit_upper_tail:
    l = s_l[-1]
    D = 0
    for s in s_l:
      D += math.log(s) - math.log(l)
    a = (n-1)/D
  elif fit_upper_tail:
    l = s_l[-1]
    i = int(math.sqrt(n) ) # int(n*0.5)
    s_l = s_l[:i]
    l_ = s_l[-1]
    D = 0
    for s in s_l:
      D += math.log(s) - math.log(l_)
    a = i/D
  log(WARNING, "done; l= {}, a= {}".format(l, a) )
  return l, a

def fit_tpareto(s_l):
  ## s_l is ordered in descending order
  # i_ = 0
  # for i in range(len(s_l)-1, -1, -1):
  #   if s_l[i] > 1.05:
  #     i_ = i
  #     break
  # n = len(s_l)
  # s_l = s_l[:i_]
  # Pr_to_subtract = (n - i_)/n
  
  n = len(s_l)
  log(WARNING, "n= {}".format(n) )
  fit_upper_tail = False # True
  def solve_a(eq):
    a = 0.01
    _a = None
    while True:
      if eq(a) > 0:
        _a = a
        a += 0.01
      else:
        return _a if _a is not None else 0.01
  
  u = s_l[0]
  if not fit_upper_tail:
    l = s_l[-1]
    r = l/u
    # Did not work somehow
    # a = sympy.Symbol('a')
    # a = sympy.solve(n/a + n*r**a*math.log(r)/(1-r**a) - sum([math.log(x/l) for x in s_l] ) )
    a = solve_a(lambda a: n/a + n*r**a*math.log(r)/(1-r**a) - sum([math.log(x/l) for x in s_l] ) )
  else:
    i = int(math.sqrt(n) ) # int(n*0.5)
    X_ip1 = s_l[i+1]
    r = X_ip1/u
    a = solve_a(lambda a: i/a + i*r**a*math.log(r)/(1-r**a) - sum([math.log(x) - math.log(X_ip1) for x in s_l[:i+1] ] ) )
    l = i**(1/a) * X_ip1*(n - (n-i)*(X_ip1/u)**a)**(-1/a) # 1
  log(WARNING, "done; l= {}, u= {}, a= {}".format(l, u, a) )
  return l, u, a

def fit_sexp(s_l):
  # https://www.statlect.com/fundamentals-of-statistics/exponential-distribution-maximum-likelihood
  D = min(s_l)
  n = len(s_l)
  mu = n/(sum(s_l) - n*D)
  
  return D, mu

if __name__ == "__main__":
  # a = 2
  # f = lambda k: G(1 - 1/a)**(-a/2)/math.sqrt(k+1)
  # print("f(10)= {}".format(f(10) ) )
  # print("f(100)= {}".format(f(100) ) )
  
  n = 10
  for k in range(2*n):
    print("n= {}, k= {}, C(n, k)= {}".format(n, k, C(n, k) ) )

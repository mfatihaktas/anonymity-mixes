from log_utils import *
from math_utils import *
from rvs import *

import scipy

"""
The target sends messages according to Poisson(lambda).
There are n receipients, including the true recipient of the target,
each receiving messages according to Poisson(mu)

N ~ max of n i.i.d. Geometric r.v.'s with success prob of Pr_RecipientReceivesAMsgInWindow.
"""
def EN_WhenNoWinStartsBeforeCurrentFinishes(lambda_, Delta, n, mu, upperBound=False):
  Pr_RecipientReceivesAMsgInWindow = 1 - math.exp(-mu*Delta)
  # log(INFO, "", Pr_RecipientReceivesAMsgInWindow=Pr_RecipientReceivesAMsgInWindow)
  
  zeta = -math.log(Pr_RecipientReceivesAMsgInWindow)
  EN = H(n-1)/zeta
  if upperBound:
    EN += 1
  return EN

def EN(lambda_, Delta, n, mu, upperBound=False):
  Pr_RecipientReceivesAMsgInWindow = 1 - math.exp(-mu*Delta)
  # log(INFO, "", Pr_RecipientReceivesAMsgInWindow=Pr_RecipientReceivesAMsgInWindow)
  
  zeta = -math.log(Pr_RecipientReceivesAMsgInWindow)
  Y = Exp(mu)
  EY_given_Y_leq_Delta = Y.mean_given_leq_x(Delta)

  c = H(n-1)/zeta
  if upperBound:
    c += 1
  return  c * (1 + EY_given_Y_leq_Delta*lambda_)

def ED(lambda_, Delta, n, mu, upperBound=False):
  EN_ = EN_WhenNoWinStartsBeforeCurrentFinishes(lambda_, Delta, n, mu, upperBound)
  # log(INFO, "EN= {}".format(EN_) )
  EX = 1/lambda_
  # EY_given_Y_leq_Delta = (1/mu - (Delta + 1/mu)*math.exp(-mu*Delta))/(1 - math.exp(-mu*Delta))
  Y = Exp(mu)
  EY_given_Y_leq_Delta = Y.mean_given_leq_x(Delta)
  
  return EN_*EX + (EN_ - 1)*EY_given_Y_leq_Delta + Delta

def ED_UB(lambda_, Delta, n, mu):
  EN_ = EN_WhenNoWinStartsBeforeCurrentFinishes(lambda_, Delta, n, mu)
  EX = 1/lambda_
  # EY_given_Y_leq_Delta = (1/mu - (Delta + 1/mu)*math.exp(-mu*Delta))/(1 - math.exp(-mu*Delta))
  Y = Exp(mu)
  EY_given_Y_leq_Delta = Y.mean_given_leq_x(Delta)
  
  # return EN_*EX + (EN_ - 1)*EY_given_Y_leq_Delta + Delta
  return EN_*EX + (EN_ - 1)*Delta + Delta

# ****************************  Traffic Mixer w/ Max Delay  *************************** #
"""
Assumption: maxDelta < Delta
"""
def Pr_receiverQIsEmptyAtStartOfWindow(mu, maxDelay):
  return math.exp(-mu*maxDelay)

def EN_whenNoWinStartsBeforeCurrentFinishes_wMixerWMaxDelay(lambda_, Delta, n, mu, maxDelay, upperBound=False):
  Pr_recipientNotReceiveAMsgInWindow = \
    Pr_receiverQIsEmptyAtStartOfWindow(mu, maxDelay) * math.exp(-mu*Delta)
  
  Pr_recipientReceivesAMsgInWindow = 1 - Pr_recipientNotReceiveAMsgInWindow
  # log(INFO, "", Pr_recipientReceivesAMsgInWindow=Pr_recipientReceivesAMsgInWindow)
  
  zeta = -math.log(Pr_recipientReceivesAMsgInWindow)
  EN = H(n-1)/zeta
  if upperBound:
    EN += 1
  return EN

def EN_wMixerWMaxDelay(lambda_, Delta, n, mu, maxDelay, upperBound=False):
  Pr_recipientNotReceiveAMsgInWindow = \
    Pr_receiverQIsEmptyAtStartOfWindow(mu, maxDelay) * math.exp(-mu*Delta)
  Pr_recipientReceivesAMsgInWindow = 1 - Pr_recipientNotReceiveAMsgInWindow
  
  zeta = -math.log(Pr_recipientReceivesAMsgInWindow)
  Y = Exp(mu)
  EY_given_Y_leq_Delta = Y.mean_given_leq_x(Delta)

  c = H(n-1)/zeta
  if upperBound:
    c += 1
  return  c * (1 + EY_given_Y_leq_Delta*lambda_)

def ED_wMixerWMaxDelay(lambda_, Delta, n, mu, maxDelay, upperBound=False):
  EN_ = EN_whenNoWinStartsBeforeCurrentFinishes_wMixerWMaxDelay(lambda_, Delta, n, mu, maxDelay, upperBound)
  # log(INFO, "EN= {}".format(EN_) )
  EX = 1/lambda_

  ro = 1 - Pr_receiverQIsEmptyAtStartOfWindow(mu, maxDelay)
  Y = Exp(mu)
  func1 = lambda y: Pr_X_eq_x_given_X_leq_y(Y, y, Delta)*(y + maxDelay)
  func2 = lambda y: Pr_X_eq_x_given_X_leq_y(Y, y, Delta)*Delta
  EW_receiverQIsEmptyAtStartOfWindow = \
    scipy.integrate.quad(func1, 0, Delta - maxDelay)[0] + \
    scipy.integrate.quad(func2, Delta - maxDelay, Delta)[0]

  EW_receiverQIsBusyAtStartOfWindow = 0 # maxDelay # /2
  blog(ro=ro,
       EW_receiverQIsEmptyAtStartOfWindow=EW_receiverQIsEmptyAtStartOfWindow)
  
  EW = EW_receiverQIsEmptyAtStartOfWindow * (1 - ro) + \
       EW_receiverQIsBusyAtStartOfWindow * ro
  return EN_*EX + (EN_ - 1)*EW + Delta

if __name__ == "__main__":
  q = lambda n: -math.log(1 - math.exp(-10))/H(n-1)
  print("q(10)= {}".format(q(10) ) )
  print("q(100)= {}".format(q(100) ) )

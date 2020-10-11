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
def EN_WhenNoWinStartsBeforeCurrentFinishes(lambda_, Delta, n, mu):
  Pr_RecipientReceivesAMsgInWindow = 1 - math.exp(-mu*Delta)
  log(INFO, "", Pr_RecipientReceivesAMsgInWindow=Pr_RecipientReceivesAMsgInWindow)
  
  zeta = -math.log(Pr_RecipientReceivesAMsgInWindow)
  return H(n-1)/zeta # + 1

def EN(lambda_, Delta, n, mu):
  Pr_RecipientReceivesAMsgInWindow = 1 - math.exp(-mu*Delta)
  log(INFO, "", Pr_RecipientReceivesAMsgInWindow=Pr_RecipientReceivesAMsgInWindow)
  
  zeta = -math.log(Pr_RecipientReceivesAMsgInWindow)
  Y = Exp(mu)
  EY_given_Y_leq_Delta = Y.mean_given_leq_x(Delta)
  return H(n-1)/zeta * (1 + EY_given_Y_leq_Delta*lambda_)

def ED(lambda_, Delta, n, mu):
  EN_ = EN_WhenNoWinStartsBeforeCurrentFinishes(lambda_, Delta, n, mu)
  log(INFO, "EN= {}".format(EN_) )
  EX = 1/lambda_
  # EY_given_Y_leq_Delta = (1/mu - (Delta + 1/mu)*math.exp(-mu*Delta))/(1 - math.exp(-mu*Delta))
  Y = Exp(mu)
  EY_given_Y_leq_Delta = Y.mean_given_leq_x(Delta)
  
  return EN_*EX + (EN_ - 1)*EY_given_Y_leq_Delta + Delta

def EN_WhenNoWinStartsBeforeCurrentFinishes_UB(lambda_, Delta, n, mu):
  Pr_RecipientReceivesAMsgInTwoWindows = 1 - math.exp(-mu*2*Delta)
  log(INFO, "", Pr_RecipientReceivesAMsgInTwoWindows=Pr_RecipientReceivesAMsgInTwoWindows)
  
  zeta = -math.log(Pr_RecipientReceivesAMsgInTwoWindows)
  return H(n-1)/zeta + 1

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

def EN_whenNoWinStartsBeforeCurrentFinishes_wMixerWMaxDelay(lambda_, Delta, n, mu, maxDelay):
  Pr_recipientNotReceiveAMsgInWindow = \
    Pr_receiverQIsEmptyAtStartOfWindow(mu, maxDelay) * math.exp(-mu*Delta)
  
  Pr_recipientReceivesAMsgInWindow = 1 - Pr_recipientNotReceiveAMsgInWindow
  log(INFO, "", Pr_recipientReceivesAMsgInWindow=Pr_recipientReceivesAMsgInWindow)
  
  zeta = -math.log(Pr_recipientReceivesAMsgInWindow)
  return H(n-1)/zeta # + 1

def ED_wMixerWMaxDelay(lambda_, Delta, n, mu, maxDelay):
  EN_ = EN_whenNoWinStartsBeforeCurrentFinishes_wMixerWMaxDelay(lambda_, Delta, n, mu, maxDelay)
  log(INFO, "EN= {}".format(EN_) )
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

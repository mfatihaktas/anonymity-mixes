from log_utils import *
from math_utils import *

"""
Probability of observing the delivery of NO message from a sender
during target's attack window.
Delta: Length of the attack window
ar: Message generation rate at the sender
d: Unit time epoch length
T: Delivery time of a message, a r.v.
""" 
def Pr_ObservingNoDeliveryFromASender(ar, T, d=0.01):
  Delta = T.M
  Pr = 1
  # Time-0 is the beginning of the attack window
  Pr_MsgGenerated = ar*d
  for t in np.arange(-Delta, 0, d):
    Pr_MsgDeliveredBeforeWindow = T.cdf(abs(t))
    Pr_NoDeliveryTriggered = \
      Pr_MsgGenerated*Pr_MsgDeliveredBeforeWindow \
      + (1 - Pr_MsgGenerated)

    Pr *= Pr_NoDeliveryTriggered

  for t in np.arange(0, Delta, d):
    Pr_MsgDeliveredAfterWindow = T.tail(Delta - t)
    Pr_NoDeliveryTriggered = \
      Pr_MsgGenerated*Pr_MsgDeliveredAfterWindow \
      + (1 - Pr_MsgGenerated)

    Pr *= Pr_NoDeliveryTriggered
  return Pr

"""
E[N] for when the subsequent attack windows are independent.
That is the case when adversary waits for a message to be delivered before picking
up a new message generation at the target as the beginning of a new attack window.
N ~ max of n i.i.d. Geometric r.v.'s with success prob of Pr_SenderTakenAsCandidate
Pr_SenderTakenAsCandidate = Pr{A sender is taken as a candidate in a given attack window}
"""
def EN_IndependentWindows(n, ar, T):
  Pr_SenderTakenAsCandidate = 1 - Pr_ObservingNoDeliveryFromASender(ar, T)
  log(INFO, "", Pr_SenderTakenAsCandidate=Pr_SenderTakenAsCandidate)
  lambda_ = -math.log(Pr_SenderTakenAsCandidate)
  return H(n)/lambda_

def ED_IndependentWindows(n, ar, T):
  EN_IndWin = EN_IndependentWindows(n, ar, T)
  return EN_IndWin*(1/ar + T.M) + T.M

def ED_LB(n, ar, T):
  EN_IndWin = EN_IndependentWindows(n, ar, T)
  return EN_IndWin*1/ar + T.M


















import simpy, random, copy, pprint
from rvs import *
from log_utils import *

# *******************************  Msg  ****************************** #
class Msg(object):
  def __init__(self, _id, flow_id):
    self._id = _id
    self.flow_id = flow_id
    
    self.entrance_time = None
  
  def __repr__(self):
    return 'Msg[_id= {}, flow_id= {}]'.format(self._id, self.flow_id)

# *************************************  MsgGen  ********************************* #
class MsgGen(object):
  def __init__(self, env, _id, ar, nflows, out=None):
    self.env = env
    self._id = _id
    self.ar = ar
    self.nflows = nflows
    self.out = out
    
    self.counter = 0
    
    self.env.process(self.run() )
  
  def __repr__(self):
    return 'MsgGen[_id={}, ar= {}, nflows= {}]'.format(self._id, self.ar, self.nflows)
  
  def run(self):
    inter_arr_rv = Exp(self.ar)
    while 1:
      yield self.env.timeout(inter_arr_rv.sample() )
      self.counter += 1
      self.out.put(Msg(_id=self.counter, flow_id=random.randint(0, self.nflows-1) ) )

# *****************************************  Q  ************************************* #
class Q(object):
  def __init__(self, _id, env):
    self._id = _id
    self.env = env

class QMonitor(object):
  def __init__(self, env, q, poll_interval):
    self.q = q
    self.env = env
    self.poll_interval = poll_interval
    
    self.pollt_l = []
    self.qlength_l = []
    self.action = env.process(self.run() )
  
  def run(self):
    while True:
      yield self.env.timeout(self.poll_interval)
      
      self.pollt_l.append(self.env.now)
      self.qlength_l.append(self.q.length() )

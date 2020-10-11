import simpy, random, copy, pprint

from rvs import *
from log_utils import *

# *******************************  Msg  ****************************** #
class Msg(object):
  def __init__(self, _id, flowId):
    self._id = _id
    self.flowId = flowId

    self.entranceTime = None

  def __repr__(self):
    return 'Msg[_id= {}, flowId= {}]'.format(self._id, self.flowId)

# *************************************  MsgGen  ********************************* #
class MsgGen(object):
  def __init__(self, env, _id, ar, nflows, out, generator=None):
    self.env = env
    self._id = _id
    self.ar = ar
    self.nflows = nflows
    self.out = out
    self.generator = generator

    self.counter = 0

    self.env.process(self.run() )

  def __repr__(self):
    return 'MsgGen[_id={}, ar= {}, nflows= {}]'.format(self._id, self.ar, self.nflows)

  def run(self):
    inter_arr_rv = Exp(self.ar)
    while 1:
      yield self.env.timeout(inter_arr_rv.sample() )
      self.counter += 1
      
      if self.generator is None:
        m = Msg(_id=self.counter, flowId=random.randint(0, self.nflows-1) )
      else:
        m = self.generator(_id=self.counter, flowId=random.randint(0, self.nflows-1) )
      self.out.put(m)

# *****************************************  Q  ************************************* #
class Q(object):
  def __init__(self, _id, env, out):
    self._id = _id
    self.env = env
    self.out = out

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
      
# **************************************  Slave Q  ********************************** #
class SlaveQ(Q): # Release HoL at command
  def __init__(self, _id, env, out=None):
    super().__init__(_id, env, out)

    self.m_l = []
    self.n_recved = 0
    self.n_released = 0
    self.qt_l = []

  def __repr__(self):
    return "SlaveQ[_id={}]".format(self._id)

  def length(self):
    return len(self.m_l)

  def Eqt(self):
    return sum(self.qt_l)/len(self.qt_l)
    # nonzero_qt_l = [t for t in self.qt_l if t > 0.000001]
    # return sum(nonzero_qt_l)/len(nonzero_qt_l)

  def Eqt2(self):
    return sum([t**2 for t in self.qt_l] )/len(self.qt_l)

  def put(self, m):
    slog(DEBUG, self.env, self, "recved", m)
    self.n_recved += 1
    m.ref_time = self.env.now

    self.m_l.append(m)

  def release(self):
    if len(self.m_l):
      m = self.m_l.pop(0)
      self.qt_l.append(self.env.now - m.ref_time)
      slog(DEBUG, self.env, self, "released", m)
      self.n_released += 1

      if self.out is not None:
        self.out.put(m)

# **************************************  Slave Q  ********************************** #
class Mix(object):
  def __init__(self, env, _id, n, k):
    self.env = env
    self._id = _id
    self.n = n
    self.k = k

    self.i_q_l = []
    for i in range(self.n):
      self.i_q_l.append(SlaveQ(_id=i, env=env) )

    self.start_time = env.now

  def __repr__(self):
    return "Mix[_id= {}, n={}, k={}]".format(self._id, self.n, self.k)

  def state(self):
    ql_l = [self.i_q_l[i].length() for i in range(self.n) ]
    return ','.join(map(str, ql_l) )

  def qt_l(self):
    l = []
    for q in self.i_q_l:
      l.extend(q.qt_l)
    return l

  def ET_ET2(self):
    ET_l, ET2_l = [], []
    for q in self.i_q_l:
      ET_l.append(q.Eqt() )
      ET2_l.append(q.Eqt2() )
    return np.mean(ET_l), np.mean(ET2_l)

  def throughput(self):
    n_released = sum([q.n_released for _, q in enumerate(self.i_q_l) ] )
    return n_released/(self.env.now - self.start_time)

# *************************  First Come First Served  ********************** #
class FCFS(): # First Come First Served
  def __init__(self, _id, env, V, out=None):
    self._id = _id
    self.env = env
    self.V = V # service time r.v.
    self.out = out
    
    self.q = simpy.Store(env)
    self.run_process = env.process(self.run() )
  
  def __repr__(self):
    return "FCFS[_id= {}, V= {}]".format(self._id, self.V)

  def put(self, m):
    slog(DEBUG, self.env, self, "recved", m)
    self.q.put(m)
  
  def run(self):
    while 1:
      m = yield (self.q.get())
      t = self.V.sample()
      slog(DEBUG, self.env, self, "will serv for t= {}".format(t), m)
      yield self.env.timeout(t)
      
      if self.out is not None:
        self.out.put(m)  

class FCFS_wZeroDelayStartForBusyPeriod(FCFS):
  def __init__(self, _id, env, V, out=None):
    super().__init__(_id, env, V, out)
    
    self.run_process = env.process(self.run() )
  
  def __repr__(self):
    return "FCFS_wZeroDelayStartForBusyPeriod[_id= {}, V= {}]".format(self._id, self.V)

  def put(self, m):
    slog(DEBUG, self.env, self, "recved", m)
    if len(self.q.items) == 0:
      m.serv_time = 0
    else:
      m.serv_time = self.V.sample()
    self.q.put(m)
  
  def run(self):
    while 1:
      m = yield (self.q.get())
      t = m.serv_time
      slog(DEBUG, self.env, self, "will serv for t= {}".format(t), m)
      yield self.env.timeout(t)
      
      if self.out is not None:
        self.out.put(m)

class FCFS_wMaxDelay(FCFS):
  def __init__(self, _id, env, maxDelay, out=None):
    super().__init__(_id, env, 0, out)
    self.maxDelay = maxDelay
    
    # self.releaseByTimeEvent = None
    # self.releaseByTime = None
    self.controlWindowEndTime = None
    self.run_process = env.process(self.run() )
  
  def __repr__(self):
    return "FCFS_wMaxDelay[_id= {}, maxDelay= {}]".format(self._id, self.maxDelay)
  
  def put(self, m):
    slog(DEBUG, self.env, self, "recved", m)
    m.entrance_time = self.env.now
    self.q.put(m)
  
  # def release_by(self, t):
  #   slog(DEBUG, self.env, self, "release_by", t)
  #   if self.releaseByTimeEvent is not None:
  #     self.releaseByTime = t
  #     slog(DEBUG, self.env, self, "will releaseByTimeEvent.succeed()", self.releaseByTime)
  #     self.releaseByTimeEvent.succeed()

  def start_control_window(self, endTime):
    slog(DEBUG, self.env, self, "start_control_window", endTime)
    if self.controlWindowEndTime is None:
      self.controlWindowEndTime = endTime
    
  def run(self):
    while 1:
      m = yield (self.q.get())
      timeInQ = self.env.now - m.entrance_time
      if timeInQ > self.maxDelay:
        slog(ERROR, self.env, self, "timeInQ= {} > maxDelay= {}".format(timeInQ, self.maxDelay), None)
        break
      
      # self.releaseByTimeEvent = self.env.event()
      # t = self.maxDelay - timeInQ
      # slog(DEBUG, self.env, self, "will wait for t= {}".format(t), m)
      # yield (self.releaseByTimeEvent | self.env.timeout(t) )
      # self.releaseByTimeEvent = None
      # if self.releaseByTime is not None:
      #   slog(DEBUG, self.env, self, "wait stopped by releaseByTimeEvent", m)
      #   timeInQ = self.env.now - m.entrance_time
      #   t = min(self.maxDelay - timeInQ, self.releaseByTime - self.env.now)
      #   # log(INFO, "self.maxDelay - timeInQ= {}, self.releaseByTime - self.env.now= {}".format(self.maxDelay - timeInQ, self.releaseByTime - self.env.now) )
      #   self.releaseByTime = None
      #   slog(DEBUG, self.env, self, "after release_by; will wait for t= {}".format(t), m)
      #   yield self.env.timeout(t)

      t = self.maxDelay - timeInQ
      if self.controlWindowEndTime is not None:
        if self.controlWindowEndTime - self.env.now > 0: # o.w. the connected recipient got already exposed
          t = min(t, self.controlWindowEndTime - self.env.now)
      slog(DEBUG, self.env, self, "will wait for t= {}".format(t), m)
      yield self.env.timeout(t)
      self.controlWindowEndTime = None
      
      if self.out is not None:
        self.out.put(m)

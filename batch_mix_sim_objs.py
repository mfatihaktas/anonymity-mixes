from sim_objs import *

# **************************************  Slave Q  ********************************** #
class SlaveQ(Q): # Release HoL at command
  def __init__(self, _id, env):
    super().__init__(_id, env)
    
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

# *************************************  Batch Mix  ****************************************** #
# n servers with Poisson arrivals, once any k servers are busy, Hol is immediately released.
class BatchMix(object):
  def __init__(self, env, _id, n, k):
    self.env = env
    self._id = _id
    self.n = n
    self.k = k
    
    self.i_q_m = []
    for i in range(self.n):
      self.i_q_m.append(SlaveQ(_id=i, env=env) )
    
    self.start_time = env.now
    
  def __repr__(self):
    return "BatchMix[_id= {}, n={}, k={}]".format(self._id, self.n, self.k)
  
  def state(self):
    ql_l = [self.i_q_m[i].length() for i in range(self.n) ]
    return ','.join(map(str, ql_l) )
  
  def qt_l(self):
    l = []
    for q in self.i_q_m:
      l.extend(q.qt_l)
    return l
  
  def ET_ET2(self):
    ET_sum, ET2_sum = 0, 0
    for q in self.i_q_m:
      ET_sum += q.Eqt()
      ET2_sum += q.Eqt2()
    return ET_sum/self.n, ET2_sum/self.n
  
  def throughput(self):
    n_released = sum([q.n_released for _, q in enumerate(self.i_q_m) ] )
    return n_released/(self.env.now - self.start_time)
  
  def put(self, m):
    slog(DEBUG, self.env, self, "recved", m)
    self.i_q_m[m.flow_id].put(m)
    
    o_l = []
    for i, q in enumerate(self.i_q_m):
      if q.length():
        o_l.append(i)
    
    if len(o_l) >= self.k:
      for i in o_l:
        self.i_q_m[i].release()

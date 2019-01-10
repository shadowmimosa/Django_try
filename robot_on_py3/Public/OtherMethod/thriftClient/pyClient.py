#!/usr/bin/env python
'a thrift python client'
__author__ = 'hottoli'

import sys
import glob
import os
import importlib
import platform

exedir = os.path.abspath('.')
pfs = platform.platform(aliased=0, terse=0)
if pfs.find("Windows") + 1:
  diri = "\\Resources\\Lib\\thriftClient\\"
else:
  diri = "/Resources/Lib/thriftClient/" 	
sys.path.insert(0,glob.glob(exedir + diri)[0]) 

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from dubboTransport.TDubboxHeaderTransport import TDubboxHeaderTransport


class pyClient(object):
  def __init__(self):
    self.name = "Client"

  def _lazyimport(self, servicelib):
    self.slobj = importlib.import_module(servicelib)
    self.clientobj = getattr(self.slobj, self.name)


  def dubboxrequest(self, host, port, servicelib, servicename, methodname, args= None):
    """request use kgthrift""" 	
    #lazy import
    self._lazyimport(servicelib)

    try:
      transport = TSocket.TSocket(host, port)
      transport = TDubboxHeaderTransport(transport, servicename)
      protocol = TBinaryProtocol.TBinaryProtocol(transport)
      client = self.clientobj(protocol)
      method = getattr(client, methodname)
      transport.open()
      if args == None:
        res = method() #todo format args
      else: 
		res = method(args)
      transport.close()

    except Thrift.TException, tx:
      print '%s' %  (tx.message)

    return res #todo format res




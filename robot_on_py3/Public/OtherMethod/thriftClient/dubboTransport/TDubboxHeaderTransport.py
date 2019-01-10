#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

# kgThrift framed protocol codec.
#
# <pre>
# |<-                                 message header                                                               ->|<- message body ->|
# +-----------------+--------------------+-------------+-------------------------------------------------------------+------------------+
# | magic (2 bytes) |  version (1 byte)  | header size | com.alibaba.dubbo.rpcprotocol.kgthrift.header.HeaderContent |   message body   |
# +-----------------+--------------------+---------------------------------------------------------------------------+------------------+
# |<-                                                           message size                                                          ->|



from thrift.transport.TTransport import *
from thrift.protocol import TBinaryProtocol
from header.ttypes import HeaderContent


class TDubboxHeaderTransport(TTransportBase, CReadableTransport):
  """Class that wraps another transport and frames its I/O when writing."""

  def __init__(self, trans, servicename):
    self.__trans = trans
    self.__rbuf = StringIO()
    self.__wbuf = StringIO()

    # customer header info
    self.__MAGIC = 0xdabc
    self.__VERSION = 1
    self.servicename = servicename

  def isOpen(self):
    return self.__trans.isOpen()

  def open(self):
    return self.__trans.open()

  def close(self):
    return self.__trans.close()

  def read(self, sz):
    ret = self.__rbuf.read(sz)
    if len(ret) != 0:
      return ret

    self.readFrame()
    return self.__rbuf.read(sz)

  def readFrame(self):
    buff = self.__trans.readAll(4)
    sz, = unpack('!i', buff)

    self.__trans.readAll(2)
    self.__trans.readAll(1)
    buff = self.__trans.readAll(2)
    headlen, =  unpack('!H', buff)

    self.__trans.readAll(headlen-5)
    self.__rbuf = StringIO(self.__trans.readAll(sz-headlen))

  def write(self, buf):
    self.__wbuf.write(buf)

  def flush(self):
    seqId = 1  #todo

    # add dubbox header.content
    header = HeaderContent(seqId, self.servicename)
    transport = TMemoryBuffer()
    protocal = TBinaryProtocol.TBinaryProtocol(transport)
    header.write(protocal)
    transport.flush()

    # add  message header
    woh = transport.getvalue()
    wszh = len(woh)+5
    buf =  pack("!H", self.__MAGIC) + pack("!b", self.__VERSION) + pack("!h", wszh) + woh
    wout = self.__wbuf.getvalue()
    # reset wbuf before write/flush to preserve state on underlying failure
    self.__wbuf = StringIO()
    # N.B.: Doing this string concatenation is WAY cheaper than making
    # two separate calls to the underlying socket object. Socket writes in
    # Python turn out to be REALLY expensive, but it seems to do a pretty
    # good job of managing string buffer operations without excessive copies
    lenall = len(buf)+len(wout)

    #flush
    self.__trans.write(pack('!i',lenall)) #frame
    self.__trans.write(buf)
    self.__trans.write(wout)
    self.__trans.flush()

  # Implement the CReadableTransport interface.
  @property
  def cstringio_buf(self):
    return self.__rbuf

  def cstringio_refill(self, prefix, reqlen):
    # self.__rbuf will already be empty here because fastbinary doesn't
    # ask for a refill until the previous buffer is empty.  Therefore,
    # we can start reading new frames immediately.
    while len(prefix) < reqlen:
      self.readFrame()
      prefix += self.__rbuf.getvalue()
    self.__rbuf = StringIO(prefix)
    return self.__rbuf


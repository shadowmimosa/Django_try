namespace java com.alibaba.dubbo.rpc.protocol.kgthrift.header

struct HeaderContent{
   1:required i64 seqId,
   2:required string servicename,
   3:optional map<string,string> attachment,
}
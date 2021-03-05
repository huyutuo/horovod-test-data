# horovod协调部分详细过程
# 整体流程
![流程图 -1-](media/16142726830976/%E6%B5%81%E7%A8%8B%E5%9B%BE%20-1-.jpg)



# 各个步骤流程
1. 将计算完成的tensor移至message_queue_tmp
2. 根据message_queue_tmp中的message是否命中response_cache(位图？)，更新cache_coordinate
![流程图 -2-](media/16142726830976/%E6%B5%81%E7%A8%8B%E5%9B%BE%20-2-.jpg)

3. 同步节点间的cache_coordinator(allreduce?)
![流程图 -3-](media/16142726830976/%E6%B5%81%E7%A8%8B%E5%9B%BE%20-3-.jpg)

4. 移除message_queue_tmp在response_cache中，不在cache_coordinate中的message(什么样的tensor满足这个条件？)
被移除的message，下一轮进行处理
5. 判断是否需要进行同步
如果response_cache_的容量大于0并且cache_coordinator中没有未进行同步的cache则不需要进行同步，否则需要同步（什么意思？）
6. （只在rank0上执行）判断message_queue_tmp中的每个message是否可以进行同步（通过rank0进行的协调？），得到ready_to_reduce
通过IncrementTensorCount函数来根据
message_table_ 中tensor_name所对应的信息去判断断request中的tensor是否在所有节点上都已经ready了。
**message_table_**是一个map，保存了coordinator收到的所有request消息。key是Tensor name, value是一个vector，长度是rank的个数，其中的元素是每个rank发来的request。当这个vector填满的时候，对应的tensor就可以进行allreduce了。
**ready_to_reduce**是一个vector<string>, 其中保存了已经完全ready的tensor_name
7. （只在rank0上执行）RecvReadyTensors，同步节点间的ready_to_reduce，存放至ready_list
通过mpi gather接收其他rank发来的RequestList，按 rank 顺序放入ready_list
8. （只在rank0上执行）判断ready_list中其余节点的request是否可以进行reduce，添加至ready_to_reduce中
判断方法与步骤6相同
9.  创建responses
responses中存放了需要进行传输的response
    1. 首先存放cache_coordinator 中cache_hits所对应的response_cache
    2. 然后存放ready_list中所对应的response
1. fuseResponses得到response_list
把多个相邻的response里的内容放入一个response对象(需满足如下条件)，再把这些response对象放入ResponseList返回
  1. 执行的操作类型相同
  2. 在同一个设备上
  3. tensor类型相同
  4. tensor大小之和不超过tensor fusion buffer大小
  5. prescale_factor和postscale_factor相同
11. coordinate广播最终得到的response_list
SendFinalTensors，通过mpi_Bcast实现
12. 此轮得到的response_list放进response_cache中
如果response_cache的容量大于0，并且之前进行了communication则将此轮得到的response_list放进response_cache中

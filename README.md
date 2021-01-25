

# 测试集群环境
## 集群机器
张家口区的horovod-4gpu-test001~horovod-4gpu-test003。
## 登录方式
开启horovod-4gpu-test001后, ssh 公网ip，密码:(). 利用horovod-dev001当做跳板机可以直接ssh连接至其他节点.
## 集群机器配置
阿里云机器实例 ：ecs.gn6e-c12g1.12xlarge


|实例规格| vCPU	内存（GiB）|内存（GiB）| GPU  | GPU显存（GB）  | 网络带宽能力（出+入）（Gbit/s）  |  网络收发包能力（出+入）（万PPS） |
|---|---|---|---|---|---|---|---|---|
|  ecs.gn6e-c12g1.2xlarge |48  |  368.0 | V100*4  | 128  | 16.0 | 240|

## 集群间延迟
节点间的平均延迟为0.140ms，具体延迟如下,第一列为发送ping命令的节点rank:

```
0 1  avg_time=0.149ms
0 2  avg_time=0.158ms
0 3  avg_time=0.134ms

1 0  avg_time=0.135ms
1 2  avg_time=0.148ms
1 3  avg_time=0.122ms

2 0  avg_time=0.154ms
2 1  avg_time=0.147ms
2 3  avg_time=0.143ms

3 0  avg_time=0.130ms
3 1  avg_time=0.131ms
3 2  avg_time=0.140ms
```

# 文件结构

## 文件总体结构
文件总体分为三部分
- horovod-test-data：其中存放测试horovod程序时的数据
- nccl-test-data：其中存放测试nccl时的数据
- scripts: 存放测试使用的脚本
- tmp-file: 一些原始数据或者重复的数据，暂时用不到

## 文件详细说明
这里简要说明各个文件的内容，对于测试数据，在单个的文件中有环境以及数据的详细说明。
### scripts
- install-horovod.sh

修改horovod源码之后，方便安装horovod的脚本

- get_avg.py

解析在horovod测试输出的log信息，获取训练中传输的数据大小以及传输时间，传输速度等信息

- nccl-test.py

分不同的参数，不同的数据大小，执行多次nccl allreduce测试，获取传输速度

- nccl-fusion-test.py

测试传输相同的数据大小，分不同的小数据传输的时间差距。例如传输1000M的数据，1次传输1000M与1000次传输1M的时间差距

- time-fusion-test.py

测试传输不同的数据大小所花费的时间

### horovod-test-data
- resnet和vgg测试数据.md

存放了在2020-11-03 与 2020-11-04 horovod测试的数据，主要是训练中每个步骤所花费的时间以及训练时的传输速度
- all-message.md

存放了2020-12中horovod测试的数据，数据为训练中传输不同大小数据的数量以及传输速度
- autotune 测试结果.md

数据为不使用autotune，使用aututune以及使用autotune得到的最优参数进行训练的区别
- autotune 最优参数.md

数据为使用autotune与不使用autotune进行训练的区别，其中包含了使用autotune得到的最优参数

### nccl-test-data
- 不同数据大小传输时间.xlsx

测试nccl 在传输不同大小的数据时所花费的时间，其中 -n 参数为1，即每次都要通过mpirun命令来进行测试
- nccl-16个GPU-传输速率.xlsx

nccl在4*4块GPU上传输的速率
- nccl不同数据大小i-o速率_i.xlsx

nccl在传输不同数据大小时的速率
- nccl—test各阶段耗时_i.txt

nccl-test中有多个阶段，包括从运行mpirun至到test main函数，以及获取内存等阶段，文件中记录了在测试中的原始数据


# 默认测试参数
如无特殊说明，默认的测试参数为:

测试集群: 上文中提到的阿里云集群

硬件: ecs.gn6e-c12g1.12xlarge 的配置

## horovod测试默认参数
如测试文件夹内无特殊说明，则默认训练的epoch为10，batch为10，batch_size为32

## nccl-test 默认参数
 -g 1  -w 0 -c 0






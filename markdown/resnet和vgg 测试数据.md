
进行训练时，每次训练跑90epoch，每个epoch中跑50次batch，batch_size皆为32。通讯库使用的是NCCL。
四卡与单卡进行训练时，因为每块卡的batch_size相同，所以四卡的训练是单卡的训练数据的四倍。若比较训练速度，将4卡总训练时长/4，这样可以大致比较在相同大小数据集下，训练速度的提升。

训练数据为imagenet数据集。GPU皆为V100。第一行括号里的数字为性能提升，如2282.8/(578.1*4)=99%



autotune: 开启horovod自动调整，--autotune
fp16: 在allreduce阶段使用fp16压缩
auto log: 使用通过autotune得到的最优参数进行训练
resnet: autotune 产生log中选择score最高的一组配置

```
hierarchical_allreduce,hierarchical_allgather,cache_enabled,cycle_time_ms,tensor_fusion_threshold,score
0,0,1,5,4,439.25
```
vgg16:

```
hierarchical_allreduce,hierarchical_allgather,cache_enabled,cycle_time_ms,tensor_fusion_threshold,score
0,1,0,5,4,409.135
```

|(resnet50)  |单机单卡 |4机4卡(2.5G带宽)|4机4卡(5G带宽)|单机4卡|4机4卡(5G)(autotune)|4机4卡(5G)(fp16)|4机4卡(auto log)|
|---|---|---|---|---|---|---|---|
|总训练时长 |578.1s|2282.8s (99%)|1142.5s  (49%)|669.5s  (29%)|1415.8s|689.9s|1141.3s|
|单个batch平均时长|128.4ms|507.3ms|254ms|148.8ms |314.6ms |153.3ms |253.6ms |
|batch-data-tocuda平均时长*|45.5ms|1.9ms|1.9ms|2.3ms|1.88ms|1.88ms|1.86ms|
|foword平均时长   |13.3ms|12.6ms|11.5ms|12.7ms|11.3ms|11.5ms|11.5ms|
|compute_loss平均时长|28.1ms|39.1ms|31.9ms|31.5ms|69.3ms|30.8ms|31.0ms|
|backword平均时长|13.4ms|39.3ms|41.6ms|37.1ms|38.4ms|42.4ms|41.0ms|
|update gradients平均时长|8.8ms|390.5ms|145.4ms|41.8ms|173.4ms|46.7ms|147.8ms|
|receving|9.6Kb/s|2.61Gb/s|5.02Gb/s|8.6Kb/s|4.04Gb/s|4.13Gb/s|5.0Gb/s|
|sending|46.2Kb/s|2.50Gb/s|4.82Gb/s|35.4Kb/s|3.87Gb/s|3.96Gb/s|4.8Gb/s|

-------

|(vgg16)  |单机单卡 |4机4卡(2.5G带宽)|4机4卡(5G带宽)|单机4卡|4机4卡(5G)(autotune)|4机4卡(5G)(fp16)|4机4卡(auto log)|
|---|---|---|---|---|---|---|---|
|总训练时长 |885.0s|12227.6s  （345%）|6116.9s   (173%)|984.0s   (28%)|6642.0s|3063.4s|6116.7s|
|单个batch平均时长|196.7ms|2717.3ms|1359.3.9ms|218.7ms|1476.0,s|680.8ms|1359.3ms|
|batch-data-tocuda平均时长*|113.7ms|6.7ms|7.7ms|8.4ms|7.5ms|7.6ms|7.5ms|
|foword平均时长   |4.2ms|4.7ms|4.1ms|4.5ms|4.1ms|4.13ms|4.0ms|
|compute_loss平均时长|54.7ms|74.1ms|59.0ms|57.0ms|95.3ms|59.6ms|57.0ms|
|backword平均时长|4.8ms|9.2ms|8.7ms|8.6ms|8.15ms|10.4ms|8.5ms|
|update gradients平均时长|2.8ms|2601.0ms|1259.9ms|119.3ms|1342.9ms|580.4ms|1263.6ms|
|receving|6.9Kb/s|2.66Gb/s|5.12Gb/s|6.3Kb/s|4.72Gb/s|5.10Gb/s|5.12Gb/s|
|sending|32.8Kb/s|2.59Gb/s|4.97Gb/s|28.0Kb/s|4.55Gb/s|4.93Gb/s|4.93Gb/s|

*训练脚本中的DataLoader指定了num_workers=4，数据加载和计算并行，导致单机单卡上把数据加载到GPU的时间变长。如果把num_workers设置为1或者去掉，则单机单卡上的加载时间和分布式的接近。
# -*- coding: UTF-8 -*-
import os
import matplotlib.pyplot as plt
import sys
import time
import re
import datetime

# 判断小的数据量在合并成大的数据量之后，速度的变化，以及运行时间的比较
mpi_command = "mpirun -np 4 -H localhost:1,172.26.89.160:1,172.26.89.159:1,172.26.89.158:1 --allow-run-as-root "
nccl_command = " ./build/all_reduce_perf -g 1  -w 0 -c 0"
init_file_path = "/root/nccl-tests/test-files/"
working_dir = "/root/nccl-tests"
thread_socket = [[1,1], [1,2], [1,4], [2,1], [2,2], [2,4], [4,1], [4,2], [4,4]]
thread_socket_default = [[1,1]]
small_data = [10, 20, 30]
fusion_file = open("/root/hyt/horovod-test-data/scripts/time-test.txt", 'wt')
def run_test(data_path, init_command):
  os.chdir(working_dir)
  for i in range(5):
    command = init_command + " -b 10M -e 10M -n 1"
    for data in small_data:
      total_start_time = datetime.datetime.now()
      for j in range(data):
        start_time = datetime.datetime.now()
        os.system(command)
        end_time = datetime.datetime.now()
        print(i,"-", j, " : ", (end_time - start_time).total_seconds(), file = fusion_file)
      total_end_time = datetime.datetime.now()
      print(data, " * -n 1 ", " : ", (total_end_time - total_start_time).total_seconds(), file = fusion_file)

      command = init_command + " -b 10M  -e 10M  -n " + str(data)
      start_time = datetime.datetime.now()
      os.system(command)
      end_time = datetime.datetime.now()
      print("1 * -n ", data , " : ", (end_time - start_time).total_seconds(), file = fusion_file)

      command = init_command + " -b " + str(data * 10) + "M -e " +  str(data * 10) + "M -n 1"
      start_time = datetime.datetime.now()
      os.system(command)
      end_time = datetime.datetime.now()
      print("1 * -n 1" , " : ", (end_time - start_time).total_seconds(), file = fusion_file)
    time.sleep(60)



def file_cmp(x):
  return int(x[:-1])



def data_run():
  data_path_name_str = time.strftime("%m-%d-%H-%M", time.localtime())
  kinds = {"_default": " "}
  for kind in kinds:
    for v in thread_socket_default:
      data_path = os.path.join(init_file_path, data_path_name_str)
      data_path += "_THREADS_" + str(v[0]) + "-"
      data_path += "SOCKETS_" + str(v[1])
      data_path += kind
      if not os.path.exists(data_path):
        os.makedirs(data_path)
      print(data_path)

      init_command = mpi_command + " -x NCCL_SOCKET_NTHREADS=" + str(v[0])
      init_command += " -x NCCL_NSOCKS_PERTHREAD=" + str(v[1])
      init_command += kinds[kind]
      init_command += nccl_command
      run_test(data_path, init_command)


if __name__ == "__main__":
  data_run()
# -*- coding: UTF-8 -*-
import os
import matplotlib.pyplot as plt
import sys
import time
import re
import datetime

# 判断小的数据量在合并成大的数据量之后，速度的变化，以及运行时间的比较
mpi_command = "mpirun -np 4 -H localhost:1,172.26.89.160:1,172.26.89.159:1,172.26.89.158:1 --allow-run-as-root "
nccl_command = " ./build/all_reduce_perf -g 1  -w 0 -c 0 "
init_file_path = "/root/nccl-tests/test-files/"
working_dir = "/root/nccl-tests"
thread_socket = [[1,1], [1,2], [1,4], [2,1], [2,2], [2,4], [4,1], [4,2], [4,4]]
thread_socket_default = [[1,1]]
small_data = [1, 10, 20, 50, 100]
fusion_file = open("/root/hyt/horovod-test-data/scripts/fusion-test.txt", 'wt')
def run_test(data_path, init_command):
  os.chdir(working_dir)
  for i in range(100, 1001, 100):
    for num in small_data:
      command  = init_command + " -n " + str(i/num)
      command = command + " -b " + str(num) + "M -e " + str(num) + "M "
      file_path = os.path.join(data_path, str(i) + "M-" + str(i/num) + "*" + str(num) + "M")
      command = command + " > " + file_path
      print(command)
      start_time = datetime.datetime.now()
      os.system(command)
      end_time = datetime.datetime.now()
      print(file_path, " : ", (start_time - end_time).microseconds, file = fusion_file)
      print(str(i) + "M-" + str(i/num) + "*" + str(num) + "M test over")
    command  = init_command + " -n 1 "
    command = command + " -b " + str(i) + "M -e " + str(i) + "M"
    file_path = os.path.join(data_path, str(i) + "M")
    command = command + " > " + file_path
    print(command)
    start_time = datetime.datetime.now()
    os.system(command)
    end_time = datetime.datetime.now()
    print(file_path, " : ", (start_time - end_time).microseconds, file = fusion_file)

def file_cmp(x):
  return int(x[:-1])

def get_data():
  def cmp(tmp_path):
    return tmp_path.split("_")[-1]
  f = open("/root/hyt/horovod-test-data/scripts/nccl_test.txt", 'wt')
  kinds = ["D", "R", "T",]

  print("data-size,", end = "", file = f)
  for kind in kinds:
    for v  in thread_socket:
      tsstr = kind + "-T" + str(v[0]) + "-S" + str(v[1]) + '-'
      print(tsstr + "o, " + tsstr + "i, ", end = "", file = f)
  print("", file = f)

  data_paths = os.listdir(init_file_path)
  print(data_paths)
  data_paths.sort()
  data_paths.sort(key=cmp)

  data_excel = {}
  for data_path in data_paths:
    print(data_path)
    #print(data_path, "\n", file = f)

    data_path = os.path.join(init_file_path, data_path)
    files = os.listdir(data_path)
    files = sorted(files, key=file_cmp)
    for file in files:
      all_data = [""] * 10
      all_data[0] = file[:-1]
      file = os.path.join(data_path, file)
      print(file)
      rf = open(file)
      line = rf.readline()
      
      
      while line:
        if line[0] != '#':
          data = re.split(r"[ ]+", line.strip(" \n"))
          all_data[2] = str(float(data[5]) * 8)
          all_data[3] = str(float(data[6]) * 8)
          all_data[4] = str(float(data[9]) * 8)
          all_data[5] = str(float(data[10]) * 8)
          # print(data)
        elif line.find("Avg") != -1:
          data = re.split(r"[ ]+", line.strip(" \n"))
          # print(data)
          all_data[1] = str(float(data[5]) * 8)
        line = rf.readline()
      # print(all_data)
      if all_data[0] in data_excel:
        data_excel[all_data[0]].append(all_data[3])
        data_excel[all_data[0]].append(all_data[5])
      else:
        data_excel[all_data[0]] = []
        data_excel[all_data[0]].append(all_data[3])
        data_excel[all_data[0]].append(all_data[5])
      #print(all_data[0], all_data[3], all_data[5], file = f)
      rf.close()
  
    #print("\n\n\n\n", file = f)
  print(data_excel)
  for data in data_excel:
    print(data, ",".join(data_excel[data]), file = f)
  f.close()

def data_run():

  
  data_path_name_str = time.strftime("%m-%d-%H-%M", time.localtime())
  kinds = {"_default": " ", "_ring":" -x NCCL_ALGO=Ring ", "_tree":" -x NCCL_ALGO=Tree"}
  for kind in kinds:
    for v in thread_socket:
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
  #get_data()
  #draw_pic()
  #get_excel()
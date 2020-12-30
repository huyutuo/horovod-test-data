# -*- coding: UTF-8 -*-
import os
import matplotlib.pyplot as plt
import sys
import time
import re

init_command = "mpirun -np 4 -H localhost:1,172.26.89.160:1,172.26.89.159:1,172.26.89.158:1 --allow-run-as-root  ./build/all_reduce_perf -g 1  -w 0 -c 0"
init_file_path = "/root/nccl-tests/test-files/"
working_dir = "/root/nccl-tests"

def run_test(data_path):
  os.chdir(working_dir)
  command = init_command + " -b 1M -e 1M "
  file_path = os.path.join(data_path, "1M")
  command = command + " > " + file_path
  print(command)
  os.system(command)
  print("1M test over")

  for i in range(50, 1001, 50):
    i_str = str(i)
    command = init_command + " -b " + i_str + "M -e " + i_str + "M"
    file_path = os.path.join(data_path, i_str + "M")
    command = command + " > " + file_path
    print(command)
    os.system(command)
    print(i, "M test over")


def file_cmp(x):
  return int(x[:-1])

def get_data():
  f = open("/root/hyt/horovod-test-data/scripts/nccl_test.md", 'wt')

  data_paths = os.listdir(init_file_path)
  print(data_paths)
  data_paths.sort()
  for data_path in data_paths:
    print(data_path)
    print("##", data_path, "\n", file = f)
    print("|大小/MB|速率/Gbps|o-algbw|o-busbw|i-algbw|i-busbw|\n|---|---|---|---|---|---|", file = f)
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
          all_data[2] = data[5]
          all_data[3] = data[6]
          all_data[4] = data[9]
          all_data[5] = data[10]
          # print(data)
        elif line.find("Avg") != -1:
          data = re.split(r"[ ]+", line.strip(" \n"))
          # print(data)
          all_data[1] = str(float(data[5]) * 8)
        line = rf.readline()
      # print(all_data)
      print("|" + "|".join(all_data[:7]), file = f)
      rf.close()
    print("\n\n\n\n", file = f)
      
  f.close()

def data_run():
  data_path_name_str = time.strftime("%m-%d-%H-%M", time.localtime())
  data_path = os.path.join(init_file_path, data_path_name_str)
  if not os.path.exists(data_path):
    os.makedirs(data_path)
  print(data_path)
  run_test(data_path)

if __name__ == "__main__":
  #for i in range (1, 5):
   # data_run()
    #time.sleep(300)
  get_data()
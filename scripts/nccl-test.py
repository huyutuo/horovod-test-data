# -*- coding: UTF-8 -*-
import os
import matplotlib.pyplot as plt
import sys
import time
import re

init_command = "mpirun -np 4 -H localhost:1,172.26.89.160:1,172.26.89.159:1,172.26.89.158:1 --allow-run-as-root  ./build/all_reduce_perf -g 1  -w 0 -c 0"
init_file_path = "/root/nccl-tests/test-files/"
working_dir = "/root/nccl-tests"

def run_test():
  os.chdir(working_dir)
  command = init_command + " -b 1M -e 1M "
  file_path = init_file_path + "1M"
  command = command + " > " + file_path
  print(command)
  os.system(command)
  print("1M test over")

  for i in range(50, 1001, 50):
    i_str = str(i)
    command = init_command + " -b " + i_str + "M -e " + i_str + "M"
    
    file_path = init_file_path + i_str + "M"
    command = command + " > " + file_path
    print(command)
    os.system(command)
    print(i, "M test over")

def file_cmp(x):
  return int(x[:-1])

def get_data():
  f = open("nccl_test.md", 'wt')
  print("|大小/MB|速率/Gbps|o-algbw|o-busbw|i-algbw|i-busbw|\n|---|---|---|---|---|---|", file=f)
  files = os.listdir(init_file_path)
  files = sorted(files, key=file_cmp)
  for file in files:
    print(file)
    all_data = [""] * 10
    all_data[0] = file[:-1]
    file = os.path.join(init_file_path, file)
    rf = open(file)
    line = rf.readline()
    
    
    while line:
      if line[0] != '#':
        data = re.split(r"[ ]+", line.strip(" \n"))
        all_data[2] = data[5]
        all_data[3] = data[6]
        all_data[4] = data[9]
        all_data[5] = data[10]
        print(data)
      elif line.find("Avg") != -1:
        data = re.split(r"[ ]+", line.strip(" \n"))
        print(data)
        all_data[1] = data[5]
      line = rf.readline()
    print(all_data)
    print("|" + "|".join(all_data[:7]), file = f)
    rf.close()

if __name__ == "__main__":
  #run_test()
  get_data()
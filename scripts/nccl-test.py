# -*- coding: UTF-8 -*-
import os
import matplotlib.pyplot as plt
import sys
import time
import re

mpi_command = "mpirun -np 16 -H localhost:4,172.26.89.160:4,172.26.89.159:4,172.26.89.158:4 --allow-run-as-root "
nccl_command = " ./build/all_reduce_perf -g 1  -w 0 -c 0 -n 10"
init_file_path = "/root/nccl-tests/test-files/"
working_dir = "/root/nccl-tests"
thread_socket = [[1,1], [1,2], [1,4], [2,1], [2,2], [2,4], [4,1], [4,2], [4,4]]
thread_socket_default = [[1,1]]
def run_test(data_path, init_command):
  os.chdir(working_dir)
  command = init_command + " -b 1M -e 1M "
  file_path = os.path.join(data_path, "1M")
  command = command + " > " + file_path
  print(command)
  os.system(command)
  print("1M test over")

  for i in range(10, 101, 10):
    i_str = str(i)
    command = init_command + " -b " + i_str + "M -e " + i_str + "M"
    file_path = os.path.join(data_path, i_str + "M")
    command = command + " > " + file_path
    print(command)
    os.system(command)
    print(i, "M test over")
  
  for i in range(150, 1001, 50):
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

def draw_pic():
  data_paths = os.listdir(init_file_path)
  print(data_paths)
  data_paths.sort()
  fig = plt.figure(figsize=(21, 21))
  count = 1
  for v in thread_socket:
    sub_fig_name = "THREADS_" + str(v[0]) + "-"
    sub_fig_name  += "SOCKETS_" + str(v[1])
    x = [1]
    for i in range(50, 1001, 50):
      x.append(i)
    y_default = []
    y_ring = []
    y_tree = []
    for data_path in data_paths:
      if data_path.find(sub_fig_name) != -1:
        print(data_path)
        tmp_data_path = data_path
        data_path = os.path.join(init_file_path, data_path)
        files = os.listdir(data_path)
        files = sorted(files, key=file_cmp)

        for file in files:
          file = os.path.join(data_path, file)
          rf = open(file)
          line = rf.readline()
          while line:
            if line.find("Avg") != -1:
              data = re.split(r"[ ]+", line.strip(" \n"))
              if tmp_data_path.find("ring") != -1:
                y_ring.append(float(data[5]) * 8)
              elif tmp_data_path.find("tree") != -1:
                y_tree.append(float(data[5]) * 8)
              else:
                y_default.append(float(data[5]) * 8)
            line = rf.readline()
    ax1 = fig.add_subplot(3, 3, count)
    ax1.set_title(sub_fig_name)
    plt.xlabel(u'data size/M')
    plt.ylabel(u'speed/Gbps')
    ax1.plot(x, y_default)
    ax1.plot(x, y_ring)
    ax1.plot(x, y_tree)
    ax1.legend(['default', 'ring', 'tree'], loc='lower right')
    count += 1
          
    plt.savefig("all.png")
  
      
def get_excel():
  f = open("/root/hyt/horovod-test-data/scripts/excel-data.txt", 'wt')
  data_paths = os.listdir(init_file_path)
  print(data_paths)
  data_paths.sort()

  speed = [[] for j in range(3)]
  for data_path in data_paths:
    if data_path.find("THREADS_") != -1:
      print(data_path)
      tmp_data_path = data_path
      data_path = os.path.join(init_file_path, data_path)
      files = os.listdir(data_path)
      files = sorted(files, key=file_cmp)

      tmp = []
      for file in files:
        file = os.path.join(data_path, file)
        print(file)
        rf = open(file)
        line = rf.readline()
        while line:
          if line.find("Avg") != -1:
            data = re.split(r"[ ]+", line.strip(" \n"))
            tmp.append(float(data[5]) * 8)
          line = rf.readline()

      tmp_dict = {}
      tmp_dict[tmp_data_path] = tmp
      if tmp_data_path.find("ring") != -1:
        speed[0].append(tmp)
      elif tmp_data_path.find("tree") != -1:
        speed[1].append(tmp)
      else:
        speed[2].append(tmp)

  print("ring\n", file = f)
  for i in range(len(speed[0][0])):
    for v in speed[0]:
      print(v[i], ",", end='',file = f)
    print("", file = f)
  
  print("tree\n", file = f)
  for i in range(len(speed[0][0])):
    for v in speed[1]:
      print(v[i], ",", end='',file = f)
    print("", file = f)
  
  print("default\n", file = f)
  for i in range(len(speed[0][0])):
    for v in speed[2]:
      print(v[i], ",", end='',file = f)
    print("", file = f)


def data_run():

  
  data_path_name_str = time.strftime("%m-%d-%H-%M", time.localtime())
  #kinds = {"_ring":" -x NCCL_ALGO=Ring ", "_tree":" -x NCCL_ALGO=Tree"}
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
  get_data()
  #draw_pic()
  #get_excel()
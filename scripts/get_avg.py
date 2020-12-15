# -*- coding: UTF-8 -*-
import os
import matplotlib.pyplot as plt
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

index_num = [0, 0.001, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90,
             100, 150, 200, 250, 300, 350, 400, 450, 500]

message = { 
            1 : "(0, 1KB]",
            2 : "(1KB, 1MB]",
            3 : "(1MB, 10MB]",
            4 : "(10MB, 20MB]",
            5 : "(20MB, 30MB]",
            6 : "(30MB, 40MB]",
            7 : "(40MB, 50MB]",
            8 : "(50MB, 60MB]",
            9 : "(60MB, 70MB]",
            10 : "(70MB, 80MB]",
            11 : "(80MB, 90MB]",
            12 : "(90MB, 100MB]",
            13 : "(100MB, 150MB]",
            14 : "(150MB, 200MB]",
            15 : "(200MB, 250MB]",
            16 : "(250MB, 300MB]",
            17 : "(300MB, 350MB]",
            18 : "(350MB, 400MB]",
            19 : "(400MB, 450MB]",
            20 : "(450MB, 500MB]",
            21 : "(500MB, ...)" }



speed_in = [[] for j in range(30)] # 每个阶段所有的传输速率，用来画速率分布图

all_message_fout = open("/Users/huyutuo/Desktop/github/horovod-test-data/all_message.md", 'a')

def get_index(x, p):
  for i in range(len(p)):
    if x <= p[i]:
      return i
  return len(p)

def draw_pic(root_path):
  os.chdir(root_path)
  global speed_in, message
  

  pic_num = 0
  for speed in speed_in:
    if len(speed) > 0 and sum(speed) > 0:
      pic_num += 1
  
  if pic_num == 0:
    return
  fig = plt.figure(figsize=(pic_num * 4, 16))

  now_num = 0
  for index in range(len(speed_in)):
    if len(speed_in[index]) > 0 and sum(speed_in[index]) > 0:
      ax1 = fig.add_subplot(2, (pic_num + 1) / 2, now_num)
      now_num += 1
      #设置标题
      ax1.set_title(message[index])
      #设置X轴标签
      plt.xlabel(u'传输速率/Mbps')
      ax1.get_yaxis().set_visible(False)
      #画散点图
      y = []
      for i in range(len(speed_in[index])):
        y.append(0)
      ax1.scatter(speed_in[index], y, c = 'r')
      #设置图标
  plt.savefig('速率分布.jpg')
  for i in range(len(speed_in)):
      speed_in[i] = []

def get_meaasge(root_path, file_path):
  os.chdir(root_path)
  num = [0] * 30    # 每个阶段出现的次数
  avg = [0.0] * 30  # 每次执行的传输速率
  time = [0] * 30   # 每次执行所用时间
  all_time = 0      # 所有执行所用的时间
  f = open(file_path)
  
  line = f.readline()
  while line:
    if line.find("执行NCCL_ALLREDUCE耗时") != -1 :
      data = line.split(",")
      v = 0
      s = 0.0
      t = 0
      for i in data :
        if i.find("total size:") != -1:
          v = float(i.split(":")[1][:-2])
        elif i.find("avg") != -1:
          s = float(i.split(":")[1].strip("\n")[:-5])
        elif i.find("耗时") != -1:
          tmps = i.replace("执行NCCL_ALLREDUCE耗时","").strip("\n")
          t = float(tmps[:-2])
      index = get_index(v, index_num)
      
      speed_in[index].append(s)
      num[index] += 1
      avg[index] += s
      time[index] += t
      all_time += t
    line = f.readline()
  f.close()

  print all_time
  f = open("README.md", 'wt')
  print >> all_message_fout, file_path.split("/")[-1]
  print >> all_message_fout, "|   |个数|速率|时间|时间占比|\n|---|---|---|---|---|"
  print >> f, "|   |个数|速率/Mbps|时间/s|时间占比|\n|---|---|---|---|---|"
  for i in range(0, 30):
    if num[i] > 0 :
      mtmp = ("|%s|%d|%.2f|%.2f|%.2f%%|" %
             (message[i], num[i], avg[i]/num[i], time[i]*1.0/1000, 100.0*time[i]/all_time))
      print >> f, mtmp
      print >> all_message_fout, mtmp
  print >> f, "\n![](./速率分布.jpg)"
  print >> all_message_fout, "\n\n\n"
  f.close


def get_file_path(root_path):
  #print(root_path)
  dir_or_files = os.listdir(root_path)
  for dir_file in dir_or_files:
    if dir_file == ".git" or dir_file == "scripts":
      continue
    dir_file_path = os.path.join(root_path, dir_file)
    if os.path.isdir(dir_file_path):
        get_file_path(dir_file_path)
    else:
      if dir_file_path.find("rank_0") != -1:
        get_message_and_pic(root_path, dir_file_path)

def get_message_and_pic(root_path, file_path):
  is_solve = False
  dir_or_files = os.listdir(root_path)
  for dir_file in dir_or_files:
      if dir_file.find("速率分布") != -1:
        is_solve = True
        break
  if is_solve == False: 
    print("solve " + file_path)
    get_meaasge(root_path, file_path)
    draw_pic(root_path)

if __name__ == "__main__":
  get_file_path("/Users/huyutuo/Desktop/github/horovod-test-data")
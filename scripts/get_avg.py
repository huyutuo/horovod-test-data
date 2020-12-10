# -*- coding: UTF-8 -*-
import os
import matplotlib.pyplot as plt
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# num[0] respnse大小为4Byte，(这种情况比较特殊，传输时间为0ms, 数据量很小, 不计算此传输速度的平均值)
# num[1] respnse大小为(4Byte, 1KB]
# num[2] respnse大小为(1KB, 1MB]
# num[3] respnse大小为(1MB, 10MB]
# num[4] respnse大小为(10MB, 20MB]
# num[5] respnse大小为(20MB, 30MB]
# num[6] respnse大小为(30MB, 40MB]
# num[7] respnse大小为(40MB, 50MB]
# num[8] respnse大小为(50MB, 60MB]
# num[9] respnse大小为(60MB, 70MB]
# num[10] respnse大小为(70MB, 80MB]
# num[11] respnse大小为(80MB, 90MB]
# num[12】 respnse大小为(90MB, 100MB]
# num[13] respnse大小为(100MB, 150MB]
# num[14] respnse大小为(150MB, 200MB]
# num[15] respnse大小为(200MB, 250MB]
# num[16] respnse大小为(250MB, 300MB]
# num[17] respnse大小为(300MB, 350MB]
# num[18] respnse大小为(350MB, 400MB]
# num[19] respnse大小为(400MB, 450MB]
# num[20] respnse大小为(450MB, 500MB]
# num[21] respnse大小为(500MB, ...)

index_num = [4, 1e3, 1e6, 1e7, 2*1e7, 3*1e7, 4*1e7, 5*1e7, 6*1e7, 7*1e7, 8*1e7, 9*1e7,
             1e8, 1e8+5*1e7, 2e8, 2e8+5*1e7, 3e8, 3e8+5*1e7, 4e8, 4e8+5*1e7, 5e8]

message = { 0 : "4Byte",
            1 : "(4Byte, 1KB]",
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

all_message_fout = open("/Users/huyutuo/Desktop/github/horovod-test-data/all_message.md", 'wt')

def get_index(x, p):
  for i in range(len(p)):
    if x*4 <= p[i]:
      return i
  return len(p)

def draw_pic(root_path):
  os.chdir(root_path)
  fig = plt.figure(figsize=(45, 15))
  global speed_in, message

  pic_num = 0
  for speed in speed_in:
    if len(speed) > 0 and sum(speed) > 0:
      pic_num += 1
  
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
    if line.find("执行ALLREDUCE耗时") != -1 :
      data = line.split(",")
      v = 0
      s = 0.0
      t = 0
      for i in data :
        if i.find("total size:") != -1:
          v = int(i.split(":")[1])
        elif i.find("avg") != -1:
          s = float(i.split(":")[1].split(" ")[0])
        elif i.find("耗时") != -1:
          tmps = i.split(":")[1].strip("\n")
          t = int(tmps[:-2])
      index = get_index(v, index_num)
      speed_in[index].append(s)
      num[index] += 1
      avg[index] += s
      time[index] += t
      all_time += t
    line = f.readline()
  f.close()

  f = open("README.md", 'wt')
  print >> all_message_fout, file_path.split("/")[-1]
  for i in range(0, 21):
    if num[i] > 0 :
      mtmp = ("%s总个数: %d,  速率平均值: %.2fMbps,  时间共: %.2fs, 百分比: %.2f%%" %
             (message[i], num[i], avg[i]/num[i], time[i]*1.0/1000, 100.0*time[i]/all_time))
      print >> f, mtmp
      print >> all_message_fout, mtmp
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
  print(file_path)
  get_meaasge(root_path, file_path)
  draw_pic(root_path)

if __name__ == "__main__":
  get_file_path("/Users/huyutuo/Desktop/github/horovod-test-data")
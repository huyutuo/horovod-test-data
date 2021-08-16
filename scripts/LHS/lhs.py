#coding=utf-8
from os import name
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as pl
import read_config
np.set_printoptions(suppress = True)
class LHSample:
    '''
    :param D : 参数个数
    :param names : 参数名字（list)
    :param bounds : 参数对应范围（list）
    :param N : 拉丁超立方层数
    :return : 样本数据
    '''
    def __init__(self, D, names, bounds, N):
        self.D = D
        self.names = names
        self.bounds = bounds
        self.N = N

    '''
    进行LHS采样
    对于每一个参数采样的范围在[0,1], 然后根据配置文件中的参数范围进行拉伸
    '''
    def getSample(self):
        result = np.empty([self.N, self.D])
        temp = np.empty([self.N])
        d = 1.0 / self.N

        for i in range(self.D):
            for j in range(self.N):
                temp[j] = np.random.uniform(
                    low = j * d, high = (j + 1) * d, size = 1)[0]
            np.random.shuffle(temp)
            for j in range(self.N):
                result[j, i] = temp[j]

        # 对样本数据进行拉伸
        b = np.array(self.bounds)
        lower_bounds = b[:,0]
        upper_bounds = b[:,1]
        if np.any(lower_bounds > upper_bounds):
            print('范围出错')
            return None

        #   sample * (upper_bound - lower_bound) + lower_bound
        np.add(np.multiply(result,
                           (upper_bounds - lower_bounds),
                           out=result),
               lower_bounds,
               out=result)
        return result

def show_pic(samples, bounds, x, y):
  N = len(samples)
  def t(num):
    if bounds[num][1] - bounds[num][0] > 1:
      return 1
    else:
      return 0.1
  xs = t(x)
  ys = t(y)
  print(xs, ys)
  ax = pl.gca()
  pl.ylim(bounds[y][0] - ys, bounds[y][1]+ys)
  pl.xlim(bounds[x][0] - xs, bounds[x][1] + xs)
  pl.grid()
  ax.xaxis.set_major_locator(MultipleLocator(xs))
  ax.yaxis.set_major_locator(MultipleLocator(ys))
  XY = np.array(samples)
  X = XY[:,x]
  Y = XY[:,y]
  pl.scatter(X,Y)
  pl.show()

if __name__ =='__main__':
  filename = "parameter_config.json"
  parameter_count, names, bounds, layers = read_config.get_config(filename)
  lhs = LHSample(parameter_count, names, bounds, layers)
  samples = lhs.getSample()
  samples = np.round(samples, decimals = 2)
  print(samples)
  read_config.out_to_config_file(samples.tolist())
  # show_pic(samples, bounds, 0, 1)
  # show_pic(samples, bounds, 0, 2)
  # show_pic(samples, bounds, 0, 3)
from math import exp, sin, pi
import numpy as np

class SignalGenerator:
    def __init__(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max
        self.step = 0.01
        self.gaussA = 1
    
    def generateRect(self, L):
        xs = np.arange(self.x_min, self.x_max+self.step, self.step)
        ys = np.where(np.abs(xs) <= L, 1.0, 0.0)
        return xs, ys
    
    def generateDiscretRect(self, L, dx):
        xs = np.arange(self.x_min, self.x_max + dx, dx)
        ys = np.where(np.abs(xs) <= L, 1.0, 0.0)
        return xs, ys
    
    # def sinc(self, x:float):
    #     if np.abs(x)<=1e-5:
    #         return 1
    #     return np.sin(x)/x
    
    def generateReconstructed(self, discret_x, discrete_y, signal_x, dx):
        t = (np.pi / dx) * (signal_x[:, np.newaxis] - discret_x[np.newaxis, :])
        with np.errstate(divide='ignore', invalid='ignore'):
            sinc_vals = np.sin(t) / t
            sinc_vals[np.isnan(sinc_vals)] = 1.0
        ys = sinc_vals @ discrete_y
        # ys = [0.]*len(signal_x)
        # for i in range(len(signal_x)):
        #     for k in range(len(discret_x)):
        #         ys[i]+= discrete_y[k]*self.sinc((pi/dx)*(signal_x[i]-discret_x[k]))
        return ys

    def generateGauss(self, sigma):
        xs = np.arange(self.x_min, self.x_max + self.step, self.step)
        ys = self.gaussA * np.exp(-(xs ** 2) / (sigma ** 2))
        return xs, ys
    
    def generateDiscretGauss(self, sigma, dx):
        xs = np.arange(self.x_min, self.x_max + dx, dx)
        ys = self.gaussA * np.exp(-(xs ** 2) / (sigma ** 2))
        return xs, ys

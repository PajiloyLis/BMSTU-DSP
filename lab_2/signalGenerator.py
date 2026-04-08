from math import exp, sin, pi
import numpy as np
import timeit


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

    @staticmethod
    def dft(discret_y, dx):
        start = timeit.default_timer()
        n = len(discret_y)
        v = np.zeros(n, dtype=complex)
        for k in range(n):
            v[k]=0.0+0.0j
            for i in range(n):
                phi = -2*np.pi * i * k/n
                v[k]+=discret_y[i] *(np.cos(phi)-np.sin(phi)*1.0j)
        stop = timeit.default_timer()
        return np.fft.fftshift(np.fft.fftfreq(len(discret_y), dx)), np.fft.fftshift(np.abs(v)), stop-start

    @staticmethod
    def removeTwinsTransform(discrete_x, discrete_y):
        n = len(discrete_y)
        return discrete_y * np.array([-1**x for x in discrete_x])
    
    @staticmethod
    def fft(discrete_y, dx):
        start = timeit.default_timer()
        v = np.fft.fft(discrete_y)
        stop = timeit.default_timer()
        return np.fft.fftshift(np.fft.fftfreq(len(discrete_y), dx)), np.fft.fftshift(np.abs(v)), stop-start
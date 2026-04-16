from math import exp, sin, pi
import numpy as np
import timeit
from enum import Enum

class NoiseType(Enum):
    IMPULSE = 1
    GAUSS = 2
    
class FrequencyType(Enum):
    HIGH = 1
    LOW = 2

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
    
    def frequenceConvolution(self, y1, y2, dx):
        len_y1, len_y2 = len(y1), len(y2)
        len_conv = len_y1+len_y2-1
        len_fft = 1<<(len_conv-1).bit_length()
        extended_y1 = np.zeros(len_fft, dtype=float)
        extended_y2 = np.zeros(len_fft, dtype=float)
        extended_y1[:len_y1]=y1
        extended_y2[:len_y2]=y2
        fft_y1 = np.fft.fft(extended_y1)
        fft_y2 = np.fft.fft(extended_y2)
        
        conv_fft = fft_y1 * fft_y2
        
        conv = np.fft.ifft(conv_fft)
        conv_real=np.real(conv[:len_conv])
        return np.arange(len_conv)*dx+self.x_min*2, conv_real
        
    @staticmethod
    def generateImpulseNoise(y, amp_ratio=0.5):
        max_val = np.max(y)
        y_count = len(y)
        noise_cnt = np.random.randint(1, y_count//10)
        noise_positions = np.random.choice(y_count, noise_cnt, False)
        noise_amps = np.random.uniform(0, amp_ratio*max_val, noise_cnt)
        noise = np.zeros(y_count, dtype=float)
        noise[noise_positions]=noise_amps*np.sign(np.random.randn(noise_cnt))
        return noise
    
    @staticmethod
    def generateGaussNoise(y, dx, sigma_f_rel):
        len_y = len(y)
        freq = np.fft.fftfreq(len_y, d = dx)
        sigma_f = sigma_f_rel/(2.0*dx)
        h = np.exp(-freq**2 / (2*sigma_f**2))
        theta = np.random.uniform(-0.5, 0.5, len_y)
        noise = np.fft.fft(theta*h)/np.sqrt(len_y)
        noise_real = np.real(noise)
        return noise_real
    
    @staticmethod
    def applyNoise(y, noise_y):
        return y+ noise_y
    
    @staticmethod
    def applyButterworth(y, dx, cutoff, freq_type):
        len_y = len(y)
        B = cutoff * 1.0/(2.0*dx)
        freq = np.fft.fftfreq(len_y, d = dx)
        if freq_type == FrequencyType.HIGH:
            with np.errstate(divide='ignore', invalid='ignore'):
                H = 1/ (1+(B/freq)**4)
                H[freq==0]=0
        else:
            H = 1/ (1+(freq/B)**4)

        spectrum = np.fft.fft(y)
        filtered_spectrum = spectrum*H
        filtered_y = np.fft.ifft(filtered_spectrum).real
        return filtered_y
    
    @staticmethod
    def applyGauss(y, dx, sigma_filter_rel, freq_type):
        len_y = len(y)
        sigma_filter = sigma_filter_rel/(2.0*dx)
        freq = np.fft.fftfreq(len_y, d = dx)
        if freq_type == FrequencyType.HIGH:
            H = 1-np.exp(-freq**2/sigma_filter**2)
        else:
            H = np.exp(-freq**2/sigma_filter**2)

        spectrum = np.fft.fft(y)
        filtered_spectrum = spectrum*H
        filtered_y = np.fft.ifft(filtered_spectrum).real
        return filtered_y
    
    @staticmethod
    def applyWeiner(y, dx, noise_y):
        spectrum_y = np.fft.fft(y)
        spectrum_noise_y = np.fft.fft(noise_y)
        abs_spectrum_y = np.abs(spectrum_y)
        abs_spectrum_noise_y = np.abs(spectrum_noise_y)
        h = 1-abs_spectrum_noise_y**2/(abs_spectrum_y**2+1e-6)
        h = np.clip(h, 0, 1) 
        filtered = np.fft.ifft(spectrum_y * h).real
        return filtered
        
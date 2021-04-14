#!/usr/bin/python
# -*- coding=utf-8 -*-
import numpy as np
#version 1.0.0.20190604


class HREstimator:
    def __init__(self, HRmax, HRrest, age, weight, criticalSPD):

        if HRmax == -1:
            self.hr_max = 208 - (0.7 * age)
        else:
            self.hr_max = HRmax
        self.hr_min = HRrest
        self.age = age
        self.weight = weight

        self.critical_spd = criticalSPD

        self.hr_M_max = 0.2
        self.hr_L_max = 0.5
        self.hr_G_max = 0.5

        self.hr_L = 0.1
        self.hr_G = 0.1
        self.hr_M = 0.

        self.tau_L = 120 #180
        self.tau_P = 97.1 # 97.1
        self.tau_R = 38.5 # 38.5
        self.tau_M = 1200 #1500

        self.G = 0
        self.D = 0
        self.M = 0
        self.G_0 = 0.15 #0.25
        self.M_0 = 0.6

        self.p_0 = 0.0025
        self.r_0 = 0.17
        self.p_t = 0.8 # threshold 0.8

        self.alpha = 0.3
        self.alpha_L = 0.15
        self.alpha_G = 0.82 #0.82
        self.alpha_M = 0.12

        self.beta = 2

    def power_normalization(self, power, incline):
        cp_coef = 1
        if incline > 0.05:
            cp_coef = 1.5
        elif incline < -0.05:
            cp_coef = 1.8
        else:
            if self.critical_spd > 14:
                cp_coef = 1.3
            else:
                cp_coef = 1.4

        # return power / (cp_coef * (self.critical_spd * self.weight) / 3.6)
        # return power/(1.7 * self.critical_spd)
        if power <= 6:
            power_c = 1
        else:
            power_c = 1.

        return power_c * power / (1.7 * self.critical_spd)

    def LGmax_update(self, hr_m):
            self.hr_G_max = 0.5 - (hr_m-0.05)/2
            self.hr_L_max = 0.5 - (hr_m-0.05)/2

    def hr_L_estimator(self, power):
        self.D = self.hr_L_steady(power)
        self.hr_L = ((self.D - self.hr_L) / self.tau_L) + self.hr_L

    def hr_L_steady(self, power):
        D = self.hr_L_max * 2 * ((1 / (1 + np.exp(-power / self.alpha_L))) - 0.5) # - 0.5
        return D

    def hr_G_estimator(self, power):
        self.G = self.G_function(power)
        if self.G >= self.G_0:
            self.hr_G = self.hr_G_max * (1 - np.exp(-(self.G - self.G_0)/self.alpha_G))
        else:
            self.hr_G = 0.
        return self.hr_G

    def G_function(self, power):
        G_production = (np.exp(power/self.p_t) - 1)
        G_removal = (self.r_0 + (1 - np.exp(-power/self.p_t))) * (1 - np.exp(-self.G/self.alpha))

        G = self.p_0 + (G_production / self.tau_P) - (G_removal / self.tau_R) + self.G

        return G

    def hr_M_estimator(self, power):
        self.M = self.M_function(power)
        self.hr_M = self.hr_M_max * (1 / (1 + np.exp(- (self.M - self.M_0) / self.alpha_M)))

    def M_function(self, power):
        M = (((self.beta * power) - self.M) / self.tau_M) + self.M
        return M

    def hr_est(self, power, incline):

        nor_power = self.power_normalization(power, incline)

        self.hr_M_estimator(nor_power)
        self.LGmax_update(self.hr_M)

        self.hr_L_estimator(nor_power)
        self.hr_G_estimator(nor_power)

        self.hr = ((self.hr_L + self.hr_G + self.hr_M) * (self.hr_max - self.hr_min)) + (1.2 * self.hr_min)

        # return self.hr_L*(self.hr_max - self.hr_min)
        # return self.hr_G * (self.hr_max - self.hr_min)
        # return self.hr_M * (self.hr_max - self.hr_min)
        return self.hr

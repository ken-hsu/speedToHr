import numpy as np


class HREstimator:
    def __init__(self, hr_max, hr_min):
        self.hr = 0.
        self.hr_max = hr_max
        self.hr_min = hr_min

        self.hr_M_max = 0.2
        self.hr_L_max = 0.5
        self.hr_G_max = 0.5

        self.hr_L = 0.1
        self.hr_G = 0.1
        self.hr_M = 0.

        self.tau_L = 180
        self.tau_P = 97.1 # 97.1
        self.tau_R = 38.5 # 38.5
        self.tau_M = 1500

        self.G = 0
        self.D = 0
        self.M = 0
        self.G_0 = 0.25
        self.M_0 = 0.6

        self.p_0 = 0.0025
        self.r_0 = 0.17
        self.p_t = 0.8 # threshold 0.8

        self.alpha = 0.3
        self.alpha_L = 0.15
        self.alpha_G = 0.82 #0.82
        self.alpha_M = 0.12

        self.beta = 2

    def setHR(self, HRmax, HRrest):
        self.hr_max = HRmax
        self.hr_min = HRrest

    def LGmax_update(self, hr_m):
            self.hr_G_max = 0.5 - (hr_m-0.05)/2
            self.hr_L_max = 0.5 - (hr_m-0.05)/2

    def hr_L_estimator(self, speed):
        self.D = self.hr_L_steady(speed)
        self.hr_L = ((self.D - self.hr_L) / self.tau_L) + self.hr_L

    def hr_L_steady(self, speed):
        D = self.hr_L_max * 2 * ((1 / (1 + np.exp(-speed / self.alpha_L))) - 0.5) # - 0.5
        return D

    def hr_G_estimator(self, speed):
        self.G = self.G_function(speed)
        if self.G >= self.G_0:
            self.hr_G = self.hr_G_max * (1 - np.exp(-(self.G - self.G_0)/self.alpha_G))
        else:
            self.hr_G = 0.
        return self.hr_G

    def G_function(self, speed):
        G_production = (np.exp(speed/self.p_t) - 1)
        G_removal = (self.r_0 + (1 - np.exp(-speed/self.p_t))) * (1 - np.exp(-self.G/self.alpha))

        G = self.p_0 + (G_production / self.tau_P) - (G_removal / self.tau_R) + self.G

        return G

    def hr_M_estimator(self, speed):
        self.M = self.M_function(speed)
        self.hr_M = self.hr_M_max * (1 / (1 + np.exp(- (self.M - self.M_0) / self.alpha_M)))

    def M_function(self, speed):
        M = (((self.beta * speed) - self.M) / self.tau_M) + self.M
        return M

    def hr_est(self, power):
        self.hr_M_estimator(power)
        self.LGmax_update(self.hr_M)

        self.hr_L_estimator(power)
        self.hr_G_estimator(power)

        self.hr = ((self.hr_L + self.hr_G + self.hr_M) * (self.hr_max - self.hr_min)) + self.hr_min

        # return self.hr_L*(self.hr_max - self.hr_min)
        # return self.hr_G * (self.hr_max - self.hr_min)
        # return self.hr_M * (self.hr_max - self.hr_min)
        return self.hr

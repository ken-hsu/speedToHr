import numpy as np
import zipfile, os, json, glob
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import hr_estimator


def gogogo(hr, spd_list, cspd, hr_rest, weight, age):

    tmp_v = -100
    tmp_idx = max(hr)
    for hr_max_try in range(190, 210):

        hr_estor = hr_estimator.HREstimator(hr_max_try, hr_rest, age, weight, cspd)
        est_hr = []
        for spd in spd_list:
            hr_t = hr_estor.hr_est(spd, 0.)
            est_hr.append(hr_t)
        r2s = r2_score(hr[60 * 26:len(hr)], est_hr[60 * 26:len(est_hr)])

        if r2s > tmp_v:
            tmp_v = r2s
            tmp_idx = hr_max_try

    hr_estor = hr_estimator.HREstimator(tmp_idx, hr_rest, age, weight, cspd)
    est_hr = []
    for spd in spd_list:
        hr_t = hr_estor.hr_est(spd, 0.)
        est_hr.append(hr_t)

    print(cspd, tmp_idx, tmp_v)
    # plt.plot(hr, 'b', est_hr, 'r')
    # plt.show()

    # if tmp_v >= 0.9:
        # print(cspd, tmp_idx, tmp_v)
        # plt.plot(hr, 'b', est_hr, 'r')
        # plt.show()
    return tmp_idx, tmp_v


with open("Pnoe_20200824_1407-Murphy_MurphyChen_6met.txt", 'r') as tf:
    heartrate = []
    time = []
    for line in tf:
        heartrate.append(float(line.split(',')[0]))
        time.append(int(line.split(',')[1].split('\n')[0]))

    hr_ = []
    spd_ = []
    for tn in range(1, len(time)):
        td = time[tn] - time[tn - 1]
        hd = (heartrate[tn] - heartrate[tn - 1]) / float(td)
        hr_tmp = heartrate[tn - 1]
        for n in range(td):
            hr_.append(hr_tmp + (n * hd))

    # for n in range(len(hr_)):
    #     if n <= 6 * 60:
    #         spd_.append(0.)
    #     elif 6 * 60 < n <= 18 * 60:
    #         spd_.append(4.)
    #     elif 18 * 60 < n <= 23 * 60:
    #         spd_.append(0.)
    #     elif 23 * 60 < n <= 34 * 60:
    #         spd_.append(8.)
    #     else:
    #         spd_.append(0.)

    for n in range(len(hr_)):
        if n <= 5 * 60:
            spd_.append(0.)
        elif 5 * 60 < n <= 10 * 60:
            spd_.append(4.)
        elif 10 * 60 < n <= 15 * 60:
            spd_.append(0.)
        elif 15 * 60 < n <= 20 * 60:
            spd_.append(6.)
        elif 20 * 60 < n <= 25 * 60:
            spd_.append(0.)
        elif 25 * 60 < n <= 30 * 60:
            spd_.append(7.)
        elif 30 * 60 < n <= 45 * 60:
            spd_.append(0.)
        elif 45 * 60 < n <= 50 * 60:
            spd_.append(8.)
        elif 50 * 60 < n <= 65 * 60:
            spd_.append(0.)
        elif 65 * 60 < n <= 70 * 60:
            spd_.append(9.)
        else:
            spd_.append(0.)

    for cs in range(60, 140, 2):
        mh, r2 = gogogo(hr_, spd_, cs/10, 54, 73, 31)
        # if r2 > 0.9:
        #     print(mh, cs, r2)

    print(1)
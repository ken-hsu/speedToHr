import numpy as np
import zipfile, os, json, glob
import matplotlib.pyplot as plt
import scipy.signal as scisgn
from sklearn.metrics import r2_score
import hr_estimator, hr_estimator_cyc
import time
import os
import pandas as pd


def estMaxHR(speed_list, hr_list, criticalSPD, hr_rest, age, weight, maxHR_age, name):

    tmp_v = 99999.0
    tmp_idx = max(hr_list)

    nIteration = 30
    left = int(max(hr_list))
    right = 260
    for iteration in range(nIteration):
        mRight = (left + 2*right) // 3
        mLeft = (2*left + right) // 3

        hr_estor = hr_estimator.HREstimator(mLeft, hr_rest, age, weight, criticalSPD)
        est_hr = []
        for i in range(len(speed_list)):
            hr_t = hr_estor.hr_est(speed_list[i], 0.)
            est_hr.append(hr_t)
        left_MAE = np.mean([abs(hr_list[i] - est_hr[i]) for i in range(len(hr_list))])

        hr_estor = hr_estimator.HREstimator(mRight, hr_rest, age, weight, criticalSPD)
        est_hr = []
        for i in range(len(speed_list)):
            hr_t = hr_estor.hr_est(speed_list[i], 0.)
            est_hr.append(hr_t)
        right_MAE = np.mean([abs(hr_list[i] - est_hr[i]) for i in range(len(hr_list))])

        if mRight - mLeft == 1:
            if right_MAE > left_MAE:
                tmp_idx = mLeft
                tmp_v = left_MAE
            else:
                tmp_idx = mRight
                tmp_v = right_MAE
            break

        if left_MAE < right_MAE:
            right = mRight
            tmp_idx = mLeft
            tmp_v = left_MAE
        else:
            left = mLeft
            tmp_idx = mRight
            tmp_v = right_MAE

    # tmp_idx = left
    # tmp_v = left_MAE
    # print(iteration)

    hr_estor = hr_estimator.HREstimator(tmp_idx, hr_rest, age, weight, criticalSPD)
    est_hr = []
    for p in speed_list:
        hr_t = hr_estor.hr_est(p, 0.)
        est_hr.append(hr_t)

    hr_estor = hr_estimator.HREstimator(maxHR_age, hr_rest, age, weight, criticalSPD)
    age_hr = []
    for p in speed_list:
        hr_t = hr_estor.hr_est(p, 0.)
        age_hr.append(hr_t)

    # print(tmp_idx)

    fig, ax1 = plt.subplots()
    plt.xlabel('time (s)')
    ax2 = ax1.twinx()
    ax1.set_ylabel('HR (bpm)', color='b')
    ax1.plot(hr_list, 'b', label="real HR")
    ax1.plot(est_hr, 'r', label = "est. HR")
    ax1.plot(age_hr, 'g', label = "est. HR (age formula)")
    ax1.tick_params(axis='y', labelcolor='b')
    ax2.set_ylabel('speed (kph)', color='brown')
    ax2.plot(speed_list, color='silver', label="speed")
    ax2.tick_params(axis='y', labelcolor='brown')
    fig.tight_layout()
    ax1.legend()
    ax2.legend(bbox_to_anchor=(1, 0.1))
    # plt.show()
    plt.savefig("vo2max_data/HR_fig_full/" + name + ".png")
    plt.close()
    return tmp_idx, tmp_v


if __name__ == "__main__":
    max_HR_list = []
    weight = 60

    name_list = os.listdir("outdoor_data/")
    user_profile = pd.read_excel("user_profile.xlsx")
    user_profile = user_profile[user_profile['Name'].notna()]
    user_profile['Name'] = user_profile['Name'].apply(lambda x: '_'.join(x.lower().split(' ')))


    # filename = 'mingchia_yeh.csv'
    # workout = pd.read_csv('vo2max_data/csv/' + filename)
    # name = filename.split('.')[0]
    # speed_list = workout['speed'].values.tolist()
    # hr_list = workout['hr'].values.tolist()
    # criticalSPD = user_profile[user_profile['Name'] == name]['critical speed'].values[0]
    # hr_rest = user_profile[user_profile['Name'] == name]['HR rest'].values[0]
    # age = user_profile[user_profile['Name'] == name]['age'].values[0]
    # maxHR_age = user_profile[user_profile['Name'] == name]['formula using age'].values[0]
    # maxHR, MAE = estMaxHR(speed_list, hr_list, criticalSPD, hr_rest, age, weight, maxHR_age, name)
    # print(name, ":", maxHR)


    file_list = os.listdir('vo2max_data/csv')
    for filename in file_list:
        workout = pd.read_csv('vo2max_data/csv/' + filename)
        name = filename.split('.')[0]
        speed_list = workout['speed'].values.tolist()
        hr_list = workout['hr'].values.tolist()
        criticalSPD = user_profile[user_profile['Name'] == name]['critical speed'].values[0]
        hr_rest = user_profile[user_profile['Name'] == name]['HR rest'].values[0]
        age = user_profile[user_profile['Name'] == name]['age'].values[0]
        maxHR_age = user_profile[user_profile['Name'] == name]['formula using age'].values[0]
        maxHR, MAE = estMaxHR(speed_list, hr_list, criticalSPD, hr_rest, age, weight, maxHR_age, name)
        print(name, ":", maxHR)
        
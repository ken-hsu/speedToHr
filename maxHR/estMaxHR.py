import numpy as np
import zipfile, os, json, glob
import matplotlib.pyplot as plt
import scipy.signal as scisgn
from sklearn.metrics import r2_score
import hr_estimator, hr_estimator_cyc
import time
import os
import pandas as pd


def estMaxHR(zip_n, criticalSPD, hr_rest, age, weight, maxHR_age, name, index):
    hr1 = []
    speed = []

    zip_name = zip_n
    with zipfile.ZipFile(zip_name, 'r') as zf:
        open("file_data", 'wb').write(zf.read("file_data"))
        with open("file_data") as ff:
            dd = json.load(ff)
            for d in dd:
                speed.append(float(d["sp"])*3.6)
                hr1.append(float(d["hr"]))

        os.remove("file_data")

    # alpha = 0.87
    # hr = [hr1[0]]
    # for n in range(1, len(hr1)):
    #     hr.append(alpha * hr[-1] + (1 - alpha) * hr1[n])

    hr = hr1
    # print("length of hr:", len(hr))

    tmp_v = 99999.0
    tmp_idx = max(hr)
    # for hr_max_try in range(int(max(hr)), 220):
    #     hr_estor = hr_estimator.HREstimator(hr_max_try, hr_rest, age, weight, criticalSPD)
    #     est_hr = []
    #     for i in range(len(speed)):
    #         hr_t = hr_estor.hr_est(speed[i], 0.)
    #         est_hr.append(hr_t)
    #     MAE = np.mean([abs(hr[i] - est_hr[i]) for i in range(len(est_hr))])
    #     if MAE < tmp_v:
    #         tmp_v = MAE
    #         tmp_idx = hr_max_try
    nIteration = 30
    left = int(max(hr))
    right = 260
    for iteration in range(nIteration):
        mRight = (left + 2*right) // 3
        mLeft = (2*left + right) // 3

        hr_estor = hr_estimator.HREstimator(mLeft, hr_rest, age, weight, criticalSPD)
        est_hr = []
        for i in range(len(speed)):
            hr_t = hr_estor.hr_est(speed[i], 0.)
            est_hr.append(hr_t)
        left_MAE = np.mean([abs(hr[i] - est_hr[i]) for i in range(300, len(hr))])

        hr_estor = hr_estimator.HREstimator(mRight, hr_rest, age, weight, criticalSPD)
        est_hr = []
        for i in range(len(speed)):
            hr_t = hr_estor.hr_est(speed[i], 0.)
            est_hr.append(hr_t)
        right_MAE = np.mean([abs(hr[i] - est_hr[i]) for i in range(300, len(hr))])

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
    for p in speed:
        hr_t = hr_estor.hr_est(p, 0.)
        est_hr.append(hr_t)

    hr_estor = hr_estimator.HREstimator(maxHR_age, hr_rest, age, weight, criticalSPD)
    age_hr = []
    for p in speed:
        hr_t = hr_estor.hr_est(p, 0.)
        age_hr.append(hr_t)

    # print(tmp_idx)

    # fig, ax1 = plt.subplots()
    # plt.xlabel('time (s)')
    # ax2 = ax1.twinx()
    # ax1.set_ylabel('HR (bpm)', color='b')
    # ax1.plot(hr, 'b', label="real HR")
    # ax1.plot(est_hr, 'r', label = "est. HR")
    # ax1.plot(age_hr, 'g', label = "est. HR (age formula)")
    # ax1.tick_params(axis='y', labelcolor='b')
    # ax2.set_ylabel('speed (kph)', color='brown')
    # ax2.plot(speed, color='silver', label="speed")
    # ax2.tick_params(axis='y', labelcolor='brown')
    # fig.tight_layout()
    # ax1.legend()
    # ax2.legend(bbox_to_anchor=(1, 0.1))
    # # plt.show()
    # plt.savefig("latest_outdoor_fig/" + name + "_" + str(index) + ".png")
    # plt.close()
    return tmp_idx, tmp_v


if __name__ == "__main__":
    max_HR_list = []
    weight = 60
    time_start = time.time()

    name_list = os.listdir("outdoor_data/")
    user_profile = pd.read_excel("user_profile.xlsx")
    user_profile = user_profile[user_profile['Name'].notna()]
    user_profile['Name'] = user_profile['Name'].apply(lambda x: '_'.join(x.lower().split(' ')))

    # name = 'lance_lee'
    # age = int(user_profile.loc[user_profile['Name'] == name]['age'].values[0])
    # hr_rest = int(user_profile.loc[user_profile['Name'] == name]['HR rest'].values[0])
    # maxHR_age = user_profile.loc[user_profile['Name'] == name]['formula using age'].values[0]
    # for d in glob.glob("data/" + name + "/*.zip"):
    #     criticalSPD = float(os.path.basename(d).split('_')[-1].split('.')[0]) / 100
    #     m, r = estMaxHR(d, criticalSPD, hr_rest, age, weight, maxHR_age)
    #     max_HR_list.append(m)
    #     print(m, r)

    for name in name_list:
        age = int(user_profile.loc[user_profile['Name'] == name]['age'].values[0])
        hr_rest = int(user_profile.loc[user_profile['Name'] == name]['HR rest'].values[0])
        maxHR_age = user_profile.loc[user_profile['Name'] == name]['formula using age'].values[0]
        index = 0
        print(name + ': ', end='')
        for d in glob.glob("outdoor_data/" + name + "/*.zip"):
            criticalSPD = float(os.path.basename(d).split('_')[-1].split('.')[0]) / 100
            m, r = estMaxHR(d, criticalSPD, hr_rest, age, weight, maxHR_age, name, index)
            max_HR_list.append(m)
            index += 1
            print(m, r)
        # print(max_HR_list, end = '   ')
        # print(np.mean(max_HR_list))
        max_HR_list = []

    time_end = time.time()
    time_c= time_end - time_start
    print('time cost', time_c, 's')  # ~0.8s

    # x_axis = range(220-len(output), 220)
    # plt.plot(x_axis, output)
    # plt.show()
    # print(np.mean(max_HR_list))

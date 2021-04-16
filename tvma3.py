import json
import os
import fnmatch
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math

## read data object
class Data:
    def __init__(self):
        self.workouts = []
        self.users = []

    def findFile(self,rootdir):
        fileList = os.listdir(rootdir)
        fldFileList = fnmatch.filter(fileList, '*.user.json')
        for i in range(len(fldFileList)):
            fldFileList[i] = fldFileList[i][0:-10]
        return fldFileList


    def findData(self,rootdir,fileName):
        with open(rootdir+"extf/"+fileName+".xx","r") as reader:
            self.workouts.append(json.loads(reader.read()))
        with open(rootdir+fileName+".user.json","r") as reader:
            self.users.append(json.loads(reader.read()))

## collect the data
#rootdir = "/Users/dy/git/data/jsonload/select/"
rootdir = "/Users/dy/git/data/jsonload/select/"
data = Data()
fileNamelist = data.findFile(rootdir)
for i in range(1):
    data.findData(rootdir,fileNamelist[i])

## select the data
i = 0
hr = np.zeros([len(data.workouts[i]),1])
sp = np.zeros([len(data.workouts[i]),1])

for j in range(len(data.workouts[i])):
    hr[j] = data.workouts[i][j]['hr']
    sp[j] = data.workouts[i][j]['sp']

startIndex = 0
endIndex = -1
#fig, ax1 = plt.subplots()
#ax1.plot(range(hr[startIndex:endIndex,:].shape[0]),hr[startIndex:endIndex,:],color='red',label='hr')
#ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
#ax2.plot(range(sp[startIndex:endIndex,:].shape[0]),sp[startIndex:endIndex,:],color='blue',label='speed')
#fig.legend()
#plt.show()

## cut the data (sp to sp2)
startIndex = 0
endIndex = 4000
dataAmount = endIndex - startIndex
sp2 = np.zeros([dataAmount,1])
sp2 = sp[startIndex:endIndex,0]
hr_ref = np.zeros([dataAmount,1])
hr_est = np.zeros([dataAmount,1])
markers = np.zeros([dataAmount,1])
#print(sp2.shape[0])

nGridx = 25
nGridy = 10
N = sp2.shape[0]
n1db2 = 7
n1 = 2*n1db2-1 #1*nGridx
n2 = 0 #1*nGridx
n3 = 37
n=n1+n2+n3
param001 = 0.000000000001 #Q_kkn1[j]
param002 = 0.001  #S_k
param003 = 100 #R_k
#param004 = 0.0001 #Phi_k[n1db2 + i]
param004 = 0.00000000000000001  #Phi_k[n1db2 + i]

theta_kk = np.zeros([n1, 1])
theta_kkn1 = np.zeros([n1, 1])
Phi_k = np.zeros([n1,1])
Q_kkn1 = np.identity(n1)
for j in range(0, int(n1)): Q_kkn1[j] = param001
S_k = np.identity(1)*param002
R_k = np.identity(int(n1))*param003
K_k = np.zeros([1,1])
r_k = np.zeros([1,1])
y_k = np.zeros([1,1])
print(r_k)
#a = np.array([[ 5, 1 ,3], [ 1, 1 ,1], [ 1, 2 ,1]])
#b = np.array([1, 2, 3])
#print(a)
#print(b)

for idx in range(0, N, 1):
    hr_ref[idx] = -1
    hr_est[idx] = -1
    markers[idx] = -100
    #print(markers[idx], "\n")

sumErrTP2=0
idxLastUpdate = -1

for idx in range(n, int(N-n2), 1):

    for i in range(0, int(n1db2)): Phi_k[i] = sp2[idx - n2 - i - 1]
    #for i in range(0, int(n1db2)-1): Phi_k[n1db2+i] = -1*np.exp(0.01*(Phi_k[0]-Phi_k[i+1])/(i+1))
    #for i in range(0, int(n1db2) - 1): Phi_k[n1db2 + i] = -1 * np.exp(param004 * (Phi_k[0] - Phi_k[i + 1]) / (i + 1))
    for i in range(0, int(n1db2) - 1): Phi_k[n1db2 + i] = -1 * np.exp(param004 * (Phi_k[i] - Phi_k[i + 1]))
    Phi_k_t = np.transpose(Phi_k)
    y_k[0] = hr[idx]

    if (idx%n) == 0:

        Q_kkn1_Phi_k = np.matmul(Q_kkn1,Phi_k)
        Mat1 = S_k+np.matmul(Phi_k_t, Q_kkn1_Phi_k)
        Mat3 = np.linalg.inv(Mat1)
        K_k = np.matmul(Q_kkn1_Phi_k, Mat3)
        r_k = y_k - np.matmul(Phi_k_t,theta_kkn1)
        theta_kk = theta_kkn1+np.matmul(K_k,r_k)
        theta_kkn1 = theta_kk
        Mat2 = np.identity(n1)-np.matmul(K_k, Phi_k_t)
        Q_kk = np.matmul(Mat2, Q_kkn1)
        Q_kkn1 = Q_kk + R_k
        #print("theta\n", theta_kkn1, "\n")
        #print("y_k\t", y_k, "estimated y_k", np.matmul(Phi_k_t, theta_kkn1), "\n")
        y_k_hat = y_k
        markers[idx] = y_k
    else:
        y_k_hat = np.matmul(Phi_k_t, theta_kk)
        #print(y_k, y_k_hat)

    #print("the marker at", idx, ":\t", markers[idx], "\n")

    hr_ref[idx] = y_k[0]
    hr_est[idx] = y_k_hat[0]
    err = hr_ref[idx]-hr_est[idx]
    sumErrTP2 = sumErrTP2+pow(err,2)

    #print(hr_ref[idx], hr_est[idx])

rmsd = math.sqrt(sumErrTP2/N)
#print("rmsd = \t", rmsd, "\n")

fig = plt.figure()
ax = fig.add_subplot(2, 1, 1)

#plt.plot(range(hr[startIndex:endIndex,:].shape[0]),hr_ref[startIndex:endIndex,:],
#         range(hr_est[startIndex:endIndex,:].shape[0]),hr_est[startIndex:endIndex,:], )
#ax.plot(range(hr[startIndex:endIndex,:].shape[0]),hr_ref[startIndex:endIndex,:],
#         range(hr_est[startIndex:endIndex,:].shape[0]),hr_est[startIndex:endIndex,:], )
ax.plot(range(hr[startIndex:endIndex,:].shape[0]),hr_ref[startIndex:endIndex,:])
ax.plot(range(hr_est[startIndex:endIndex,:].shape[0]),hr_est[startIndex:endIndex,:])
ax.plot(range(markers[startIndex:endIndex,:].shape[0]),markers[startIndex:endIndex,:], "rx")
ax.legend(['reference', 'estimation'])

ax2 = fig.add_subplot(2,1,2)
ax2.plot(range(sp2[startIndex:endIndex].shape[0]),sp2[startIndex:endIndex],'r')

x_major_ticks = np.arange(0, 4100, 200)
x_minor_ticks = np.arange(0, 4100, 25)
y_major_ticks = np.arange(-0.5, 180, 20)
y_minor_ticks = np.arange(-0.5, 180, 5)
y2_major_ticks = np.arange(-0.5,3.0,0.5)

ax.set_xlim([0, 4100])
ax.set_ylim([-0.5, 180])
ax2.set_xlim([0, 4100])
ax2.set_ylim([-0.5, 3.5])

ax.set_xticks(x_major_ticks)
ax.set_xticks(x_minor_ticks, minor=True)
ax.set_yticks(y_major_ticks)
ax.set_yticks(y_minor_ticks, minor=True)
ax2.set_yticks(y2_major_ticks)

ax.grid(True, which='both')

ax.grid(b=True, which='major', linestyle='-', alpha=0.5)
ax.grid(b=True, which='minor', linestyle='-', alpha=0.2)
ax.grid()
#ax.minorticks_on()

title = "1 heart rate measurement every " + str(n) + " seconds"
ax.title.set_text(title)
plt.grid()

ax.set_ylabel('heart rate (bpm)')
ax.set_xlabel('time (sec)')

plt.show()

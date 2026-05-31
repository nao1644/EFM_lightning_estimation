import numpy as np
import os
import sys
from const import SITE, DTLIST, SAMPLING_RATE, SECONDS_PER_DAY, LEN_TIME

# set
f = open('list.txt', 'r', encoding='UTF-8') # read date(mmddyyyy)
date = f.read()
date = date.rstrip()
f.close()
out_dat   = '../out/dat_data/'
out_waveorigin  = out_dat + 'wavedata/'
out_waveyear  = out_waveorigin + date[4:8] + '/'
out_wave  = out_waveyear + date[0:4] + '/'
file_path_list = [] 
dat_path1_list = []
for i in range(len(SITE)):
    file_path_list.append(str('../data/site' + SITE[i] + '/' + date[4:8] + '/'\
                            + 'Data_Source_' + SITE[i] + '-' + date + '.efm'))
    dat_path1_list.append(str(out_wave + 'wave_file_' + SITE[i] + '_' + date + '.dat'))
logtex0 = '../out/log/'
logtexy = logtex0 + date[4:8] + '/'
logtext = logtexy + 'logtext_'+date+'.txt'

# check file exist
if not os.path.isdir(out_dat):
    os.makedirs(out_dat)
if not os.path.isdir(out_waveorigin):
    os.makedirs(out_waveorigin)
if not os.path.isdir(out_waveyear):
    os.makedirs(out_waveyear)
if not os.path.isdir(out_wave):
    os.makedirs(out_wave)
if not os.path.isdir(logtex0):
    os.makedirs(logtex0)
if not os.path.isdir(logtexy):
    os.makedirs(logtexy)
for i in range(len(dat_path1_list)):
    if os.path.isfile(dat_path1_list[i]):
        print("wave file already made. check !! : " + dat_path1_list[i])
        sys.exit()

# def
def reshape_files(path, dtl): # data formation
    # read original data
    pn_time = []
    pn_char = []
    unknown = []
    file = open(path, 'r')
    for values in file:
        value = values.strip().split(',')  # line is separated by ','
        pn_time.append(str(value[0]))
        pn_char.append(str(value[1]))
        unknown.append(str(value[2]))
    file.close()

    # separate "time" & add ms
    time = np.arange(LEN_TIME)/SAMPLING_RATE + float(dtl)

    # separate positive and negative
    pn_valuere = np.zeros(len(pn_char))
    for i in range(len(pn_char)):
        if pn_char[i][0] == "+":
            pn_valuere[i] = float(str(pn_char[i][1:]))
        elif pn_char[i][0] == "-":
            pn_valuere[i] = -1.*float(str(pn_char[i][1:]))
        else:
            pn_valuere[i] = float(str(pn_char[i][:]))

    # data formation
    n = 0
    undef = -999.
    pn_value = np.zeros(LEN_TIME)
    for i in range(int(SECONDS_PER_DAY)):
        start_ind = n
        for j in range(int(start_ind), len(pn_time)):
            if start_ind >= len(pn_time)-25: # 25: over 20 under 40, this is for last data(23:59(JST))
                pn_value[int(SAMPLING_RATE*i):int(SAMPLING_RATE*(i+1))] = pn_valuere[int(len(pn_valuere)-SAMPLING_RATE):len(pn_valuere)]
                break
            elif pn_time[j][6:8] != str('{0:02d}'.format(int(i%60))):
                pn_num = int(j - start_ind)
                n += pn_num
                if pn_num == SAMPLING_RATE: # normal
                    pn_value[int(SAMPLING_RATE*i):int(SAMPLING_RATE*(i+1))] = pn_valuere[int(start_ind):int(start_ind+SAMPLING_RATE)]
                elif pn_num == SAMPLING_RATE + 1: # more data, one you donot need
                    pn_value[int(SAMPLING_RATE*i):int(SAMPLING_RATE*(i+1))] = pn_valuere[int(start_ind):int(start_ind+SAMPLING_RATE)]
                elif pn_num == SAMPLING_RATE - 1: # less data, one you need to add
                    pn_value[int(SAMPLING_RATE*i):int(SAMPLING_RATE*(i+1)-1)] = pn_valuere[int(start_ind):int(start_ind+SAMPLING_RATE-1)]
                    pn_value[int(SAMPLING_RATE*(i+1)-1)] = pn_valuere[int(start_ind+SAMPLING_RATE-2)]
                else: # abnormal data. change undef, do NOT use these data
                    pn_value[int(SAMPLING_RATE*i):int(SAMPLING_RATE*(i+1))] = [undef for k in range(SAMPLING_RATE)]
                break

    # moving average
    pn_filt = np.zeros(LEN_TIME)
    for i in range(LEN_TIME):
        if i == 0 :
            pn_filtl = [x for x in pn_value[0:3] if x > undef]
        elif i == 1 :
            pn_filtl = [x for x in pn_value[0:4] if x > undef]
        elif i == int(LEN_TIME-2) :
            pn_filtl = [x for x in pn_value[int(LEN_TIME-4):LEN_TIME] if x > undef]
        elif i == int(LEN_TIME-1) :
            pn_filtl = [x for x in pn_value[int(LEN_TIME-3):LEN_TIME] if x > undef]
        else:
            pn_filtl = [x for x in pn_value[int(i-2):int(i+3)] if x > undef]
        if len(pn_filtl) != 0:
            pn_filt[i] = sum(pn_filtl)/len(pn_filtl)
        else:
            pn_filt[i] = undef

    return pn_value, pn_filt, time

# add text
log = open(logtext, mode='a')
log.write('========= start make file =========\n')
log.close()

# read textfile
for i in range(len(SITE)):
    print("site num :", SITE[i])
    file_path = file_path_list[i]
    # add text
    log = open(logtext, mode='a')
    log.write("site num : " + str(SITE[i]) + "\n")
    log.close()
    if not os.path.isfile(file_path):
        print("NO field mill data. check !! : " + file_path)
        # add text
        log = open(logtext, mode='a')
        log.write("NO field mill data. check !! : " + file_path + "\n")
        log.close()
        continue

    pnvalue, pnfilt, pntime = reshape_files(file_path, DTLIST[i])
    # dat
    dat_path1 = dat_path1_list[i]
    dat1 = np.column_stack((pntime, pnfilt, pnvalue))
    np.savetxt(dat_path1, dat1, delimiter=',', fmt=['%.6f','%.6f','%.6f'])

# add text
log = open(logtext, mode='a')
log.write('========= end make file ===========\n')
log.write("\n")
log.close()

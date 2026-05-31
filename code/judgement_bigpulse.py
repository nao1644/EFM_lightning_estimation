import numpy as np
import os
import sys
import datetime
from const import SITE, LEN_TIME

# set
f = open('list.txt', 'r', encoding='UTF-8') # read date(mmddyyyy)
date = f.read()
date = date.rstrip()
f.close()
out_dat   = '../out/dat_data/'
out_pulseorigin = out_dat + 'bigpulse/'
out_pulseyear = out_pulseorigin + date[4:8] + '/'
out_pulse = out_pulseyear + date[0:4] + '/'
out_waveorigin  = out_dat + 'wavedata/'
out_waveyear1  = out_waveorigin + date[4:8] + '/'
out_wave1  = out_waveyear1 + date[0:4] + '/'
out_path2 = out_pulse + 'bigpulse_' + date + '.dat'
dat_path1_list = []
dat_path2_list = []
# make file list
s_nextday = date[4:8] + date[0:4]
s_format = '%Y%m%d'
t_nextday = datetime.datetime.strptime(s_nextday, s_format) + datetime.timedelta(days=1)
s_nextdate = t_nextday.strftime('%Y%m%d')
nextdate = s_nextdate[4:8] + s_nextdate[0:4]
out_waveyear2  = out_waveorigin + nextdate[4:8] + '/'
out_wave2  = out_waveyear2 + nextdate[0:4] + '/'
for i in range(len(SITE)):
    dat_path1_list.append(str(out_wave1 + 'wave_file_' + SITE[i] + '_' + date + '.dat'))
    dat_path2_list.append(str(out_wave2 + 'wave_file_' + SITE[i] + '_' + nextdate + '.dat'))
logtex0 = '../out/log/'
logtexy = logtex0 + date[4:8] + '/'
logtext = logtexy + 'logtext_'+date+'.txt'

# check file exist
if not os.path.isdir(out_dat):
    os.makedirs(out_dat)
if not os.path.isdir(out_pulseorigin):
    os.makedirs(out_pulseorigin)
if not os.path.isdir(out_pulseyear):
    os.makedirs(out_pulseyear)
if not os.path.isdir(out_pulse):
    os.makedirs(out_pulse)
if not os.path.isdir(logtex0):
    os.makedirs(logtex0)
if not os.path.isdir(logtexy):
    os.makedirs(logtexy)
check_f = 0
for i in range(len(dat_path1_list)):
    if not os.path.isfile(dat_path1_list[i]):
        check_f += 1
if check_f == len(SITE):
    print("NO wave file. check !!")
    log = open(logtext, mode='a')
    log.write('========= search big pulse ========\n')
    log.write("NO wave file. check !!\n")
    log.write('======= end search big pulse ======\n')
    log.write("\n")
    log.close()
    sys.exit()
if os.path.isfile(out_path2):
    print("pulse file already made. check !! : " + out_path2)
    sys.exit()

# def
def find_bigpulse(path1, path2): # search BIG pulse
    # read
    check = 0
    undef = -999.
    pn_value = np.loadtxt(path1, dtype = 'float', delimiter=',', usecols = 2, ndmin = 1).tolist() # wave value
    pn_filt  = np.loadtxt(path1, dtype = 'float', delimiter=',', usecols = 1, ndmin = 1).tolist() # average
    time     = np.loadtxt(path1, dtype = 'float', delimiter=',', usecols = 0, ndmin = 1).tolist() # time
    if os.path.isfile(path2): # data file of nextday, for calculation of  0 o'clock
        check += 1
        pn_value2 = np.loadtxt(path2, dtype = 'float', delimiter=',', usecols = 2, ndmin = 1).tolist() # wave value
        pn_filt2  = np.loadtxt(path2, dtype = 'float', delimiter=',', usecols = 1, ndmin = 1).tolist() # average
        pn_value = pn_value + pn_value2 
        pn_filt  = pn_filt  + pn_filt2
    else:
        print('No data:'+path2)
        log = open(logtext, mode='a')
        log.write('No data:'+path2+'\n')
        log.close()

    # judege pulse peak & positive or negative
    p_time = [] # time of pulse start
    p_valu = [] # value of pulse start
    dp_val = [] # diference value of pulse
    p_inde = [] # index of pulse start
    p_inee = [] # index of pulse end
    p_vale = [] # value of pulse end
    n_time = []
    n_valu = []
    dn_val = []
    n_inde = []
    n_inee = []
    n_vale = []
    print("loop!!")
    # decide end
    if check == 1:
        endindex = LEN_TIME
    else:
        endindex = int(LEN_TIME-5)
    # calculate difference
    pn_valuedif = np.zeros(endindex+4)
    for i in range(endindex+4):
        if pn_value[i+1] != undef and pn_value[i] != undef:
            pn_valuedif[i] = pn_value[i+1] - pn_value[i]
        
    # loop
    for i in range(1, endindex):
        if pn_valuedif[i] > 0. and pn_valuedif[i-1] < 0.02: # negative
            if (pn_valuedif[i]+pn_valuedif[i+1])/2. > 0.02:
                if (pn_valuedif[i]+pn_valuedif[i+1]+pn_valuedif[i+2])/3. > 0.02:
                    if (pn_valuedif[i]+pn_valuedif[i+1]+pn_valuedif[i+2]+pn_valuedif[i+3])/4. > 0.02:
                        check_p = 0
                        for j in range(int(i+4), endindex):
                            if pn_valuedif[j] < 0.:
                                check_p += 4
                                if check_p == 5: # "dE == 0", "dE<0" both ones in a row
                                    for k in range(i, 1, -1): # search base time(search CORRECT time of lightning)
                                        if pn_valuedif[k-1] <= 0. or pn_valuedif[k-1] <= undef: # opposite slope (base, start time of lightning)
                                            pn_ddal = sum(pn_valuedif[k:j])#pn_value[j-1]-pn_value[k]
                                            if abs(pn_ddal/(j-1-k)) > 0.02: # absolute value of dE in ONE lightning
                                                n_time.append(float(time[k]))
                                                n_valu.append(float(pn_value[k]))
                                                n_inde.append(int(k))
                                                dn_val.append(float(pn_ddal))
                                                n_inee.append(int(j-1))
                                                n_vale.append(float(pn_value[j-1]))
                                            break
                                    break
                                elif check_p == 6: # "dE == 0" two times, and "dE<0"
                                    for k in range(i, 1, -1): # search base time(search CORRECT time of lightning)
                                        if pn_valuedif[k-1] <= 0. or pn_valuedif[k-1] <= undef: # opposite slope (base, start time of lightning)
                                            pn_ddal = sum(pn_valuedif[k:j-1])#pn_value[j-2]-pn_value[k]
                                            if abs(pn_ddal/(j-2-k)) > 0.02: # absolute value of dE in ONE lightning
                                                n_time.append(float(time[k]))
                                                n_valu.append(float(pn_value[k]))
                                                n_inde.append(int(k))
                                                dn_val.append(float(pn_ddal))
                                                n_inee.append(int(j-2))
                                                n_vale.append(float(pn_value[j-2]))
                                            break
                                    break
                                elif check_p == 8: # "dE == 0", two times in a row
                                    for k in range(i, 1, -1): # search base time(search CORRECT time of lightning)
                                        if pn_valuedif[k-1] <= 0. or pn_valuedif[k-1] <= undef: # opposite slope (base, start time of lightning)
                                            pn_ddal = sum(pn_valuedif[k:j])#pn_value[j-1]-pn_value[k]
                                            if abs(pn_ddal/(j-1-k)) > 0.02: # absolute value of dE in ONE lightning
                                                n_time.append(float(time[k]))
                                                n_valu.append(float(pn_value[k]))
                                                n_inde.append(int(k))
                                                dn_val.append(float(pn_ddal))
                                                n_inee.append(int(j-1))
                                                n_vale.append(float(pn_value[j-1]))
                                            break
                                    break
                                else:
                                    continue
                            elif int(1.e4*pn_valuedif[j]) == 0:
                                check_p += 1
                                if check_p == 3:
                                    for k in range(i, 1, -1):
                                        if pn_valuedif[k-1] <= 0. or pn_valuedif[k-1] <= undef:
                                            pn_ddal = sum(pn_valuedif[k:j-1])#pn_value[j-2]-pn_value[k]
                                            if abs(pn_ddal/(j-2-k)) > 0.02:
                                                n_time.append(float(time[k]))
                                                n_valu.append(float(pn_value[k]))
                                                n_inde.append(int(k))
                                                dn_val.append(float(pn_ddal))
                                                n_inee.append(int(j-2))
                                                n_vale.append(float(pn_value[j-2]))
                                            break
                                    break
                                elif check_p == 5: # "dE == 0", "dE<0" both ones in a row
                                    for k in range(i, 1, -1): # search base time(search CORRECT time of lightning)
                                        if pn_valuedif[k-1] <= 0. or pn_valuedif[k-1] <= undef: # opposite slope (base, start time of lightning)
                                            pn_ddal = sum(pn_valuedif[k:j])#pn_value[j-1]-pn_value[k]
                                            if abs(pn_ddal/(j-1-k)) > 0.02: # absolute value of dE in ONE lightning
                                                n_time.append(float(time[k]))
                                                n_valu.append(float(pn_value[k]))
                                                n_inde.append(int(k))
                                                dn_val.append(float(pn_ddal))
                                                n_inee.append(int(j-1))
                                                n_vale.append(float(pn_value[j-1]))
                                            break
                                    break
                                elif check_p == 6: # "dE == 0" two times, and "dE<0"
                                    for k in range(i, 1, -1): # search base time(search CORRECT time of lightning)
                                        if pn_valuedif[k-1] <= 0. or pn_valuedif[k-1] <= undef: # opposite slope (base, start time of lightning)
                                            pn_ddal = sum(pn_valuedif[k:j-1])#pn_value[j-2]-pn_value[k]
                                            if abs(pn_ddal/(j-2-k)) > 0.02: # absolute value of dE in ONE lightning
                                                n_time.append(float(time[k]))
                                                n_valu.append(float(pn_value[k]))
                                                n_inde.append(int(k))
                                                dn_val.append(float(pn_ddal))
                                                n_inee.append(int(j-2))
                                                n_vale.append(float(pn_value[j-2]))
                                            break
                                    break
                                else:
                                    continue
                            else:
                                check_p = 0
                                continue
                    else:
                        continue
                else:
                    continue
            else:
                continue
        elif pn_valuedif[i] < 0. and pn_valuedif[i-1] > -0.02: # positive
            if (pn_valuedif[i]+pn_valuedif[i+1])/2. < -0.02:
                if (pn_valuedif[i]+pn_valuedif[i+1]+pn_valuedif[i+2])/3. < -0.02:
                    if (pn_valuedif[i]+pn_valuedif[i+1]+pn_valuedif[i+2]+pn_valuedif[i+3])/4. < -0.02:
                        check_p = 0
                        for j in range(int(i+4), endindex):
                            if pn_valuedif[j] > 0.:
                                check_p += 4
                                if check_p == 5:
                                    for k in range(i, 1, -1):
                                        if pn_valuedif[k-1] >= 0. or pn_valuedif[k-1] <= undef:
                                            pn_ddal = sum(pn_valuedif[k:j])#pn_value[j-1]-pn_value[k]
                                            if abs(pn_ddal/(j-1-k)) > 0.02:
                                                p_time.append(float(time[k]))
                                                p_valu.append(float(pn_value[k]))
                                                p_inde.append(int(k))
                                                dp_val.append(float(pn_ddal))
                                                p_inee.append(int(j-1))
                                                p_vale.append(float(pn_value[j-1]))
                                            break
                                    break
                                elif check_p == 6:
                                    for k in range(i, 1, -1):
                                        if pn_valuedif[k-1] >= 0. or pn_valuedif[k-1] <= undef:
                                            pn_ddal = sum(pn_valuedif[k:j-1])#pn_value[j-2]-pn_value[k]
                                            if abs(pn_ddal/(j-2-k)) > 0.02:
                                                p_time.append(float(time[k]))
                                                p_valu.append(float(pn_value[k]))
                                                p_inde.append(int(k))
                                                dp_val.append(float(pn_ddal))
                                                p_inee.append(int(j-2))
                                                p_vale.append(float(pn_value[j-2]))
                                            break
                                    break
                                elif check_p == 8:
                                    for k in range(i, 1, -1):
                                        if pn_valuedif[k-1] >= 0. or pn_valuedif[k-1] <= undef:
                                            pn_ddal = sum(pn_valuedif[k:j])#pn_value[j-1]-pn_value[k]
                                            if abs(pn_ddal/(j-1-k)) > 0.02:
                                                p_time.append(float(time[k]))
                                                p_valu.append(float(pn_value[k]))
                                                p_inde.append(int(k))
                                                dp_val.append(float(pn_ddal))
                                                p_inee.append(int(j-1))
                                                p_vale.append(float(pn_value[j-1]))
                                            break
                                    break
                                else:
                                    continue
                            elif int(1.e4*pn_valuedif[j]) == 0:
                                check_p += 1
                                if check_p == 3:
                                    for k in range(i, 1, -1):
                                        if pn_valuedif[k-1] >= 0. or pn_valuedif[k-1] <= undef:
                                            pn_ddal = sum(pn_valuedif[k:j-1])#pn_value[j-2]-pn_value[k]
                                            if abs(pn_ddal/(j-2-k)) > 0.02:
                                                p_time.append(float(time[k]))
                                                p_valu.append(float(pn_value[k]))
                                                p_inde.append(int(k))
                                                dp_val.append(float(pn_ddal))
                                                p_inee.append(int(j-2))
                                                p_vale.append(float(pn_value[j-2]))
                                            break
                                    break
                                elif check_p == 5:
                                    for k in range(i, 1, -1):
                                        if pn_valuedif[k-1] >= 0. or pn_valuedif[k-1] <= undef:
                                            pn_ddal = sum(pn_valuedif[k:j])#pn_value[j-1]-pn_value[k]
                                            if abs(pn_ddal/(j-1-k)) > 0.02:
                                                p_time.append(float(time[k]))
                                                p_valu.append(float(pn_value[k]))
                                                p_inde.append(int(k))
                                                dp_val.append(float(pn_ddal))
                                                p_inee.append(int(j-1))
                                                p_vale.append(float(pn_value[j-1]))
                                            break
                                    break
                                elif check_p == 6:
                                    for k in range(i, 1, -1):
                                        if pn_valuedif[k-1] >= 0. or pn_valuedif[k-1] <= undef:
                                            pn_ddal = sum(pn_valuedif[k:j-1])#pn_value[j-2]-pn_value[k]
                                            if abs(pn_ddal/(j-2-k)) > 0.02:
                                                p_time.append(float(time[k]))
                                                p_valu.append(float(pn_value[k]))
                                                p_inde.append(int(k))
                                                dp_val.append(float(pn_ddal))
                                                p_inee.append(int(j-2))
                                                p_vale.append(float(pn_value[j-2]))
                                            break
                                    break
                                else:
                                    continue
                            else:
                                check_p = 0
                                continue
                    else:
                        continue
                else:
                    continue
            else:
                continue
        else:
            continue

    # delete same times
    p_timef = []
    p_valuf = []
    dp_valf = []
    p_indef = []
    n_timef = []
    n_valuf = []
    dn_valf = []
    n_indef = []
    search_p = 0
    check_p = 0
    search_n = 0
    check_n = 0
    for i in range(len(p_time)): # positive
        search_p = i
        if  p_inde[search_p] >= p_inde[check_p] and p_inee[search_p] <= p_inee[check_p]:
            continue
        elif p_inde[search_p] <= p_inde[check_p] and p_inee[search_p] >= p_inee[check_p]:
            check_p = search_p
        elif i == int(len(p_time)-1):
            if p_inde[search_p] >= p_inde[check_p] and p_inee[search_p] <= p_inee[check_p]:
                p_timef.append(float(p_time[check_p]))
                p_valuf.append(float(p_valu[check_p]))
                p_indef.append(int(p_inde[check_p]))
                dp_valf.append(float(dp_val[check_p]))
            elif p_inde[search_p] <= p_inde[check_p] and p_inee[search_p] >= p_inee[check_p]:
                p_timef.append(float(p_time[search_p]))
                p_valuf.append(float(p_valu[search_p]))
                p_indef.append(int(p_inde[search_p]))
                dp_valf.append(float(dp_val[search_p]))
            else:
                p_timef.append(float(p_time[check_p]))
                p_valuf.append(float(p_valu[check_p]))
                p_indef.append(int(p_inde[check_p]))
                dp_valf.append(float(dp_val[check_p]))
                p_timef.append(float(p_time[search_p]))
                p_valuf.append(float(p_valu[search_p]))
                p_indef.append(int(p_inde[search_p]))
                dp_valf.append(float(dp_val[search_p]))
        else:
            p_timef.append(float(p_time[check_p]))
            p_valuf.append(float(p_valu[check_p]))
            p_indef.append(int(p_inde[check_p]))
            dp_valf.append(float(dp_val[check_p]))
            check_p = search_p
    for i in range(len(n_time)): # negative
        search_n = i
        if  n_inde[search_n] >= n_inde[check_n] and n_inee[search_n] <= n_inee[check_n]:
            continue
        elif n_inde[search_n] <= n_inde[check_n] and n_inee[search_n] >= n_inee[check_n]:
            check_n = search_n
        elif i == int(len(n_time)-1):
            if n_inde[search_n] >= n_inde[check_n] and n_inee[search_n] <= n_inee[check_n]:
                n_timef.append(float(n_time[check_n]))
                n_valuf.append(float(n_valu[check_n]))
                n_indef.append(int(n_inde[check_n]))
                dn_valf.append(float(dn_val[check_n]))
            elif n_inde[search_n] <= n_inde[check_n] and n_inee[search_n] >= n_inee[check_n]:
                n_timef.append(float(n_time[search_n]))
                n_valuf.append(float(n_valu[search_n]))
                n_indef.append(int(n_inde[search_n]))
                dn_valf.append(float(dn_val[search_n]))
            else:
                n_timef.append(float(n_time[check_n]))
                n_valuf.append(float(n_valu[check_n]))
                n_indef.append(int(n_inde[check_n]))
                dn_valf.append(float(dn_val[check_n]))
                n_timef.append(float(n_time[search_n]))
                n_valuf.append(float(n_valu[search_n]))
                n_indef.append(int(n_inde[search_n]))
                dn_valf.append(float(dn_val[search_n]))
        else:
            n_timef.append(float(n_time[check_n]))
            n_valuf.append(float(n_valu[check_n]))
            n_indef.append(int(n_inde[check_n]))
            dn_valf.append(float(dn_val[check_n]))
            check_n = search_n

    return p_timef, p_valuf, dp_valf, p_indef, n_timef, n_valuf, dn_valf, n_indef

# add text
log = open(logtext, mode='a')
log.write('========= search big pulse ========\n')
log.close()

# read textfile
alltime_p   = []
allvalue_p  = []
alldvalue_p = []
allindex_p  = []
allsite_p   = []
for i in range(len(SITE)):
    print("site num :", SITE[i])
    # add text
    log = open(logtext, mode='a')
    log.write("site num : "+str(SITE[i]) + "\n")
    log.close()

    # calculation
    file_path1 = dat_path1_list[i]
    file_path2 = dat_path2_list[i]
    if not os.path.isfile(file_path1):
        log = open(logtext, mode='a')
        log.write("NO wave file. :"+str(file_path1)+"\n")
        log.write("\n")
        log.close()
        continue
    else:
        ptime, pvalue, dpvalue, pinde, ntime, nvalue, dnvalue, ninde = find_bigpulse(file_path1, file_path2)
        print("pulse_number : ", str(len(ptime)+len(ntime)))

    # add to one list
    for j in range(len(ptime)):
        alltime_p.append(ptime[j])
        allvalue_p.append(pvalue[j])
        alldvalue_p.append(dpvalue[j])
        allindex_p.append(pinde[j])
        allsite_p.append(int(i+1))
    for j in range(len(ntime)):
        alltime_p.append(ntime[j])
        allvalue_p.append(nvalue[j])
        alldvalue_p.append(dnvalue[j])
        allindex_p.append(ninde[j])
        allsite_p.append(int(i+1))

    # add text
    log = open(logtext, mode='a')
    log.write("pulse_number : "+str(len(ptime)+len(ntime)) + "\n")
    log.write("\n")
    log.close()

# sort data by time
if len(alltime_p) != 0:
    combined_p = list(zip(alltime_p, allvalue_p, alldvalue_p, allindex_p, allsite_p))
    sort_p = sorted(combined_p, key=lambda x: x[0])
    alltime_pp, allvalue_pp, alldvalue_pp, allindex_pp, allsite_pp = zip(*sort_p) # positive

# make .dat for pulse
if len(alltime_p) != 0:
    dat2 = np.column_stack((alltime_pp, allvalue_pp, alldvalue_pp, allindex_pp, allsite_pp))
    np.savetxt(out_path2, dat2, delimiter=',', fmt=['%.6f','%.6f','%.6f','%d','%d'])

print()
print("all pulse number")
print("pulse_num :", len(alltime_p))

# add text
log = open(logtext, mode='a')
log.write("all pulse number\n")
log.write("pulse_number : "+str(len(alltime_p)) + "\n")
log.write('======= end search big pulse ======\n')
log.write("\n")
log.close()

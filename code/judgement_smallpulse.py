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
out_pulseorigin = out_dat + 'smallpulse/'
out_pulseyear = out_pulseorigin + date[4:8] + '/'
out_pulse = out_pulseyear + date[0:4] + '/'
out_waveorigin  = out_dat + 'wavedata/'
out_waveyear1  = out_waveorigin + date[4:8] + '/'
out_wave1  = out_waveyear1 + date[0:4] + '/'
dat_path1_list = []
dat_path2_list = []
out_path2_list = []
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
    out_path2_list.append(str(out_pulse + 'smallpulse_' + SITE[i] + '_' + date + '.dat'))
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
check_f = 0
for i in range(len(dat_path1_list)):
    if not os.path.isfile(dat_path1_list[i]):
        check_f += 1
    if os.path.isfile(out_path2_list[i]):
        print("pulse file already made. check !! : " + out_path2_list[i])
        sys.exit()
if check_f == len(SITE):
    print("NO wave file. check !!")
    log = open (logtext, mode='a')
    log.write('========= search small pulse ========\n')
    log.write("NO wave file. check !!\n")
    log.write('======= end search small pulse ======\n')
    log.write("\n")
    log.close()
    sys.exit()

# def
def find_smallpulse(path1, path2):  # search small pulse
    # search grid
    dsgrid = 5
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
        log = open (logtext, mode='a')
        log.write('No data:'+path2+'\n')
        log.close()

    # judege pulse peak & positive or negative
    p_time = []
    p_valu = []
    dp_val = []
    p_valf = []
    dp_vaf = []
    p_inde = []
    n_time = []
    n_valu = []
    dn_val = []
    n_valf = []
    dn_vaf = []
    n_inde = []
    print("loop!!")
    # decide end
    if check == 1:
        endindex = LEN_TIME
    else:
        endindex = int(LEN_TIME - dsgrid)
    # calculate difference
    pn_valuedif = np.zeros(endindex + dsgrid)
    pn_filtdif = np.zeros(endindex + dsgrid)
    for i in range(endindex + dsgrid):
        if check != 1 and i == endindex + dsgrid - 1:
            pn_valuedif[i] = 0.
            pn_filtdif[i]  = 0.
            continue
        else:
            if pn_value[i+1] != undef and pn_value[i] != undef:
                pn_valuedif[i] = pn_value[i+1] - pn_value[i]
            if pn_filt[i+1] != undef and pn_filt[i] != undef:
                pn_filtdif[i] = pn_filt[i+1] - pn_filt[i]

    # loop
    for i in range(dsgrid, endindex):
        # searching the time of lightning
        if int(1.e4*pn_valuedif[i]) == 0. and int(1.e4*pn_valuedif[i-1]) == 0.: # no change, check filted data
            if sum(pn_filtdif[i:i+dsgrid]) > 0. and sum(pn_filtdif[i-dsgrid:i]) < 0.: # negative
                pn_valuel = [x for x in pn_value[i-dsgrid:i+dsgrid+1] if x > undef]
                pn_filtl  = [x for x in  pn_filt[i-dsgrid:i+dsgrid+1] if x > undef]
                if len(pn_valuel) != 0:
                    pn_ddal = max(pn_valuel)-min(pn_valuel)
                    pn_fdal = max(pn_filtl)-min(pn_filtl)
                    if abs(pn_ddal) > 1.e-5 and abs(pn_fdal) > 1.e-5:
                        n_time.append(float(time[i]))
                        n_valu.append(float(pn_value[i]))
                        dn_val.append(float(pn_ddal))
                        n_valf.append(float(pn_filt[i]))
                        dn_vaf.append(float(pn_fdal))
                        n_inde.append(int(i))
            elif sum(pn_filtdif[i:i+dsgrid]) < 0. and sum(pn_filtdif[i-dsgrid:i]) > 0.: # positive
                pn_valuel = [x for x in pn_value[i-dsgrid:i+dsgrid+1] if x > undef]
                pn_filtl  = [x for x in  pn_filt[i-dsgrid:i+dsgrid+1] if x > undef]
                if len(pn_valuel) != 0:
                    pn_ddal = min(pn_valuel)-max(pn_valuel)
                    pn_fdal = min(pn_filtl)-max(pn_filtl)
                    if abs(pn_ddal) > 0.0000001 and abs(pn_fdal) > 0.0000001:
                        p_time.append(float(time[i]))
                        p_valu.append(float(pn_value[i]))
                        dp_val.append(float(pn_ddal))
                        p_valf.append(float(pn_filt[i]))
                        dp_vaf.append(float(pn_fdal))
                        p_inde.append(int(i))
            else: # neutral
                continue
        elif pn_valuedif[i] >= 0. and pn_valuedif[i-1] <= 0.: # negative
            pn_valuel = [x for x in pn_value[i-dsgrid:i+dsgrid+1] if x > undef]
            pn_filtl  = [x for x in  pn_filt[i-dsgrid:i+dsgrid+1] if x > undef]
            if len(pn_valuel) != 0:
                pn_ddal = max(pn_valuel)-min(pn_valuel)
                pn_fdal = max(pn_filtl)-min(pn_filtl)
                if abs(pn_ddal) > 1.e-5 and abs(pn_fdal) > 1.e-5:
                    n_time.append(float(time[i]))
                    n_valu.append(float(pn_value[i]))
                    dn_val.append(float(pn_ddal))
                    n_valf.append(float(pn_filt[i]))
                    dn_vaf.append(float(pn_fdal))
                    n_inde.append(int(i))
        elif  pn_valuedif[i] <= 0. and pn_valuedif[i-1] >= 0.: # positive
            pn_valuel = [x for x in pn_value[i-dsgrid:i+dsgrid+1] if x > undef]
            pn_filtl  = [x for x in  pn_filt[i-dsgrid:i+dsgrid+1] if x > undef]
            if len(pn_valuel) != 0:
                pn_ddal = min(pn_valuel)-max(pn_valuel)
                pn_fdal = min(pn_filtl)-max(pn_filtl)
                if abs(pn_ddal) > 1.e-5 and abs(pn_fdal) > 1.e-5:
                    p_time.append(float(time[i]))
                    p_valu.append(float(pn_value[i]))
                    dp_val.append(float(pn_ddal))
                    p_valf.append(float(pn_filt[i]))
                    dp_vaf.append(float(pn_fdal))
                    p_inde.append(int(i))

    return p_time, p_valu, dp_val, p_valf, dp_vaf, p_inde, n_time, n_valu, dn_val, n_valf, dn_vaf, n_inde

# add text
log = open (logtext, mode='a')
log.write('======== search small pulse =======\n')
log.close()

# read textfile
for i in range(len(SITE)):
    print("site num :", SITE[i])
    file_path1 = dat_path1_list[i]
    file_path2 = dat_path2_list[i]

    if not os.path.isfile(file_path1):
        log = open (logtext, mode='a')
        log.write("NO wave file. :"+str(file_path1)+"\n")
        log.write("\n")
        log.close()
        continue
    else:
        alltime_p   = []
        allvalue_p  = []
        alldvalue_p = []
        allvaluef_p  = []
        alldvaluef_p = []
        allindex_p  = []
        ptime, pvalue, dpvalue, pvaluef, dpvaluef, pinde, ntime, nvalue, dnvalue, nvaluef, dnvaluef, ninde = find_smallpulse(file_path1, file_path2)
    # add to one list
    alltime_p.extend(ptime)
    allvalue_p.extend(pvalue)
    alldvalue_p.extend(dpvalue)
    allvaluef_p.extend(pvaluef)
    alldvaluef_p.extend(dpvaluef)
    allindex_p.extend(pinde)
    alltime_p.extend(ntime)
    allvalue_p.extend(nvalue)
    alldvalue_p.extend(dnvalue)
    allvaluef_p.extend(nvaluef)
    alldvaluef_p.extend(dnvaluef)
    allindex_p.extend(ninde)

    # sort data by time
    if len(alltime_p) != 0:
        combined_p = list(zip(alltime_p, allvalue_p, alldvalue_p, allvaluef_p, alldvaluef_p, allindex_p))
        sort_p = sorted(combined_p, key=lambda x: x[0])
        alltime_pp, allvalue_pp, alldvalue_pp, allvaluef_pp, alldvaluef_pp, allindex_pp = zip(*sort_p)

        # dat
        out_path2 = out_path2_list[i]
        dat2 = np.column_stack((alltime_pp, allvalue_pp, alldvalue_pp, allvaluef_pp, alldvaluef_pp, allindex_pp))
        np.savetxt(out_path2, dat2, delimiter=',', fmt=['%.6f','%.6f','%.6f','%.6f','%.6f','%d'])
        print("pulse_num:", str(len(ptime)+len(ntime)))

    # add text
    log = open (logtext, mode='a')
    log.write("site num : "+str(SITE[i]) + "\n")
    log.write("pulse_number : "+str(len(ptime)+len(ntime)) + "\n")
    if i != len(SITE)-1:
        log.write("\n")
    log.close()

# add text
log = open (logtext, mode='a')
log.write('====== end search small pulse =====\n')
log.write("\n")
log.close()

import numpy as np
import os
import sys
from const import SITE, RR, C_CALIBRATION

# path
f = open('list.txt', 'r', encoding='UTF-8') # read date(mmddyyyy)
date = f.read()
date = date.rstrip()
f.close()
path_pulb = '../out/dat_data/bigpulse/' + date[4:8] + '/' + date[0:4]
path_timp = '../out/timelist/' + date[4:8] + '/' + date[0:4]
out_path = '../out/for_calculation/'
out_pathyear = out_path + date[4:8] + '/'
out_pathday  = out_pathyear + date[0:4] + '/'
logtex0 = '../out/log/'
logtexy = logtex0 + date[4:8] + '/'
logtext = logtexy + 'logtext_'+date+'.txt'

# add text
log = open(logtext, mode='a')
log.write('====== create file for next  ======\n')
log.close()

# check file exist
if not os.path.isdir(out_path):
    os.makedirs(out_path)
if not os.path.isdir(out_pathyear):
    os.makedirs(out_pathyear)
if not os.path.isdir(out_pathday):
    os.makedirs(out_pathday)
else:
    print("dir already made. check !! : " )
    sys.exit()

# def
thre_dE = 0. # kV/m
undef = -999.
undefindex = -999
len_index = 60 # range for numpy()

# read big pulse data
pultime_p   = [] # time 
pulvalue_p  = [] # kV/m
puldvalue_p = [] # kV/m
pulindex_p  = [] # index
pulsite_p   = [] # sitenum
fp_path = os.path.join(path_pulb, "bigpulse" + "_" + str(date) +".dat")
# check start calculate or not
check_p = 0
past_data = np.zeros(int(len(SITE)+1)) # check already made smae dE data file or not
if not os.path.isfile(fp_path):
    print("BIG pulse file not found. check !! : " + fp_path)
    # add text
    log = open(logtext, mode='a')
    log.write('BIG pulse file not found. check !!\n')
    log.close()
else:
    # read
    pultime_p   = np.loadtxt(fp_path, dtype = 'float', delimiter=',', usecols = 0, ndmin = 1).tolist() # time
    pulvalue_pp  = RR*np.loadtxt(fp_path, dtype = 'float', delimiter=',', usecols = 1, ndmin = 1) # kV/m
    puldvalue_pp = RR*np.loadtxt(fp_path, dtype = 'float', delimiter=',', usecols = 2, ndmin = 1) # kV/m
    pulindex_p  = np.loadtxt(fp_path, dtype = 'int', delimiter=',', usecols = 3, ndmin = 1).tolist() # index(time)
    pulsite_p   = np.loadtxt(fp_path, dtype = 'int', delimiter=',', usecols = 4, ndmin = 1).tolist() # site num
    pulvalue_p  = pulvalue_pp.tolist()
    puldvalue_p = puldvalue_pp.tolist()
    # location
    for i in range(len(pultime_p)):
        print("")
        print("start searching locations:", str(pultime_p[i]))

        time_site = pultime_p[i]
        # index for each site
        indexb = np.full((len(SITE), int(len_index)), undefindex)
        indexs = np.full((len(SITE), int(len_index)), undefindex)
        indexb_index = np.zeros(len(SITE)) # save index for select indexb
        indexs_index = np.zeros(len(SITE)) # save index for select indexs

        # location of pulse
        aim = 0
        for j in range(len(SITE)):
            if pulsite_p[i] == int(j+1):
                indexb[j, int(indexb_index[j])] = int(i)
                aim = int(j+1)
                indexb_index[j] = indexb_index[j] + 1

        # search pulse in big pulse
        print("search big pulse")
        for j in range(i, -1, -1): # search pulse forward
            if abs(pultime_p[j] - pultime_p[i]) < 1.0: # difference of second
                if pulsite_p[j] != aim:
                    for k in range(len(SITE)):
                        if pulsite_p[j] == int(k+1):
                            indexb[k, int(indexb_index[k])] = int(j)
                            indexb_index[k] = indexb_index[k] + 1
            else:
                break
        for j in range(i, len(pultime_p), 1): # search pulse backward
            if abs(pultime_p[j] - pultime_p[i]) < 1.0: # difference of second
                if pulsite_p[j] != aim:
                    for k in range(len(SITE)):
                        if pulsite_p[j] == int(k+1):
                            indexb[k, int(indexb_index[k])] = int(j)
                            indexb_index[k] = indexb_index[k] + 1
            else:
                break

        # search pulse in small pulse
        print("search small pulse")
        time_round = round(pultime_p[i])
        time_sp = [int(time_round-1), int(time_round), int(time_round+1)]
        pultime_sp   = [] 
        pulvalue_sp  = []
        puldvalue_sp = []
        pulvaluf_sp  = []
        puldvaluf_sp = []
        pulindex_sp  = []
        pulsite_sp   = []
        for l in range(len(time_sp)):
            fsp_path = os.path.join(path_timp, str(time_sp[l]) + ".dat") # .dat? check your "timelist" !!
            print("file place:", str(fsp_path))
            if os.path.exists(fsp_path):
                file = open(fsp_path, 'r')
                for values in file:
                    value = values.strip().split(',') # line is separated by ','
                    pultime_sp.append(float(value[0]))
                    pulvalue_sp.append(RR*float(value[1]))
                    puldvalue_sp.append(RR*float(value[2]))
                    pulvaluf_sp.append(RR*float(value[3]))
                    puldvaluf_sp.append(RR*float(value[4]))
                    pulindex_sp.append(int(value[5]))
                    pulsite_sp.append(int(value[6]))
                file.close()

        # check
        if len(pultime_sp) == 0:
            print("All file not found. CHECK!!")
            continue
        else:
            # search pulse in small pulse
            for j in range(len(pultime_sp)):
                if pulsite_sp[j] <= len(SITE):
                    if abs(pultime_sp[j] - pultime_p[i]) < 1.0:# difference of second
                        site_index = pulsite_sp[j]-1
                        indexs[int(site_index), int(indexs_index[int(site_index)])] = int(j)
                        indexs_index[int(site_index)] = indexs_index[int(site_index)] + 1

        # check before loop
        check_loop = 0
        indexb_numsum = np.zeros(len(SITE))
        indexs_numsum = np.zeros(len(SITE))
        for j in range(len(SITE)):
            for k in range(len_index):
                if indexb[j, k] >= 0:
                    indexb_numsum[j] += 1
                else:
                    break
        for j in range(len(SITE)):
            for k in range(len_index):
                if indexs[j, k] >= 0:
                    indexs_numsum[j] += 1
                else:
                    break

        # check whether at least four sites have dE data
        valid_site_num = 0
        for j in range(len(SITE)):
            if int(indexb_numsum[j] + indexs_numsum[j]) != 0:
                valid_site_num += 1
        if valid_site_num >= 4:
            check_loop = 1
        else:
            check_loop = 0

        # loop
        if check_loop != 0:
            # def dE
            print("start make file")
            # make list of dE for calculate location and dq of lightnig.
            site_de = np.zeros(len(SITE))
            windex  = np.zeros(len(SITE))
            bs = np.zeros(len(SITE))

            for j in range(len(SITE)):
                if indexb_numsum[j] == 0:
                    if indexs_numsum[j] == 0: # NO dE data.
                        site_de[j] = undef
                        windex[j] = undefindex
                        bs[j] = 0
                    else:
                        abst = 999.
                        check_break = 0
                        for k in range(len_index):
                            if indexs[j, k] >= 0:
                                if abst > abs(time_site-pultime_sp[int(indexs[j, k])]):
                                    abst = abs(time_site-pultime_sp[int(indexs[j, k])])
                                    site_de[j] = abs(puldvaluf_sp[int(indexs[j, k])])
                                    windex[j] = pulindex_sp[int(indexs[j, k])]
                                    bs[j] = 0
                            else:
                                check_break += 1 # count undef in an array. 
                                if check_break > 2:
                                    break # to check NEXT site
                else:
                    for k in range(len_index):
                        if indexb[j, k] >= 0:
                            site_de[j] = abs(puldvalue_p[int(indexb[j, k])])
                            windex[j] = pulindex_p[int(indexb[j, k])]
                            bs[j] = 1 # big pulse

            # save
            # time, site num of BIG pulse, dE of each sites
            if max(site_de) > thre_dE:
                # check
                check_save = 0
                if abs(past_data[0]-time_site) <= 1.:
                    for k in range(len(SITE)):
                        if not int(1000*(past_data[k+1]-site_de[k])) == 0:
                            check_save = 1
                    if not check_save == 0:
                        past_data[0] = time_site # input time
                        for j in range(len(SITE)):
                            past_data[j+1] = site_de[j] # input dE data
                else:
                    check_save = 1
                    past_data[0] = time_site # input time
                    for j in range(len(SITE)):
                        past_data[j+1] = site_de[j] # input dE data

                # save text
                if check_save != 0:
                    # apply calibration factor
                    if len(C_CALIBRATION) < len(SITE):
                        print("Number of C_CALIBRATION is not enough. check const.py")
                        continue
                    
                    # use C_CALIBRATION
                    for j in range(len(SITE)):
                        if site_de[j] > 0:
                            site_de[j] = C_CALIBRATION[j]*site_de[j]
                    check_p += 1

                    dat1_list = [time_site, aim]
                    dat1_list.extend(site_de)
                    dat1_list.extend(windex)
                    dat1_list.extend(bs)
                    dat1 = np.array(dat1_list).reshape(1, -1)

                    out_path1 = out_pathday + str(time_site) + '_' + str(int(check_loop))

                    # format
                    fmt = ['%.3f', '%d']
                    fmt.extend(['%.6f'] * len(SITE))
                    fmt.extend(['%d'] * len(SITE))
                    fmt.extend(['%d'] * len(SITE))

                    # save
                    np.savetxt(out_path1, dat1, delimiter=',', fmt=fmt)
                    print("end make file!")
                else:
                    print("same time NEXT")
            else:
                print("data is too small.")
        else:
            print("data is not enough.")

print("complete all !!")


# add text
log = open(logtext, mode='a')
log.write("file_number : "+str(check_p) + "\n")
log.write('===== end create file for next  ===\n')
log.write('\n')
log.close()

import numpy as np
import os
import sys
from const import SITE, SECONDS_PER_DAY

# set
f = open('list.txt', 'r', encoding='UTF-8') # read date(mmddyyyy)
date = f.read()
date = date.rstrip()
f.close()
path_t = "../out/timelist/"
path_ty = path_t +"/"+ date[4:8]+"/"
path_td = path_ty +"/"+ date[0:4]
path_small = "../out/dat_data/smallpulse"
logtex0 = '../out/log/'
logtexy = logtex0 + date[4:8] + '/'
logtext = logtexy + 'logtext_'+date+'.txt'

# check file exist
if not os.path.isdir(path_t):
    os.makedirs(path_t)
if not os.path.isdir(path_td):
    os.makedirs(path_td)
else:
    print("dir already made. check !! : " )
    sys.exit()

# add text
log = open(logtext, mode='a')
log.write('==== combination of small pulse ===\n')
log.close()

#list-list for read .dat
p_ae    = []
p_de    = []
p_aef   = []
p_def   = []
p_time  = []
p_site  = []
p_index = []

# import points --all sites
print("read files ...")
check_file = 0
for i in range(len(SITE)):
    fp_path = os.path.join(path_small, date[4:8], date[0:4], "smallpulse_" + str(SITE[i]) + "_" + str(date) +".dat") 
    if os.path.isfile(fp_path):
        fp = open(fp_path, 'r')
        for values in fp:
            value = values.strip().split(',')
            p_time.append(float(value[0])) # time
            p_ae.append(float(value[1]))   # pulse value ... E
            p_de.append(float(value[2]))   # pulse value ... ΔE
            p_aef.append(float(value[3]))  # pulse value ... E(filt)
            p_def.append(float(value[4]))  # pulse value ... ΔE(filt)
            p_site.append(int(i+1))        # site number
            p_index.append(int(value[5]))  # index(each site)
        fp.close()
    else:
        print("small pulse file ("+ fp_path +") not found! check!!")
        check_file += 1

if check_file == len(SITE):
   print("small pulse file (" + fp_path + ") not found. skip this site.")
   sys.exit()

# check
if len(p_time) == 0:
    print("No small pulse data. check !!")
    log = open(logtext, mode='a')
    log.write("No small pulse data. check !!\n")
    log.write('== end combination of small pulse =\n')
    log.write('\n')
    log.close()
    sys.exit()
# sort data by time
combined_p = list(zip(p_time, p_ae, p_de, p_aef, p_def, p_site, p_index))
sort_p = sorted(combined_p, key=lambda x: x[0])
ptime, pae, pde, paef, pdef, psite, pindex = zip(*sort_p) # positive
ft = 1 # integer
t_list = np.arange(0, SECONDS_PER_DAY + ft, ft) # SECONDS_PER_DAY: 86400...1day(s)

# combine
n = 0
nj = 0
check_p = 0
print("start make file !")
for i in range(len(t_list)-1): # CAUTION... this program cannot calculate midnight
    n += nj
    npp = int(n-nj)
    if npp<0:
        npp = 0
    pptime  = []
    ppae    = []
    ppde    = []
    ppaef   = []
    ppdef   = []
    ppsite  = []
    ppindex = []
    nj = 0
    for j in range(npp, len(ptime)):
        if ptime[j] < float(t_list[i]):
            continue
        elif ptime[j] >= float(t_list[i]) and ptime[j] < float(t_list[i+1]):
            pptime.append(float(ptime[j]))
            ppae.append(float(pae[j]))
            ppde.append(float(pde[j]))
            ppaef.append(float(paef[j]))
            ppdef.append(float(pdef[j]))
            ppsite.append(int(psite[j]))
            ppindex.append(int(pindex[j]))
        elif ptime[j] >= float(t_list[i+1]):
            break
    if len(pptime) > 0:
        path_txtp = os.path.join(path_td, str(t_list[i])+".dat")
        txtp = np.column_stack((pptime, ppae, ppde, ppaef, ppdef, ppindex, ppsite))
        np.savetxt(path_txtp, txtp, delimiter=',', fmt=['%.6f', '%.6f', '%.6f', '%.6f', '%.6f', '%d', '%d'])
        check_p += 1 
    nj = len(pptime)
print("end make file !")

# add text
log = open(logtext, mode='a')
log.write("file_number : "+str(check_p) + "\n")
log.write('== end combination of small pulse =\n')
log.write('\n')
log.close()

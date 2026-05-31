# Site numbers
SITE = ["01", "2", "3", "4", "5", "6"]

# Time correction for each site
DTLIST = [0, 0, 0, 0, 0, 0]

# Sampling frequency [Hz]
SAMPLING_RATE = 20

# Attenuator [Ω]
ATTENUATOR = 0.5

# Calibration factor 
C_CALIBRATION = [0.51, 0.67, 1.17, 1.57, 0.63, 0.59]

###########################################
#### DO NOT CHANGE ########################
###########################################
# Time length [s]
SECONDS_PER_DAY = 24 * 60 * 60

# Number of samples per day
LEN_TIME = SAMPLING_RATE * SECONDS_PER_DAY

# 1/Attenuator [1/Ω]
RR = 1./ATTENUATOR
###########################################
###########################################

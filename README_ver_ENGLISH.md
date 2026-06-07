# EFM_lightning_estimation
[Japanese version](README.md)  
This code is an analysis program for estimating lightning discharge locations and neutralized charge amounts from atmospheric electric field data obtained by ground-based electric field observations, based on a point charge model (Jacobson and Krider, 1976; Krehbiel et al., 1979; Maier and Krider, 1986).
When publishing results obtained using this code, please cite the following paper.
```text
Iwai et al. (2026), JAE, in preparation.
```

## Code structure
The code files should be used in the following order.
- make_reshapefile.py
- judgement_bigpulse.py
- judgement_smallpulse.py
- search_lightning_time.py
- search_calculation_time.py
- calculate_location.f90
The following code files contain functions and constants.
- const.py
- const.f90
- monopole_model.f90  

## Environment setup
This code was tested in the following environment.
- Python 3.9
- GNU Fortran (GCC) 11.5.0 20240719 (Red Hat 11.5.0-11)

The atmospheric electric field sensor used in the test environment was as follows.
- Boltek EFM-100

## Preparation
Electric field waveform files should be saved for each date and observation site using the following file name format.
```text
Data_Source_<site number>-mmddyyyy.efm
```
Example:
```text
Data_Source_1-01222024.efm
```
Here, `1` represents the site number, and `01222024` represents January 22, 2024.

This code assumes the following directory structure.
```text
.
├── code/                  # Directory containing this code
├── out/                   # Directory for output files
└── data/                  # Directory for input data
    ├── site1/
    │   └── 2024/
    │       └── Data_Source_1-01222024.efm
    ├── site2/
    │   └── 2024/
    │       └── Data_Source_2-01222024.efm
```

Create the `out` and `data` directories at the same level as the `code` directory.
```shell-session
$ mkdir out data
```

In the `data` directory, create directories for each observation site using the following format.
```text
site<site number>
```
Example:
```text
site1
site2
```
Under each site directory, create a directory for each year, and place the corresponding electric field waveform files in that directory.

## How to run the code
Note: This program was designed to perform calculations on a daily basis. In particular, when analyzing time periods around the change of date, observations from the following day are also used. Therefore, it is recommended that `make_reshapefile.py` be run first for the entire analysis period. However, this does not apply if time periods around the change of date do not need to be considered. In that case, the program can still be used without errors.
In `list.txt`, register the dates to be analyzed. In addition, define the necessary settings for the calculation in `const.py` and `const.f90`. See below for the contents of each file.

### list.txt
Enter the dates to be analyzed in `mmddyyyy` format.
```text
01222024
```

### const.py
`const.py` sets the constants used in each Python program.
`const.py` is not a program to be executed directly. However, its contents need to be edited according to the analysis conditions.
Enter the numbers of the site directories created during the preparation step. By default, the code assumes that six sites exist.
```python
SITE = ["1", "2", "3", "4", "5", "6"]
```

If the times are not synchronized among the sites, time offsets can be entered in seconds in the following list. By default, the time offset is set to 0 seconds for all sites.
```python
DTLIST = [0, 0, 0, 0, 0, 0]
```

Enter the sampling rate of the atmospheric electric field sensor. In the test environment, a Boltek EFM-100 was used, so the sampling rate is set to 20 Hz.
```python
SAMPLING_RATE = 20
```

Enter the value of the attenuator used, in Ω.
```python
ATTENUATOR = 0.5
```

If flat-plate calibration was performed, enter the calibration coefficient for each site below. By default, all calibration coefficients are set to 1.
```python
C_CALIBRATION = [1., 1., 1., 1., 1., 1.]
```

The values below usually do not need to be changed. Edit them only if necessary.
The number of seconds per day is defined as follows.
```python
SECONDS_PER_DAY = 24 * 60 * 60
```

The number of data points per day is defined as follows. It is calculated by multiplying the sampling rate by the number of seconds per day.
```python
LEN_TIME = SAMPLING_RATE * SECONDS_PER_DAY
```

The reciprocal of the attenuator is defined as follows.
```python
RR = 1. / ATTENUATOR
```

### const.f90
`const.f90` sets the constants used in the Fortran programs.
`const.f90` is not a program to be executed directly. However, its contents need to be edited according to the analysis conditions.
Enter the numbers of the site directories created during the preparation step. By default, the code assumes that six sites exist.
```fortran
character(len=1), parameter :: site(6) = ["1", "2", "3", "4", "5", "6"]
```

The number of sites is automatically defined from the number of elements in `site`.
```fortran
integer, parameter :: site_num = size(site)
```

Define the center coordinates used as the reference point when converting the output horizontal lightning discharge locations into Cartesian coordinates. Enter the latitude and longitude in degrees.
```fortran
real(rk), parameter :: lon_center = 0.0_rk ! longitude of standard site
real(rk), parameter :: lat_center = 0.0_rk ! latitude of standard site
```

Define the latitude and longitude of each observation site in degrees.
```fortran
real(rk), parameter :: lat_degree(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! degree, latitude of sites
real(rk), parameter :: lon_degree(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! degree, longitude of sites
```

Define the position of each observation site in a Cartesian coordinate system relative to `lon_center` and `lat_center`. The unit is m.
The north-south direction should be defined with **northward positive**, and the east-west direction should be defined with **westward positive**.
```fortran
real(rk), parameter :: site_lat(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, latitude of sites
real(rk), parameter :: site_lon(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, longitude of sites
```

Define the altitude of each observation site in m.
```fortran
real(rk), parameter :: site_alt(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, altitude of sites
```

The values defined after this point are physical constants and usually do not need to be changed.

### make_reshapefile.py
`make_reshapefile.py` is a program that reshapes the electric field waveform files into a format that can be easily used in subsequent analyses.

Run it with the following command.
```shell-session
$ python3 make_reshapefile.py
```

### judgement_bigpulse.py
`judgement_bigpulse.py` is a program that reads the electric field waveform data reshaped by `make_reshapefile.py` and detects pulses associated with large electric field changes.
Run it with the following command.
```shell-session
$ python3 judgement_bigpulse.py
```

### judgement_smallpulse.py
`judgement_smallpulse.py` is a program that reads the electric field waveform data reshaped by `make_reshapefile.py` and detects pulses associated with small electric field changes.
Run it with the following command.
```shell-session
$ python3 judgement_smallpulse.py
```

### search_lightning_time.py
`search_lightning_time.py` is a program that uses the results of `judgement_smallpulse.py` to create an intermediate file used by `search_calculation_time.py`.
Run it with the following command.
```shell-session
$ python3 search_lightning_time.py
```

### search_calculation_time.py
`search_calculation_time.py` is a program that combines the lightning discharge candidate times extracted by `judgement_bigpulse.py` and the electric field changes at each site into a single file.
Run it with the following command.
```shell-session
$ python3 search_calculation_time.py
```

### calculate_location.f90
`calculate_location.f90` is a Fortran program that estimates lightning discharge locations and neutralized charge amounts using the electric field change data created by `search_calculation_time.py`. The calculation uses the observation site information defined in `const.f90` and the point charge model implemented in `monopole_model.f90`.
Compile it with the following command.
```shell-session
$ gfortran -g -fbacktrace -fcheck=all const.f90 monopole_model.f90 calculate_location.f90 -o a.out
```

After compilation, run it with the following command.
```shell-session
$ ./a.out
```
Using `nohup` allows the calculation to continue after the terminal is closed. Standard output and error messages are saved in `log`.
```shell-session
$ nohup ./a.out >& log &
```

## How to read the results
The output text file contains the following values from left to right.
The description below assumes that six observation sites exist. If the number of observation sites changes, the correspondence of the 7th and subsequent columns will change. In general, the last column indicates the number of sites used for location estimation, and the second-to-last column indicates the sum of squared errors.
| Column | Description | Unit / Note |
|---|---|---|
| 1 | Lightning discharge time | s, JST |
| 2 | Representative site number showing the largest electric field change | This value does not necessarily indicate the site with the strict maximum value. Please judge based on the electric field changes output for each site. |
| 3 | Estimated neutralized charge amount | C |
| 4 | Estimated position in the latitudinal direction relative to `lat_center` | m, **northward positive** |
| 5 | Estimated position in the longitudinal direction relative to `lon_center` | m, **westward positive** |
| 6 | Estimated altitude | m |
| 7 | Electric field change at site 1 | V/m, `-999` is output for sites that were not used for location estimation. |
| 8 | Electric field change at site 2 | V/m, `-999` is output for sites that were not used for location estimation. |
| 9 | Electric field change at site 3 | V/m, `-999` is output for sites that were not used for location estimation. |
| 10 | Electric field change at site 4 | V/m, `-999` is output for sites that were not used for location estimation. |
| 11 | Electric field change at site 5 | V/m, `-999` is output for sites that were not used for location estimation. |
| 12 | Electric field change at site 6 | V/m, `-999` is output for sites that were not used for location estimation. |
| 13 | Sum of squared errors | In this analysis, only results with this value smaller than 10000 are used empirically. |
| 14 | Number of sites used for location estimation | This indicates the number of observation sites used for lightning discharge location estimation. |

## References
Iwai et al., 2026, JAE (in preparation)
Jacobson, E. A., & Krider, E. P. (1976). Electrostatic field changes produced by Florida lightning. Journal of the Atmospheric Sciences, 33(1), 103–117. https://doi.org/10.1175/1520-0469(1976)033<0103:EFCPBF>2.0.CO;2
Krehbiel, P. R., Brook, M., & McCrory, R. A. (1979). An analysis of the charge structure of lightning discharges to ground. Journal of Geophysical Research: Oceans, 84(C5), 2432–2456. https://doi.org/10.1029/JC084iC05p02432
Maier, L. M., & Krider, E. P. (1986). The charges that are deposited by cloud-to-ground lightning in Florida. Journal of Geophysical Research: Atmospheres, 91(D12), 13275–13289. https://doi.org/10.1029/JD091iD12p13275

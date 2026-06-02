module const
 use, intrinsic :: iso_fortran_env, only : rk => real64
 implicit none

 ! def
 character(len=1) :: site(6) = ["1", "2", "3", "4", "5", "6"]
 integer, parameter :: site_num = size(site)
 real(rk), parameter :: lon_center = 0.0_rk ! longitude of standard site
 real(rk), parameter :: lat_center = 0.0_rk ! latitude of standard site
 real(rk), parameter :: lat_degree(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! degree, latitude of sites
 real(rk), parameter :: lon_degree(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! degree, longitude of sites
 real(rk), parameter :: site_lat(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, latitude of sites
 real(rk), parameter :: site_lon(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, longitude of site, west distance
 real(rk), parameter :: site_alt(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, altitude of sites
 !###########################################
 !#### DO NOT CHANGE ########################
 !###########################################
 real(rk), parameter :: eo = 8.85418e-12_rk ! F/m, permittivity
 real(rk), parameter :: ek = 1.0059e0_rk ! relative permittivity(air)
 real(rk), parameter :: ea = eo*ek ! permittivity(air)
 real(rk), parameter :: pi = 3.14159265358979323846_rk ! circle ration
 real(rk), parameter :: kk = 1._rk/(2._rk*ea*pi) ! 1/2*pi*"k"
 real(rk), parameter :: po_r = 6378137._rk ! m, semi-major axis
 real(rk), parameter :: re_a = 299.257222101_rk ! 1/flattening
 real(rk), parameter :: m0 = 0.9999e0_rk ! scale factor
 real(rk), parameter :: n0 = 1._rk/(2._rk*re_a - 1._rk)
 real(rk), parameter :: deg180 = 180._rk ! degree
 real(rk), parameter :: err_r = 9999999999.99999e0_rk ! error
 real(rk), parameter :: lamb_init = 0.01_rk ! levenberg_marquardt
 real(rk), parameter :: lamb_fact = 2._rk ! levenberg_marquardt
 real(rk), parameter :: tol = 1.e-6_rk ! levenberg_marquardt
 !###########################################
 !###########################################
 !###########################################
end module const

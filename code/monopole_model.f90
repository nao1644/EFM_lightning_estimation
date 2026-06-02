module monopole_model
 use const
 use, intrinsic :: iso_fortran_env, only : rk => real64
 implicit none

contains
 ! model ~ a point charge model (monopole model) ~
 subroutine point_charge_solve(data_list, lat, lon, alt, num, e)
  ! in
  integer, intent(in) :: num
  real(rk), intent(in) :: data_list(4)
  real(rk), intent(in) :: lat(num), lon(num), alt(num)
  ! out
  real(rk), intent(out) :: e(num) ! ideal dE
  ! for calculation
  real(rk) :: top(num), bottom(num) ! Numerator, Denominator
  ! calculation
  top = (kk*data_list(1)*data_list(4))
  bottom =  (((lat-data_list(2))**2.e0_rk&
            +(lon-data_list(3))**2.e0_rk&
            +(data_list(4))**2.e0_rk)**(3.e0_rk/2.e0_rk))
  e = top/bottom
 end subroutine point_charge_solve

 ! get ERROR(difference) from ideal model
 subroutine calculate_error(data_list, de_obs, lat, lon, alt, num, r)
  ! in
  integer, intent(in) :: num
  real(rk), intent(in) :: data_list(4)
  real(rk), intent(in) :: de_obs(num), lat(num), lon(num), alt(num)
  ! out
  real(rk), intent(inout) :: r(num) ! error
  ! for calculation
  real(rk) :: de_ideal(num) ! from "point_charge_solve"

  ! calculation
  call point_charge_solve(data_list, lat, lon, alt, num, de_ideal)
  r = de_obs - de_ideal !  _2
 end subroutine calculate_error

 ! jacobian matrix
 subroutine jacobian(data_list, lat, lon, alt, num, matrix)
  ! in
  integer, intent(in) :: num
  real(rk), intent(in) :: data_list(4)
  real(rk), intent(in) :: lat(num), lon(num), alt(num)
  ! out
  real(rk), intent(inout) :: matrix(num,4)
  ! for calculation
  real(rk) c
  real(rk) :: d(num), r15(num), r25(num)

  ! calculation
  c = data_list(1)*data_list(4)*kk
  d = (lat-data_list(2))**2.e0_rk&
      +(lon-data_list(3))**2.e0_rk&
      +data_list(4)**2.e0_rk
  r15 = d ** 1.5e0_rk
  r25 = d * r15

  ! J
  matrix(:, 1) = c/data_list(1)/r15
  matrix(:, 2) = -3.e0_rk*c*(data_list(2)-lat)/r25
  matrix(:, 3) = -3.e0_rk*c*(data_list(3)-lon)/r25
  matrix(:, 4) = c/data_list(4)*(d-3.e0_rk*data_list(4)**2)/r25
 end subroutine jacobian

 ! inversion matrix
 subroutine matinv(a, num)
  ! in
  integer, intent(in) :: num
  real(rk), intent(inout) :: a(num, num)
  ! calculation
  real(rk) :: c, dum
  integer :: i, j, k

  ! loop 
  do k = 1, num
     c = a(k, k)
     a(k, k) = 1
     do j = 1, num
        a(k, j) = a(k, j)/c
     enddo
     do i = 1, num
        if( i /= k ) then
           dum = a(i, k)
           a(i, k) = 0.e0_rk
           do j = 1, num
              a(i, j) = a(i, j) - dum*a(k, j)
           enddo
        endif
     enddo
  enddo
 endsubroutine matinv

 ! levenberg_marquardt method
 subroutine levenberg_marquardt(data_list,&
                                de_obs, lat, lon, alt, num,&
                                p0, error, zmin)
  ! in
  integer, intent(in) :: num
  real(rk), intent(in) :: data_list(4)
  real(rk), intent(in) :: de_obs(num), lat(num), lon(num), alt(num)
  real(rk), intent(in) :: zmin
  ! out
  real(rk), intent(inout) :: p0(4)
  real(rk), intent(inout) :: error
  ! for calculation
  real(rk) :: r(num) ! error
  real(rk) lamb
  real(rk) :: jm(num,4), jmt(4,num)
  real(rk) :: h(4,4), hinv(4,4)
  real(rk) :: im(4,4), dm1(4), dm2(4)
  real(rk) :: de_ideal(num) ! from "point_charge_solve"
  integer i, j, k, l

  ! calculation
  p0 = data_list
  lamb = lamb_init
  do l = 1, 100
     call jacobian(p0, lat, lon, alt, num, jm)
     jmt = transpose(jm)
     h = matmul(jmt, jm)
     ! error
     call calculate_error(p0, de_obs, lat, lon, alt, num, r)
     error = 0.e0_rk
     do i = 1, num ! calculate RSS(residual sum of square)
        error = error + r(i)*r(i) ! _1, _2, _4, _5
     end do
     im = 0.e0_rk
     do i = 1, 4 ! I matrix
        im(i, i) = lamb
     end do
     h = h + im
     hinv = h
     call matinv(hinv, 4)
     dm1 = matmul(jmt, r)
     dm2 = matmul(hinv, dm1)
     p0 = p0 + dm2

     !restriction
     ! Q [C]
     if ( p0(1) >= 5.e2_rk ) then
             p0(1) = 1.e1_rk
     else if ( p0(1) <= 1.e-2_rk ) then
             p0(1) = 1.e-2_rk
     end if
     ! Z [m]
     if ( p0(4) <= zmin ) then
             p0(4) = zmin
     else if ( p0(4) >= 1.5e4_rk ) then
             p0(4) = 2.e3_rk
     end if

     ! NEXT step
     if (maxval(abs(dm2)) < tol) then
             exit
     else
             lamb = lamb*lamb_fact
     end if
  end do
 end subroutine levenberg_marquardt

 ! latitude, logitude to cartesian coordinates
 subroutine latlon_xy(lon_1, lat_1, lon_2, lat_2, dx, dy)
  ! in
  real(rk), intent(in) :: lon_1, lat_1, lon_2, lat_2
  ! out
  real(rk), intent(out) :: dy, dx
  ! for calculation
  real(rk) :: a(5), b(6)
  real(rk) rlat_1, rlon_1, rlat_2, rlon_2
  real(rk) dlat, dlon
  real(rk) s, bb
  real(rk) t, tv, lac, las, xi, et
  real(rk) x, y
  integer ii

  ! calculation
  ! radian
  rlat_1 = lat_1*pi/deg180
  rlon_1 = lon_1*pi/deg180
  rlat_2 = lat_2*pi/deg180
  rlon_2 = lon_2*pi/deg180
  ! difference
  dlat   = rlat_1 - rlat_2
  dlon   = rlon_1 - rlon_2
  ! arupha
   a(1) = (1.e0_rk/2.e0_rk)*n0 - (2.e0_rk/3.e0_rk)*(n0**2)&
         + (5.e0_rk/16.e0_rk)*(n0**3) + (41.e0_rk/180.e0_rk)*(n0**4) - (127.e0_rk/288.e0_rk)*(n0**5)
  a(2) = (13.e0_rk/48.e0_rk)*(n0**2) - (3.e0_rk/5.e0_rk)*(n0**3)&
         + (557.e0_rk/1440.e0_rk)*(n0**4) + (281.e0_rk/630.e0_rk)*(n0**5)
  a(3) = (61.e0_rk/240.e0_rk)*(n0**3) - (103.e0_rk/140.e0_rk)*(n0**4) + (15061.e0_rk/26880.e0_rk)*(n0**5)
  a(4) = (49561.e0_rk/161280.e0_rk)*(n0**4) - (179.e0_rk/168.e0_rk)*(n0**5)
  a(5) = (34729.e0_rk/80640.e0_rk)*(n0**5)
  b(1) = 1.e0_rk + (n0**2)/4.e0_rk + (n0**4)/64.e0_rk
  b(2) = -1.e0_rk*(3.e0_rk/2.e0_rk)*(n0 - (n0**3)/8.e0_rk - (n0**5)/64.e0_rk)
  b(3) = (15.e0_rk/16.e0_rk)*(n0**2 - (n0**4)/4.e0_rk)
  b(4) = -1.e0_rk*(35.e0_rk/48.e0_rk)*(n0**3 - (5.e0_rk/16.e0_rk)*(n0**5))
  b(5) = (315.e0_rk/512.e0_rk)*(n0**4)
  b(6) = -1.e0_rk*(693.e0_rk/1280.e0_rk)*(n0**5)

  ! s
  s = m0*po_r*(b(1)*rlat_2)/(1.e0_rk + n0)
  do ii = 1, 6
     s = s + m0*po_r*(b(ii)*sin(2.e0_rk*(ii - 1)*rlat_2))/(1.e0_rk + n0)
  end do
  ! A var
  bb = m0*po_r*b(1)/(1.e0_rk + n0)
  ! dx, dy
  t   = sinh(atanh(sin(rlat_1))&
        -2.e0_rk*sqrt(n0)*atanh(2.e0_rk*sqrt(n0)*sin(rlat_1)/(1.e0_rk + n0))/(1.e0_rk + n0))
  tv  = sqrt(1.e0_rk + t**2)
  las = sin(dlon)
  lac = cos(dlon)
  xi  = atan(t/lac)
  et  = atanh(las/tv)
  x = bb*xi - s
  do ii = 1, 5
     x = x + bb*(a(ii)*sin(2.e0_rk*ii*xi)*cosh(2.e0_rk*ii*et))
  end do
  y = bb*et
  do ii = 1, 5
     y = y + bb*(a(ii)*cos(2.e0_rk*ii*xi)*sinh(2.e0_rk*ii*et))
  end do
  dy = x
  dx = -1.e0_rk*y ! caution!! ...west distace
 end subroutine latlon_xy

end module monopole_model

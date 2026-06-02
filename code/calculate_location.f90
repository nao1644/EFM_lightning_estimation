program calculate_location
  use monopole_model
  use const
  use, intrinsic :: iso_fortran_env, only : rk => real64
  implicit none

  ! path
  integer :: fd = 11, fo = 12, fl = 13
  character(len=8) date
  character(len=1024) path_time
  character(len=1024) dat_pathorigin, dat_pathyear, dat_pathday, dat_path1
  character(len=1024) get_path, logtex0, logtexy, logtext
  character(len=1024) path_timefile
  integer io, ios, ioc
  ! read data
  integer dir_status
  character(len=1024) :: dir_list = "./dir_list.txt"
  character(len=1024) command
  character(len=1024) out_fmt
  integer :: fa = 16, fs1 = 17
  character(len=1024) time_site
  real(rk) time_obs
  integer aim
  real(rk), dimension(site_num) :: site_de
  integer, dimension(site_num) :: site_de_index
  integer, dimension(site_num) :: index_check
  ! set data
  integer :: set_num = 0
  integer set_loop
  real(rk), dimension(:), allocatable :: site_de_loop, site_alt_loop, site_lon_loop, site_lat_loop
  ! set range for loop
  integer i, j, k, l, m
  real(rk), dimension(1) :: dq_set = (/ 1.e1_rk /)
  real(rk), dimension(:), allocatable :: lon_list, lat_list
  real(rk), dimension(:,:), allocatable :: lon_set, lat_set
  real(rk), dimension(5) :: alt_set = (/ 5.e3_rk, 7.5e3_rk, 8.e3_rk, 9.e3_rk, 1.e4_rk /)
  real(rk), dimension(4) :: a1
  real(rk), dimension(4) :: p0, p1
  real(rk) err_old1
  real(rk) err_r1
  real(rk) latin, lonin
  real(rk) :: altlimit = 2.e3_rk

  ! read date
  open(fd, file='./list.txt', status='old')
  read(fd, *, iostat=io) date
  close(fd)
  ! path
  path_time = '../out/timelist/' // date(5:8) // '/' // date(1:4)
  dat_pathorigin = '../out/location/'
  dat_pathyear = trim(dat_pathorigin) // date(5:8) // '/'
  dat_pathday = trim(dat_pathyear) // date(1:4) // '/'
  dat_path1 = trim(dat_pathday) // 'full_location_' // date(1:4) // '.txt'
  get_path = '../out/for_calculation/' // date(5:8) // '/' // date(1:4)
  logtex0 = '../out/log/'
  logtexy = trim(logtex0) // date(5:8) // '/'
  logtext = trim(logtexy) // 'logtext_' // date // '.txt'

  ! log
  open(fo, file=logtext, position='append')
  write(fo, *) '===== start calculate location ===='
  close(fo)
  ! make path
  if (access(dat_pathorigin, "") /= 0) then
          write(command, '(A, A)') 'mkdir ', trim(dat_pathorigin)
          dir_status = system(command)
  end if
  if (access(dat_pathyear, "") /= 0) then
          write(command, '(A, A)') 'mkdir ', trim(dat_pathyear)
          dir_status = system(command)
  end if
  if (access(dat_pathday, "") /= 0) then
          write(command, '(A, A)') 'mkdir ', trim(dat_pathday)
          dir_status = system(command)
  end if
  !file_status = access(dir_list, "")
  !if (file_status /= 0) then
          write(command, '(A, A, A, A)') 'ls ', trim(get_path), ' > ', trim(dir_list)
          dir_status = system(command)
  !else
  !        dir_status = 0
  !end if
  if (dir_status /= 0) then ! NO directory of the date.
          ! log
          open(fo, file=logtext, position='append')
          write(fo, *) 'NO data of lightning.'
          write(fo, *) '===== end calculate location ====='
          close(fo)
          stop
  else
          open(fl, file=dir_list, status='old', action='read')
  end if

  ! read filelist and calculation
  do 
     ! read filelist
     read(fl, '(A)', iostat=io) time_site
     ! check end or read & remove origin file(for_calculation)
     if (IS_IOSTAT_END(io)) then
             exit ! end of filelist
     else
             path_timefile = trim(get_path) // '/' // trim(time_site)
             open(fa, iostat=ios, file=path_timefile, status='old', action='read')
             if (ios /= 0) then ! already removed file
                     cycle
             else
                     ! read
                     read(fa, *) time_obs, aim, site_de, site_de_index, index_check
                     close(fa, iostat=ioc, status='delete') ! close and delete file
                     if (ios /= 0) then ! already removed file
                             cycle
                     end if
             end if
     end if
     ! set data
     set_num = 0
     do i = 1, site_num
        site_de(i) = 1.e3_rk * site_de(i) ! kV to V
        if (site_de(i) >= 0.e0_rk) then
                set_num = set_num + 1
        else
                site_de(i) = -999.e0_rk
        end if
     end do
     ! set range
     allocate(site_de_loop(set_num))
     allocate(site_alt_loop(set_num))
     allocate(site_lat_loop(set_num))
     allocate(site_lon_loop(set_num))
     set_loop = 0
     do i = 1, site_num
        if (site_de(i) >= 0.e0_rk) then
                set_loop = set_loop + 1
                site_de_loop(set_loop) = site_de(i)
                site_lat_loop(set_loop) = site_lat(i)
                site_lon_loop(set_loop) = site_lon(i)
                site_alt_loop(set_loop) = site_alt(i)
        end if
     end do

     ! set range
     allocate(lon_list(11))
     allocate(lat_list(11))
     lon_list = (/ (lon_degree(aim)+1.e-1_rk*i, i = -5, 5) /)
     lat_list = (/ (lat_degree(aim)+1.e-1_rk*i, i = -5, 5) /)
     allocate(lon_set(size(lon_list), size(lat_list)))
     allocate(lat_set(size(lon_list), size(lat_list)))
     do i = 1, size(lon_list)
        do j = 1, size(lat_list)
           call latlon_xy(lon_list(i), lat_list(j),&
                          lon_center, lat_center,&
                          lon_set(i, j), lat_set(i, j))
        end do
     end do

     ! calculation
     err_r1 = err_r
     a1 = -999.e0_rk
     do i = 1, size(lon_list)
        do j = 1, size(lat_list)
           do k = 1, size(dq_set)
              do l = 1, size(alt_set)
                 latin = lat_set(i, j)
                 lonin = lon_set(i, j)
                 p0 = (/ dq_set(k), latin, lonin, alt_set(l) /)
                 do m = 1, 50
                    call levenberg_marquardt(p0, site_de_loop,&
                                             site_lat_loop, site_lon_loop, site_alt_loop, set_loop,&
                                             p1, err_old1, altlimit) ! NOT use altlimit
                    p0 = p1
                 end do
                 ! best fit
                 if (err_old1 < err_r1) then
                          err_r1 = err_old1
                          a1 = p1
                 end if
              end do
           end do
        end do
     end do

     ! save
     open(fs1, file=dat_path1, position='append')
     write(out_fmt, '(A, I0, A)') '(F10.3, 1X, I0, 1X, F12.6, 3(1X, F15.6), ', site_num, &
                                  '(1X, F18.8), 1X, F20.8, 1X, I0)'
     write(fs1, out_fmt) time_obs, aim, a1(1), a1(2:4), site_de, err_r1, set_num

     ! close
     close(fs1)
     ! end deallocate
     deallocate(lon_list, lat_list)
     deallocate(lon_set, lat_set)
     deallocate(site_de_loop, site_lat_loop, site_lon_loop, site_alt_loop)
  end do
  write(*, *) "end."
  close(fl)

  ! log
  open(fo, file=logtext, position='append')
  write(fo, *) '===== end calculate location ====='
  close(fo)

end program calculate_location

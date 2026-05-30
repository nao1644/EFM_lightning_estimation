# EFM_lightning_estimation
地上電場観測により得られた大気電場のデータから、発雷位置及び中和電荷量を点電荷モデル(Jacobson and Krider, 1976; Krehbiel et al., 1979; Maier and Krider, 1986)を使用して導出します。本コードを使用する際はIwai et al., 2026, JAEの引用をお願いします。

## コードの構成
コードは以下の順番で使用します。
- make_reshapefile.py
- judgement_bigpulse.py
- judgement_smallpulse.py
- search_lightning_time.py
- search_calculation_time.py
- calculate_location.f90

## 環境設定
テスト環境で使用したプログラミング言語は以下のとおりです。
- Python 3.9
- GNU Fortran (GCC) 11.5.0 20240719 (Red Hat 11.5.0-11)

## コードの動かし方
### 事前準備


### make_reshapefile.py


### judgement_bigpulse.py


### judgement_smallpulse.py


### search_lightning_time.py


### search_calculation_time.py


### calculate_location.f90


## 参考文献
Iwai et al., 2026, JAE 

Jacobson, E. A., & Krider, E. P. (1976). Electrostatic field changes produced by Florida lightning. Journal of the Atmospheric Sciences, 33(1), 103–117. [https://doi.org/10.1175/1520-0469(1976)033<0103:EFCPBF>2.0.CO;2](https://doi.org/10.1175/1520-0469(1976)033<0103:EFCPBF>2.0.CO;2)

Krehbiel, P. R., Brook, M., & McCrory, R. A. (1979). An analysis of the charge structure of lightning discharges to ground. Journal of Geophysical Research: Oceans, 84(C5), 2432–2456. [https://doi.org/10.1029/JC084iC05p02432](https://doi.org/10.1029/JC084iC05p02432) 

Maier, L. M., & Krider, E. P. (1986). The charges that are deposited by cloud-to-ground lightning in Florida. Journal of Geophysical Research: Atmospheres, 91(D12), 13275–13289. [https://doi.org/10.1029/JD091iD12p13275](https://doi.org/10.1029/JD091iD12p13275)


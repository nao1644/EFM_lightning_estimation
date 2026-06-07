# EFM_lightning_estimation
[English version of this README](README_ver_ENGLISH.md)  
本コードは、地上電場観測により得られた大気電場データを用いて、発雷位置および中和電荷量を点電荷モデル（Jacobson and Krider, 1976; Krehbiel et al., 1979; Maier and Krider, 1986）に基づいて推定するための解析コードです。
本コードを使用した成果を公表する際には、以下の論文を引用してください。
```text
Iwai et al. (2026), JAE, in preparation.
```

## コードの構成
コードは以下の順番で使用します。
- make_reshapefile.py
- judgement_bigpulse.py
- judgement_smallpulse.py
- search_lightning_time.py
- search_calculation_time.py
- calculate_location.f90

以下のコードは関数や定数を格納するコードです。
- const.py
- const.f90
- monopole_model.f90  

## 環境設定
本コードは以下の環境で動作確認を行いました。
- Python 3.9
- GNU Fortran (GCC) 11.5.0 20240719 (Red Hat 11.5.0-11)

使用している大気電場観測測器は以下の測器です。
- Boltek 社製 EFM-100

## 事前準備
電場波形ファイルは、日付ごと・観測サイトごとに以下のファイル名形式で保存してください。
```text
Data_Source_<サイト番号>-mmddyyyy.efm
```
例：
```text
Data_Source_1-01222024.efm
```

ここで、`1` はサイト番号、`01222024` は 2024 年 1 月 22 日を表します。
本コードでは、以下のディレクトリ構造を想定しています。
```text
.
├── code/                  # 本コード群を配置するディレクトリ
├── out/                   # 出力ファイルを保存するディレクトリ
└── data/                  # 入力データを保存するディレクトリ
    ├── site1/
    │   └── 2024/
    │       └── Data_Source_1-01222024.efm
    ├── site2/
    │   └── 2024/
    │       └── Data_Source_2-01222024.efm
```

`out` ディレクトリおよび `data` ディレクトリは、`code` ディレクトリと同じ階層に作成してください。
```shell-session
$ mkdir out data
```

また、`data` ディレクトリの中には、観測サイトごとに以下の形式でディレクトリを作成してください。
```text
site<サイト番号>
```

例：
```text
site1
site2
```
各サイトディレクトリの下には年ごとのディレクトリを作成し、その中に対応する電場波形ファイルを配置してください。

## コードの動かし方
注意：本プログラムは、1日単位での計算を想定して作成されています。特に、日付が変わる時間帯を解析する場合は、翌日の観測値も使用するため、最初に `make_reshapefile.py` を解析対象期間全体に対して実行することを推奨します。ただし、日付が変わる時間帯を考慮しない場合は、この限りではありません。その場合でも、プログラムはエラーなく使用できます。
`list.txt`では解析対象の日付を登録します。また、`const.py`と`const.f90`で計算に必要な定義を行います。それぞれの中身については以下を参照してください。

### list.txt
mmddyyyyで解析対象の日付を入力してください。
```text
01222024
```
### const.py
`const.py`では、各 Python プログラム内で使用する定数を設定します。
`const.py`は直接実行するプログラムではありません。ただし、解析条件に応じて内容を編集する必要があります。

事前準備で作成したサイトディレクトリの番号を、以下に入力してください。デフォルトでは、6つのサイトが存在することを想定しています。
```python
SITE = ["1", "2", "3", "4", "5", "6"]
```

各サイトで時刻が同期されていない場合は、以下のリストに秒単位で時刻のずれを入力できます。デフォルトでは、すべてのサイトで時刻のずれを 0 秒としています。
```python
DTLIST = [0, 0, 0, 0, 0, 0]
```

大気電場観測測器のサンプリングレートを以下に入力してください。テスト環境では Boltek 社製 EFM-100 を使用しているため、20 Hz としています。
```python
SAMPLING_RATE = 20
```

使用したアッテネータの値を Ω 単位で入力してください。
```python
ATTENUATOR = 0.5
```

平面校正を行った場合は、以下に各サイトの校正係数を入力してください。デフォルトでは、すべての校正係数を 1 としています。
```python
C_CALIBRATION = [1., 1., 1., 1., 1., 1.]
```

これ以降の値は、通常は変更する必要はありません。必要に応じて編集してください。
1日あたりの秒数を定義しています。

```python
SECONDS_PER_DAY = 24 * 60 * 60
```

1日あたりのデータ点数を定義しています。サンプリングレートに 1日あたりの秒数を掛けることで計算されます。
```python
LEN_TIME = SAMPLING_RATE * SECONDS_PER_DAY
```

アッテネータの逆数を定義しています。
```python
RR = 1. / ATTENUATOR
```

### const.f90
`const.f90`では、Fortran プログラム内で使用する定数を設定します。
`const.f90`は直接実行するプログラムではありません。ただし、解析条件に応じて内容を編集する必要があります。

事前準備で作成したサイトディレクトリの番号を、以下に入力してください。デフォルトでは、6つのサイトが存在することを想定しています。
```fortran
character(len=1), parameter :: site(6) = ["1", "2", "3", "4", "5", "6"]
```

サイト数は、`site`の要素数から自動的に定義されます。
```fortran
integer, parameter :: site_num = size(site)
```

出力される水平方向の発雷位置を直交座標に変換する際に、基準点として使用する中心座標を定義します。緯度・経度は度単位で入力してください。
```fortran
real(rk), parameter :: lon_center = 0.0_rk ! longitude of standard site
real(rk), parameter :: lat_center = 0.0_rk ! latitude of standard site
```

各観測サイトの緯度・経度を度単位で定義します。
```fortran
real(rk), parameter :: lat_degree(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! degree, latitude of sites
real(rk), parameter :: lon_degree(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! degree, longitude of sites
```

各観測サイトの位置を、`lon_center`および `lat_center`を基準とした直交座標系で定義します。単位は m です。
なお、南北方向は**北向きを正**、東西方向は**西向きを正**として定義してください。
```fortran
real(rk), parameter :: site_lat(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, latitude of sites
real(rk), parameter :: site_lon(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, longitude of sites
```

各観測サイトの高度を m 単位で定義します。
```fortran
real(rk), parameter :: site_alt(site_num) = [0._rk, 0._rk, 0._rk, 0._rk, 0._rk, 0._rk] ! m, altitude of sites
```
これ以降に定義されている値は物理定数であるため、通常は変更する必要はありません。

### make_reshapefile.py
`make_reshapefile.py`は、電場波形ファイルを後続の解析で使用しやすい形式に整形するプログラムです。
以下のコマンドで動作します。
```shell-session
$ python3 make_reshapefile.py
```

### judgement_bigpulse.py
`judgement_bigpulse.py`は、`make_reshapefile.py`によって整形された電場波形データを読み込み、大きな電場変化を伴うパルスを検出するプログラムです。
以下のコマンドで動作します。
```shell-session
$ python3 judgement_bigpulse.py
```

### judgement_smallpulse.py
`judgement_smallpulse.py`は、`make_reshapefile.py`によって整形された電場波形データを読み込み、小さな電場変化を伴うパルスを検出するプログラムです。
以下のコマンドで動作します。
```shell-session
$ python3 judgement_smallpulse.py
```

### search_lightning_time.py
`search_lightning_time.py`は、`judgement_smallpulse.py`の結果を用いて、`search_calculation_time.py`で使用する中間ファイルを作成するプログラムです。
以下のコマンドで動作します。
```shell-session
$ python3 search_lightning_time.py
```


### search_calculation_time.py
`search_calculation_time.py`は、`judgement_bigpulse.py`で抽出された発雷候補時刻をもとに、発雷時刻および各サイトにおける電場変化量を1つのファイルにまとめるプログラムです。
以下のコマンドで実行します。
```shell-session
$ python3 search_calculation_time.py
```


### calculate_location.f90
`calculate_location.f90`は、`search_calculation_time.py`で作成した電場変化データを用いて発雷位置および中和電荷量を推定するFortranプログラムです。計算には、`const.f90`に定義された観測サイト情報および `monopole_model.f90`に実装された点電荷モデルを使用します。
以下のコマンドでコンパイルします。
```shell-session
$ gfortran -g -fbacktrace -fcheck=all const.f90 monopole_model.f90 calculate_location.f90 -o a.out
```
コンパイル後、以下のコマンドで実行します。
```shell-session
$ ./a.out
```
`nohup`を使用することで、ターミナルを閉じた後も計算を継続できます。標準出力およびエラーメッセージは `log`に保存されます。
```shell-session
$ nohup ./a.out >& log &
```
## 結果の見方
出力されたテキストファイルには、左から順に以下の値が出力されます。
以下では、6つの観測サイトが存在する場合を想定しています。観測サイト数が変わった場合、7列目以降の対応が変わるため注意してください。一般に、最後の列は標定に使用したサイト数を示し、最後から2番目の列は二乗和誤差を示します。
| 列 | 内容 | 単位・補足 |
|---|---|---|
| 1 | 発雷時刻 | s, JST |
| 2 | 最大の電場変化量を示す代表サイト番号 | この値は必ずしも厳密な最大値を示すサイトではありません。実際に出力される各サイトの電場変化量を確認して判断してください。 |
| 3 | 標定された中和電荷量 | C |
| 4 | 標定されたlat_centerを基準とした緯度方向の位置 | m, **北向きを正**とします。 |
| 5 | 標定されたlon_centerを基準とした経度方向の位置 | m, **西向きを正**とします。 |
| 6 | 標定された高度 | m |
| 7 | サイト1での電場変化量 | V/m, 標定には使用していないサイトは`-999` が出力されます。 |
| 8 | サイト2での電場変化量 | V/m, 標定には使用していないサイトは`-999` が出力されます。 |
| 9 | サイト3での電場変化量 | V/m, 標定には使用していないサイトは`-999` が出力されます。 |
| 10 | サイト4での電場変化量 | V/m, 標定には使用していないサイトは`-999` が出力されます。 |
| 11 | サイト5での電場変化量 | V/m, 標定には使用していないサイトは`-999` が出力されます。 |
| 12 | サイト6での電場変化量 | V/m, 標定には使用していないサイトは`-999` が出力されます。 |
| 13 | 二乗和誤差 | 本解析では、経験的にこの値が 10000 より小さい結果のみを使用しています。 |
| 14 | 標定に使用したサイト数 | 発雷位置推定に使用された観測サイト数を示します。 |


## 参考文献
Iwai et al., 2026, JAE  (in preparation)

Jacobson, E. A., & Krider, E. P. (1976). Electrostatic field changes produced by Florida lightning. Journal of the Atmospheric Sciences, 33(1), 103–117. [https://doi.org/10.1175/1520-0469(1976)033<0103:EFCPBF>2.0.CO;2](https://doi.org/10.1175/1520-0469(1976)033<0103:EFCPBF>2.0.CO;2)

Krehbiel, P. R., Brook, M., & McCrory, R. A. (1979). An analysis of the charge structure of lightning discharges to ground. Journal of Geophysical Research: Oceans, 84(C5), 2432–2456. [https://doi.org/10.1029/JC084iC05p02432](https://doi.org/10.1029/JC084iC05p02432) 

Maier, L. M., & Krider, E. P. (1986). The charges that are deposited by cloud-to-ground lightning in Florida. Journal of Geophysical Research: Atmospheres, 91(D12), 13275–13289. [https://doi.org/10.1029/JD091iD12p13275](https://doi.org/10.1029/JD091iD12p13275)

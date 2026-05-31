# EFM_lightning_estimation
地上電場観測により得られた大気電場のデータから、発雷位置及び中和電荷量を点電荷モデル(Jacobson and Krider, 1976; Krehbiel et al., 1979; Maier and Krider, 1986)を使用して導出します。本コードを使用する際は、Iwai et al., 2026, JAEの引用をお願いします。

## コードの構成
コードは以下の順番で使用します。
- make_reshapefile.py
- judgement_bigpulse.py
- judgement_smallpulse.py
- search_lightning_time.py
- search_calculation_time.py
- calculate_location.f90

## 環境設定
本コードは以下の環境で動作確認を行いました。
- Python 3.9
- GNU Fortran (GCC) 11.5.0 20240719 (Red Hat 11.5.0-11)

使用している多岐電場観測測器は以下の測器です。
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
├── code/                  # 本コードを配置するディレクトリ
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
注意：本プログラムは、1日単位での計算を想定して作成されています。特に、日付が変わる時間帯を解析する場合は、翌日の観測値も使用するため、最初に `make_reshape.py` を解析対象期間全体に対して実行することを推奨します。ただし、日付が変わる時間帯を考慮しない場合は、この限りではありません。その場合でも、プログラムはエラーなく使用できます。

### const.py
`const.py` では、各 Python プログラム内で使用する定数を設定します。
`const.py` は、以下のように直接実行するプログラムではありません。
```shell-session
$ python3 const.py
```
ただし、解析条件に応じて内容を編集する必要があります。

事前準備で作成したサイトディレクトリの番号のみを、以下に入力してください。デフォルトでは、6つのサイトが存在することを想定しています。
```python
SITE = ["1", "2", "3", "4", "5", "6"]
```

各サイトで時刻が同期されていない場合は、以下のリストに秒単位で時刻のずれを入力できます。デフォルトでは、すべてのサイトで時刻のずれは 0 秒としています。
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


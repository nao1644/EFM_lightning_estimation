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
本コードは以下の環境で動作確認を行いました。
- Python 3.9
- GNU Fortran (GCC) 11.5.0 20240719 (Red Hat 11.5.0-11)

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
注意：本プログラムは１日単位毎での計算を想定して作成されています。特に、日付が変わる時間帯については翌日の観測値も使用するため、まず初めにmake_reshape.pyを解析対象期間全体にわたって使用することを推奨します。しかし、日付が変わる時間帯について考慮しなくても良い場合はその限りではなく、エラーなくプログラムを使用することが可能です。
### const.py
このプログラムでは使用するpythonプログラム内で使用する定義を設定します。
プログラムとして直接python3 const.pyとはしませんが、編集を行う必要があります。

事前準備で指定したディレクトリの番号をここに入力します。デフォルトでは6つのサイトが存在する想定となっています。
```python
SITE = ["1", "2", "3", "4", "5", "6"]
```

各サイトで時刻が同期されていない場合、このlist内に秒単位で時間のずれを入力することが可能です。デフォルトでは時刻のずれは0となっています。
```python
DTLIST = [0, 0, 0, 0, 0, 0]
```

大気電場観測測器のサンプリングレートをここに入力します。
テスト環境ではBoltek社製 EFM-100を使用しているため、20 Hzとなっています。
```python
SAMPLING_RATE = 20
```

使用したアッテネータの単位をΩで入力します。
```python
ATTENUATOR = 0.5
```

平面校正を行った場合、ここに校正係数を入れてください。デフォルトでは全て1になっています。
```python
C_CALIBRATION = [1., 1., 1., 1., 1., 1.]
```

以下は変える必要がありませんが、必要に応じて編集してください。 

１日あたりの秒数を定義しています。
```python
SECONDS_PER_DAY = 24 * 60 * 60
```
サンプリングレートとかけることで、存在するデータ点数を定義しています。
```python
LEN_TIME = SAMPLING_RATE * SECONDS_PER_DAY
```

アッテネータの逆数を定義しています。
```python
RR = 1./ATTENUATOR
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


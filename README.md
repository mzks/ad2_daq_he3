# Memo: DAQ for He-3 Counter

Author Keita Mizukoshi (Kobe Univ.)

 Jun. 14 2020



## 概要

He-3比例計数管を用いた地下での環境中性子測定のためのデータ収集系を制作, 試験した.

データ収集においては, 小型で安定して動作すること, 低 sampling rateで長い波形を取得できることが求められる. 一方で, 地下環境では中性子のレートは非常に低いため, データ取得レート性能は放射線源をもちいた較正に耐えうる程度でよい. そのため2万円強で購入できるUSBオシロスコープ Analog Discovery 2 とその制御用のRaspberry pi 4でDAQを制作し, テストパルスを入れて動作を試験した.

Analog Discovery 2はUSBでraspberry pi4に接続し, 通信, 給電をおこなう. 今回の環境では問題にならなかったが, 電力供給が不足する場合にはAnalog Discovery 2にDCで電源供給することも可能である.

試験に用いたソフトウェアは `/home/pi/ad2` 以下を参照されたい. 特に`daq/daq.py` がAnalog Discovery 2と通信し波形取得するスクリプトである. その他のスクリプトについては後述する.

## Prerequirement

  - Adept 2 runtime
  - WaveForms

## `daq.py`

本スクリプトはAnalog Discovery 2と通信し, トリガーを超えた信号についてデータを取得, ASCIIファイルとして保存するpythonスクリプトである. コマンドラインからオプションで制御可能なので, 長期ランを行う際にはこのスクリプトを連続して実行する仕組みを作ればよい. オプションの内容は`-h`で確認可能である.

```
pi@raspberrypi:~/ad2/daq $ ./daq.py -h
usage: daq.py [-h] [-v VERBOSE] [-d DIRNAME] [-f FILENAME] [-t TRIGGER_LEVEL]
              [-n] [-p TIME_POSITION] [-s SAMPLING] [-e ENTRIES]

AD2 DAQ in CUI

optional arguments:
  -h, --help            show this help message and exit
  -v VERBOSE, --verbose VERBOSE
                        verbose level
  -d DIRNAME, --dirname DIRNAME
                        Directory name
  -f FILENAME, --filename FILENAME
                        File name
  -t TRIGGER_LEVEL, --trigger_level TRIGGER_LEVEL
                        Trigger Level (V)
  -n, --negative_edge   Negative edge for trigger
  -p TIME_POSITION, --time_position TIME_POSITION
                        Center of time position (sec.)
  -s SAMPLING, --sampling SAMPLING
                        Sampling frequency (Hz)
  -e ENTRIES, --entries ENTRIES
                        Number of events
```

DIRNAMEは最後の/を含むこと. また, 負の値を入力する際はオプションと区別するために"で囲む必要がある.



実行すると 'DIRNAME''FILENAME'.txtというオプションの設定情報を書き出すファイルと,波形データを含むファイル 'DIRNAME''FILENAME'.xxxx.dat (1000イベントごとにxxxxがインクリメント)が生成される.

実行例

```
pi@raspberrypi:~/ad2/daq $ ./daq.py -f test1 -t "0.1" -e 100
DWF Version: b'3.12.2'
Opening first device
Start DAQ
Stop DAQ
pi@raspberrypi:~/ad2/daq $ ./daq.py -f test2 -t "-0.1" -n -e 100
DWF Version: b'3.12.2'
Opening first device
Start DAQ
Stop DAQ
```

設定情報ファイル

```
pi@raspberrypi:~/ad2/data/test1 $ cat test1.txt
Dir name    : /home/pi/ad2/data/test1/
File name   : test1
N events    : 100
Trigger (V) : c_double(0.1)
Trig. Edge  : Positive
Sampling Hz : c_double(10000000.0)
time pos.(s): c_double(0.0)

pi@raspberrypi:~/ad2/data/test1 $ cat test2.txt
Dir name    : /home/pi/ad2/data/test1/
File name   : test2
N events    : 100
Trigger (V) : c_double(-0.1)
Trig. Edge  : Negative
Sampling Hz : c_double(10000000.0)
time pos.(s): c_double(0.0)
```

波形ファイル

波形ファイルの出力はイベントごとに,イベント番号と大まかなTrigger timingのタイムスタンプを並べたheaderとそれに続く8192行の波高値 (V), ファイルを書き込み終わった時間のタイムスタンプのfooterで構成されている. 以下に例を示す. これらのタイムスタンプから大まかなlivetimeが計算できる.

```
#. 0  1592122600.627274
-0.0037076929163779534
-0.0033708782669286284
-0.0037076929163779534
-0.0030340636174793034
略
-0.0037076929163779534
-0.0033708782669286284
-0.0030340636174793034
-0.0033708782669286284
1592122600.699681
#. 1  1592122600.706305
-0.0037076929163779534
略
-0.0033708782669286284
-0.004044507565827278
1592122600.767549
```



## こまごまとしたスクリプト

Raspberry piには大きなストレージがないため, USBでストレージを接続して用いることが良いと思われる. 今回は試験のために, 取得データを順次ネットワーク上のデータ収集PCにコピーし, コピーが確認できれば削除することにした. それらのスクリプトは`run_script/autocopy.sh`と`run_script/safe_rm.py`である. 必要に応じて適宜参照されたい.



## 試験結果

![テストパルスを入れ取得した波形例](./figure/sample.png)

テストパルスを入れ波形を取得した. 1kHzでテストパルスを導入したところ, およそ20Hzでデータ取得ができた. Sampling を変えることで, 適切な時間幅でデータ取得ができることを確認した.

# Script for Drone operating
## 1. 概要
大学の集中講義で使用するドローンを操作するためのスクリプトをまとめたもの。

## 2. 動作環境
- 使用言語：python 3.7.0
- 主な使用ライブラリ：opencv-python

## 3. 使用するドローン
Telloの小型ドローン（詳細は今後追記予定）

## 4. 構成
以下の3つのスクリプトを用いる。
- drone_operator.py
    - ドローンの操縦のみを行うスクリプト
- drone_qr.py
    - 土論の操縦を行いながら、qrコードの検出を行うスクリプト
- drone_lintrace.py
    - ドローンを用いたライントレースを行うためのスクリプト

## 5. 実行方法
### 5.1 環境構築
```
pip install -r requirements.txt
```

### 5.2 .envの作成
`.env_example`を参考に、.envファイルを作成してください。

### 5.3 ドローン操作スクリプトの実行
```
python drone_operator.py
```
```
python drone_qr.py
```
```
python drone_lintrace.py
```

## 6. ドローンの操作方法
### 6.1 基本操作
```
j : 離陸    k : 着陸
h : 上昇    l : 下降
w : 前進    s : 後進
a : 左進    d : 右進
u : 左回転  i : 右回転
m : 速度変更
q : 終了（※必ず着陸してから終了してください）
```





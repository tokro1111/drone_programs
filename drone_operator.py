import socket
import threading
import cv2
import time
import numpy as np
import dotenv
import os
from dotenv import load_dotenv

load_dotenv(override=True)



class DroneOperator:
    TELLO_IP = os.getenv('TELLO_IP')
    TELLO_PORT = os.getenv('TELLO_PORT')
    TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)
    TELLO_CAMERA_ADDRESS = os.getenv('TELLO_CAMERA_ADDRESS')

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.command_text = "None"
        self.battery_text = "Battery:"
        self.time_text = "Time:"
        self.status_text = "Status:"

    def flight(self):
        # キャプチャ用のオブジェクト
        cap = None

        # データ受信用のオブジェクト備
        response = None

        # 通信用のソケットを作成 ※アドレスファミリ：AF_INET（IPv4）、ソケットタイプ：SOCK_DGRAM（UDP）
        sock = self.sock

        # 自ホストで使用するIPアドレスとポート番号を設定
        sock.bind(('', self.TELLO_PORT))

        # 問い合わせスレッド起動
        ask_thread = threading.Thread(target=self.ask)
        ask_thread.setDaemon(True)
        ask_thread.start()

        # 受信用スレッドの作成
        recv_thread = threading.Thread(target=self.udp_receiver, args=())
        recv_thread.daemon = True
        recv_thread.start()

        # コマンドモード
        sock.sendto('command'.encode('utf-8'), self.TELLO_ADDRESS)

        time.sleep(1)

        # カメラ映像のストリーミング開始
        sock.sendto('streamon'.encode('utf-8'), self.TELLO_ADDRESS)

        time.sleep(1)

        if cap is None:
            cap = cv2.VideoCapture(self.TELLO_CAMERA_ADDRESS)

        if not cap.isOpened():
            cap.open(self.TELLO_CAMERA_ADDRESS)

        time.sleep(1)


        while True:
            ret, frame = cap.read()

            # 動画フレームが空ならスキップ
            if frame is None or frame.size == 0:
                continue

            # カメラ映像のサイズを半分にする
            frame_height, frame_width = frame.shape[:2]
            frame_resized = cv2.resize(frame, (frame_width//2, frame_height//2))
            frame_output = frame_resized    
            

            # 送信したコマンドを表示
            cv2.putText(frame_output,
                    text="Cmd:" + self.command_text,
                    org=(10, 20),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(0, 255, 0),
                    thickness=1,
                    lineType=cv2.LINE_4)
            # バッテリー残量を表示
            cv2.putText(frame_output,
                    text=self.battery_text,
                    org=(10, 40),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(0, 255, 0),
                    thickness=1,
                    lineType=cv2.LINE_4)
            # 飛行時間を表示
            cv2.putText(frame_output,
                    text=self.time_text,
                    org=(10, 60),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(0, 255, 0),
                    thickness=1,
                    lineType=cv2.LINE_4)
            # ステータスを表示
            cv2.putText(frame_output,
                    text=self.status_text,
                    org=(10, 80),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(0, 255, 0),
                    thickness=1,
                    lineType=cv2.LINE_4)
            # カメラ映像を画面に表示
            cv2.imshow('Tello Camera View', frame_output)

            # キー入力を取得
            key = cv2.waitKey(1)

            # qキーで終了
            if key == ord('q'):
                break
            # wキーで前進
            elif key == ord('w'):
                self.forward(sock)
                self.command_text = "Forward"
            # sキーで後進
            elif key == ord('s'):
                self.back(sock)
                self.command_text = "Back"
            # aキーで左進
            elif key == ord('a'):
                self.left(sock)
                self.command_text = "Left"
            # dキーで右進
            elif key == ord('d'):
                self.right(sock)
                self.command_text = "Right"
            # jキーで離陸
            elif key == ord('j'):
                self.takeoff(sock)
                self.command_text = "Take off"
            # kキーで着陸
            elif key == ord('k'):
                self.land(sock)
                self.command_text = "Land"
            # hキーで上昇
            elif key == ord('h'):
                self.up(sock)
                self.command_text = "Up"
            # lキーで下降
            elif key == ord('l'):
                self.down(sock)
                self.command_text = "Down"
            # uキーで左回りに回転
            elif key == ord('u'):
                self.ccw(sock)
                self.command_text = "Ccw"
            # iキーで右回りに回転
            elif key == ord('i'):
                self.cw(sock)
                self.command_text = "Cw"
            # mキーで速度変更
            elif key == ord('m'):
                self.set_speed(sock)
                self.command_text = "Changed speed"

        cap.release()
        cv2.destroyAllWindows()

        # ビデオストリーミング停止
        sock.sendto('streamoff'.encode('utf-8'), self.TELLO_ADDRESS)
          
    # データ受け取り用の関数
    def udp_receiver(self):
            while True: 
                try:
                    data, server = self.sock.recvfrom(1518)
                    resp = data.decode(encoding="utf-8").strip()
                    # レスポンスが数字だけならバッテリー残量
                    if resp.isdecimal():
                        self.battery_text = "Battery:" + resp + "%"
                    # 最後の文字がsなら飛行時間
                    elif resp[-1:] == "s":
                        self.time_text = "Time:" + resp
                    else: 
                        self.status_text = "Status:" + resp
                except:
                    pass

    # 問い合わせ
    def ask(self, sock):
        while True:
            try:
                sent = sock.sendto('battery?'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass
            time.sleep(0.5)

            try:
                sent = sock.sendto('time?'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass
            time.sleep(0.5)

    # 離陸
    def takeoff(self, sock):
            try:
                sent = sock.sendto('takeoff'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 着陸
    def land(self, sock):
            try:
                sent = sock.sendto('land'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 上昇(20cm)
    def up(self, sock, value=20):
            try:
                sent = sock.sendto(f'up {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 下降(20cm)
    def down(self, sock, value=20):
            try:
                sent = sock.sendto(f'down {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 前進(40cm)
    def forward(self, sock, value=40):
            try:
                sent = sock.sendto(f'forward {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 後進(40cm)
    def back(self, sock, value=40):
            try:
                sent = sock.sendto(f'back {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 右に進む(40cm)
    def right(self, sock, value=40):
            try:
                sent = sock.sendto(f'right {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 左に進む(40cm)
    def left(self, sock, value=40):
            try:
                sent = sock.sendto(f'left {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 右回りに回転(90 deg)
    def cw(self, sock, value=90):
            try:
                sent = sock.sendto(f'cw {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 左回りに回転(90 deg)
    def ccw(self, sock, value=90):
            try:
                sent = sock.sendto(f'ccw {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass

    # 速度変更(例：速度40cm/sec, 0 < speed < 100)
    def set_speed(self, sock, value=40):
            try:
                sent = sock.sendto(f'speed {value}'.encode(encoding="utf-8"), self.TELLO_ADDRESS)
            except:
                pass


def main():
     drone_operator = DroneOperator()
     drone_operator.flight()



if __name__ == '__main__':
     main()
import socket
import threading
import cv2
import time
import numpy as np
from drone_operator import DroneOperator


class DroneQRReader(DroneOperator):
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

        cnt_frame = 0

        # qrコード読み取り用のインスタンス
        qcd = cv2.QRCodeDetector()

        while True:
            ret, frame = cap.read()
            cnt_frame += 1

            # 動画フレームが空ならスキップ
            if frame is None or frame.size == 0:
                continue

            # カメラ映像のサイズを半分にする
            frame_height, frame_width = frame.shape[:2]
            frame_resized = cv2.resize(frame, (frame_width//2, frame_height//2))
            frame_output = frame_resized

            # qrコードの読み取り
            if cnt_frame % 5 == 0:
                retval, decoded_info, points, straight_qrcode = qcd.detectAndDecodeMulti(frame_resized) 
                if retval:
                    frame_qrdet = cv2.polylines(frame_resized, points.astype(int), True, (0, 255, 0), 3)
                    frame_ouput = frame_qrdet
            
                if len(decoded_info) != 0:
                    print(f"読み取り結果(result)：{decoded_info}")
            

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


def main():
    drone_qr_reader = DroneQRReader()
    drone_qr_reader.flight()

if __name__ == '__main__':
    main()
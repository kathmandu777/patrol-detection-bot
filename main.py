
import requests
import RPi.GPIO as GPIO  # GPIO用のモジュールをインポート
import time
import os
import sys

class LINENotifyBot:
    API_URL = 'https://notify-api.line.me/api/notify'

    def __init__(self, access_token):
        self.__headers = {'Authorization': 'Bearer ' + access_token}

    def send(self, message):
        data = {'message': message}
        r = requests.post(
            LINENotifyBot.API_URL,
            headers=self.__headers,
            data=data
        )


class PatrolDetectionBot:
    # ポート番号の定義
    Trig = 27
    Echo = 18
    DISTANCE_TO_DOOR = 300 # cm

    def __init__(self) -> None:
        # GPIOの設定
        GPIO.setmode(GPIO.BCM)  # GPIOのモードを"GPIO.BCM"に設定
        GPIO.setup(self.Trig, GPIO.OUT)  # GPIO27を出力モードに設定
        GPIO.setup(self.Echo, GPIO.IN)  # GPIO18を入力モードに設定

    # HC-SR04で距離を測定する関数
    def read_distance(self):
        GPIO.output(self.Trig, GPIO.HIGH)  # GPIO27の出力をHigh(3.3V)にする
        time.sleep(0.00001)  # 10μ秒間待つ
        GPIO.output(self.Trig, GPIO.LOW)  # GPIO27の出力をLow(0V)にする

        while GPIO.input(self.Echo) == GPIO.LOW:  # GPIO18がLowの時間
            sig_off = time.time()
        while GPIO.input(self.Echo) == GPIO.HIGH:  # GPIO18がHighの時間
            sig_on = time.time()

        duration = sig_on - sig_off  # GPIO18がHighしている時間を算術
        distance = duration * 34000 / 2  # 距離を求める(cm)
        return distance

    def check(self) -> bool:
        cm = self.read_distance()  # HC-SR04で距離を測定する
        print("distance=", int(cm), "cm")  # 距離をint型で表示
        if cm >= self.DISTANCE_TO_DOOR:
            return True
        return False  # TODO: change logic


def main():
    line_bot = LINENotifyBot(os.environ["LINE_NOTIFY_TOKEN"])
    patrol_bot = PatrolDetectionBot()
    while True:
        try:
            if patrol_bot.check():
                line_bot.send(message="巡回が来ました(立志玄関)")
                GPIO.cleanup()  # GPIOをクリーンアップ
                print("detected patrol")
                break
            time.sleep(0.1)
        except KeyboardInterrupt:
            GPIO.cleanup()  # GPIOをクリーンアップ
            print("keyboard interrupt")
            sys.exit()
        except Exception as e:
            print(e)
            GPIO.cleanup()  # GPIOをクリーンアップ
            print("exit")
            sys.exit()
            

if __name__ == '__main__':
    main()

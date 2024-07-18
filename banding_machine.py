import RPi.GPIO as gpio
import time
import vlc
import serial

import signal
import sys
	
# 아두이노에서 값 받아오기
port="/dev/ttyACM0"
serialFromArduino = serial.Serial(port,2400)
serialFromArduino.flushInput()

# 초음파 센서 설정

TRIGER = 24
ECHO = 23

gpio.setmode(gpio.BCM)
gpio.setup(TRIGER,gpio.OUT)
gpio.setup(ECHO,gpio.IN)

startTime = time.time()


# 변수 선언
# isUsing = False
mp3_location = "/home/hamtory/Desktop/banding_machine_mp3/"
mp3_saying = [
	{
		"path" : "hello",
	},
	{
		"path" : "bye",
	},
	{
		"path" : "money_before_pay",
	},
	{
		"path" : "money_after_pay",
	},
	{
		"path" : "money_after_pay",
	},
	{
		"path" : "insufficient_money",
	},
	{
		"path" : "error",
	},
	{
		"path" : "won",
	},
	{
		"path" : "pay",
	},
	{
		"path" : "you_chose",
	},
	{
		"path" : "put_card",
	},
]

# TTS 출력 함수
def speaking(filename):
	mp3 = vlc.MediaPlayer(mp3_location + filename+".mp3")
	mp3.play()
	time.sleep(0.1)
	
	while mp3.is_playing():
		continue
		
	mp3.release()	


#---------------------------------------

def read_money(pay_money) : 
	pay_money_len = len(pay_money)

	for i in pay_money:
		if i != '0':
			speaking(i)
		
			if pay_money_len == 5:
				speaking("10000")
				
			if pay_money_len == 4:
				speaking("1000")
				
			if pay_money_len == 3:
				speaking("100")
				
			if pay_money_len == 2:
				speaking("10")
			
		pay_money_len = pay_money_len - 1

# --------------------------

def use_banding_machine():
	mp3 = vlc.MediaPlayer("/home/hamtory/Desktop/banding_machine_mp3/" + "hello" + ".mp3")
	mp3.play()
	time.sleep(6)
	mp3.release()

	while True:	
		arduino_input = serialFromArduino.readline().decode('utf-8')

		if arduino_input[:13] == "selected item":
			# isUsing = True
			speaking(arduino_input[16:].split(",")[0])
			
			speaking(mp3_saying[9]["path"])
		
		elif arduino_input[:5] == "price":
			read_money(str(int(arduino_input[8:].split(",")[0])))
			speaking(mp3_saying[7]["path"])
			
			speaking(mp3_saying[10]["path"])
		
		# 충전 또는 결제 및 금액, 잔액 출력
		# 이전 잔액
		elif arduino_input[:11] == "old balance":
			speaking(mp3_saying[2]["path"])
			
			read_money(str(int(arduino_input[14:].split(",")[0])))
			speaking(mp3_saying[7]["path"])
		
		# 금액
		elif arduino_input[:12] == "change_value":
			read_money(str(int(arduino_input[14:].split(",")[0]))[1:])
			speaking(mp3_saying[8]["path"])
		
		# 결제 후 잔액
		elif arduino_input[:11] == "new balance":
			speaking(mp3_saying[3]["path"])
			
			read_money(str(int(arduino_input[14:].split(",")[0])))
			speaking(mp3_saying[7]["path"])
			
		# rfid 통신 성공
		elif arduino_input[:22] == "MIFARE_Write() success":
			# isUsing = False
			
			return 0
		
		# 잔액 부족시
		elif arduino_input[:20] == "Insufficient balance":
			speaking(mp3_saying[5]["path"])
			
			# isUsing = False
			
			return 0
			
		# 에러 출력
		elif "failed" in arduino_input:
			speaking(mp3_saying[6]["path"])
		
			# isUsing = False
			
			return 0
			

		print(arduino_input)
		# print(GPIO.input(PIR_PIN))	

sw = 0

while True:
	if sw==0:
		gpio.output(TRIGER,gpio.LOW)
		time.sleep(0.1)
		gpio.output(TRIGER,gpio.HIGH)
		time.sleep(0.00001)
		gpio.output(TRIGER,gpio.LOW)
		
		while gpio.input(ECHO) == gpio.LOW:
			startTime = time.time()
		
		while gpio.input(ECHO) == gpio.HIGH:
			endTime = time.time()

		period = endTime - startTime
		dist = period * 1000000 / 58
		
		if dist < 50:
			sw = 1

		if sw == 1:
	
			use_banding_machine()

			sw = 0
		print("input sensor")


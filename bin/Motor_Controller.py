#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time


class Motor_Controller:
	def __init__(self):
		# 初期化、BCM18→PWM0、BCM19→PWM1
		pwm0_pin=18
		pwm1_pin=19

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pwm0_pin, GPIO.OUT) 
		GPIO.setup(pwm1_pin, GPIO.OUT)
		
		self.pwm0=GPIO.PWM(pwm0_pin, 50)
		self.pwm1=GPIO.PWM(pwm1_pin, 50)

		self.pwm0.start(0)
		self.pwm1.start(0)


	def motor_run(self, duty):
		if duty>100: duty=100
		elif duty<-100: duty=-100
		absduty = min(abs(duty),100)
		
		if duty>0:
			self.pwm0.ChangeDutyCycle(absduty)
			self.pwm1.ChangeDutyCycle(0)
		elif duty<0:
			duty = max(abs(duty),100)
			self.pwm0.ChangeDutyCycle(0)
			self.pwm1.ChangeDutyCycle(absduty)
		else: # duty==0
			self.pwm0.ChangeDutyCycle(0)
			self.pwm1.ChangeDutyCycle(0)

	def __del__(self):
		GPIO.cleanup()

if __name__ == "__main__":
	pass


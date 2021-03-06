from flask import Flask
from flask_ask import Ask, statement, convert_errors, convert
import RPi.GPIO as GPIO
import logging
#from __future__ import print_function
#import threading
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)

app = Flask(__name__)
ask = Ask(app, '/')

'''
class timer_thread(threading.thread):
	def run(self, timedelta=0):
		time.sleep(time)
		GPIO.output(4,True)
		time.sleep(30)
		GPIO.output(4,False)


so now we do:
  Timer = timer_thread(name="timer {}".format(timer_number))
  Timer.start(desired_time)
  return statement("timer started")

bc setting a timer does work but the skill times out
we can use this for both timer and a desired time we just 
need to calculate the time difference which should be trivial

we should also set a limit on the number of timers bc each timer
is a thread so if people set a lot of timers we will get a 
lot of threads on the pi and slow down or even crash 
'''

#logging.getLogger("flask_ask").setLevel(logging.DEBUG)

'''
@ask.intent('GPIOControlIntent', mapping={'status': 'status', 'pin': 'pin'})
def gpio_control(status, pin):

    try:
        pinNum = int(pin)
    except Exception as e:
        return statement('Pin number not valid.')

    GPIO.setup(pinNum, GPIO.OUT)

    if status in ['on', 'high']:    GPIO.output(pinNum, GPIO.HIGH)
    if status in ['off', 'low']:    GPIO.output(pinNum, GPIO.LOW)

    return statement('Turning pin {} {}'.format(pin, status))
'''
@ask.intent('SetTimeIntent', mapping={'settime':'time'})
def set_time(time):
	pass


@ask.intent('SetTimerIntent', mapping={'quantity':'quantity', 'units':'units'})
def set_timer(quantity, units):
	if units == "seconds" or units=="second":
		time.sleep(quantity)
		GPIO.output(4, True)
		time.sleep(int(quantity))
		GPIO.output(4,False)

        elif units == "minute" or units=="minutes":
		secConv = int(quantity) * 60
		#if starting instead of duration:
		time.sleep(secConv)
                GPIO.output(4, True)
                time.sleep(secConv)
                GPIO.output(4,False)
 	elif units == "hours" or units=="hour":
                secConv = int(quantity) * 3600
                #if starting instead of duration:
                #time.sleep(secConv))
                GPIO.output(4, True)
                time.sleep(secConv)
                GPIO.output(4,False)
	else:
		return statement("Please try again")

	#return statement("Your coffee has begun brewing")
	return statement("brewing coffee for {} {}".format(quantity, units))


@ask.intent('OnIntent')
def turn_on():
	GPIO.output(4,True)

	return statement('Coffee pot is on')

@ask.intent('OffIntent')
def turn_off():
	GPIO.output(4,False)

	return statement('Coffee pot is off')

from __future__ import print_function
import threading
from flask import Flask
from flask_ask import Ask, request, statement, convert_errors, convert
import RPi.GPIO as GPIO
import logging
import time as tm
from datetime import datetime
import ssl

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)
NUM_OF_TIMERS = 0

app = Flask(__name__)
ask = Ask(app, '/')



#class timer_thread(threading.Thread):
def run(timedelta=0):
	global NUM_OF_TIMERS
	if NUM_OF_TIMERS < 5:
		NUM_OF_TIMERS = NUM_OF_TIMERS + 1
		print ("timer started for {}".format(timedelta))
		tm.sleep(timedelta)
		print ("coffee on")
		GPIO.output(4,True)
		tm.sleep(6 * 60)
		NUM_OF_TIMERS = NUM_OF_TIMERS - 1
		print ("coffee off")
		GPIO.output(4,False)

def parse_duration(duration):
	quantity = 0
	duration = duration[1:]
	T_value = duration.find("T")
	if duration[0] != 'T':
	# <1 day in advance
		year = duration.find("Y")
		if year > -1:
			quantity = quantity + int(duration[:year])*365*24*3600
			duration = duration[year + 1:]
		mnth = duration.find("M")
		if mnth > -1 and mnth < T_value:
			quantity = quantity + int(duration[:mnth])*30*24*3600
			duration = duration[mnth + 1:]
		day  = duration.find("D")
		if day > -1:
			quantity = quantity + int(duration[:day])*24*3600
			duration = duration[day + 1:]
	# >1 day in advance
	if T_value > -1:
		duration = duration[T_value+1:]
		hour = duration.find("H")
		if hour > -1:
			quantity = quantity + int(duration[:hour])*3600
			duration = duration[hour + 1:]
		mnt = duration.find("M")
		if mnt > -1:
			quantity = quantity + int(duration[:mnt])*60
			duration = duration[mnt+1:]
		sec = duration.find("S")
		if sec > -1:
			quantity = quantity + int(duration[:sec])
		
	return quantity
'''
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


@ask.intent('SetTimeIntent', mapping={'settime':'on_time','setdate':'on_date'})
def set_time(on_time,on_date):
	#---NEEDS TESTING -----------------------------------
	time_now = datetime.now()
	on_time = request.intent.slots.settime.value
	if len(on_time) == 2:
	    on_time = on_time + ":00"
	try: 
	    on_date = request.intent.slots.setdate.value
	    net_time = on_time + " " + on_date
	    print(net_time)
	    on_time_f = tm.strptime(net_time, "%H:%M %Y-%m-%d")
	    on_time_f = datetime.fromtimestamp(tm.mktime(on_time_f))
	except:
	    on_date = "";
	    print(on_time)
	    on_time_f = tm.strptime(on_time, "%H:%M")
	    on_time_f = datetime.fromtimestamp(tm.mktime(on_time_f))
	
	quantity = (time_now - on_time_f).total_seconds()
	quantity = int(quantity)
	TIMER = threading.Thread(target=run,args=(quantity,))
	TIMER.start()
	if on_date == "":
	    return statement("coffee will brew at {}".format(request.intent.slots.settime.value))
	else:
	    return statement("coffee will brew at {0} on {1}".format(request.intent.slots.settime.value,request.intent.slots.setdate.value))
	
	# ---------------------------------------------------

@ask.intent('SetTimerIntent', mapping={'duration':'duration'})
def set_timer(duration):
	duration = request.intent.slots.duration.value
	if duration[0] == 'P':
		quantity = parse_duration(duration)
		if quantity == 0:
			return statement("please try again")
		TIMER = threading.Thread(target=run,args=(quantity,))
		TIMER.start()
		return statement("coffee will brew in {}".format(duration))

	else:
		return statement("please try again")
		

@ask.intent('OnIntent')
def turn_on():
	GPIO.output(4,True)

	return statement('Coffee pot is on')

@ask.intent('OffIntent')
def turn_off():
	GPIO.output(4,False)

	return statement('Coffee pot is off')

if __name__ == '__main__':
    #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #context.load_cert_chain('certificate.pem', 'private-key.pem')
    #
    #app.run(host='155.47.187.6',port=443, ssl_context=context)
    app.run()

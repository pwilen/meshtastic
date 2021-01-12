#!/usr/bin/env python3

# Import required Python libraries
import paho.mqtt.client as paho
import time
import urllib.parse
import RPi.GPIO as GPIO
import datetime
import subprocess
import meshtastic

# Mqtt
mqttc = paho.Client()
url_str = 'mqtt://192.168.68.114:1883'
url = urllib.parse.urlparse(url_str)
mqttc.username_pw_set("mqtthass", "mqttpass")

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_PIR = 17

print("PIR Module Test (CTRL-C to exit)")

# Set pin as input
GPIO.setup(GPIO_PIR,GPIO.IN)      # Echo

Current_State  = 0
Previous_State = 0

#Setup meshtastic TCPInterface
interface = meshtastic.TCPInterface("meshtastic.local")


#Setup MQTT
def printtime(): # Used for debug
	# Current time
	global hour, minute, wholetime
	now = datetime.datetime.now()
	hour = str(now.hour)
	minute = int(now.minute)
	minute = '%02d' % minute
	wholetime = hour + ":" + minute

#Definitions
def sendmqtt(mess):
    try:
        mqttc.connect(url.hostname, url.port)
        mqttc.publish("movement/touch", mess)
        sleep(5)
    except:
        pass

def sendtomesh(mess):
    try:
        interface.sendText(mess)
        sleep(5)
    except:
        pass

#Notify that we are ready to go
sendmqtt("Pirmqtt started")
sendtomesh("Pirmqtt started")
#Loop
try:

  print("Waiting for PIR to settle ...")

  # Loop until PIR output is 0
  while GPIO.input(GPIO_PIR)==1:
    Current_State  = 0

  print("Ready")

  # Loop until users quits with CTRL-C
  while True :

    # Read PIR state
    Current_State = GPIO.input(GPIO_PIR)

    if Current_State==1 and Previous_State==0:
      # PIR is triggered
      print("Motion detected!")
      #sendmqtt("Motion detected")
      sendtomesh("Motion detected")
      #subprocess.call('/home/pi/wakeup.sh', shell=True)
      # Record previous state
      Previous_State=1
    elif Current_State==0 and Previous_State==1:
      # PIR has returned to ready state
      print("Ready")
      Previous_State=0

    # Wait for 5 seconds
    time.sleep(5)
    print("Sleep 5 seconds")
    #subprocess.call('/home/pi/sleep.sh', shell=True)
except KeyboardInterrupt:
  print("Quit")
  # Reset GPIO settings
  GPIO.cleanup()

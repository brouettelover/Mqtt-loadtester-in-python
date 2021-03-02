import paho.mqtt.client as mqtt
import random
import datetime
import threading
import time
import configparser

cp_mqtt = configparser.ConfigParser()
cp_mqtt.read("mqtt_config.ini")
username = cp_mqtt["account"]['username']
password = cp_mqtt["account"]['password']
qos = cp_mqtt["sub"]['qos']
topic = cp_mqtt["sub"]['topic']

x = 0
def on_connect(client, obj, flags, rc):
    countdown_thread = threading.Thread(target=countdown)
    countdown_thread.start()
    client.subscribe(topic, int(qos))
 
def on_message(client, obj, msg):
    global x
    x = x + 1

def countdown():
    my_timer = 5
    end = my_timer
    while my_timer <= end and my_timer > 0 :
        my_timer = my_timer - 1
        time.sleep(1)
    if my_timer == 0:
        my_timer = 5
        now = datetime.datetime.now()
        print(str(now.strftime("%Y-%m-%d %H:%M:%S")) +"|"+ "The current number of message that has been receive is :" + str(x)) 
        countdown()
 
print("Initializing subscriber")
nbr = random.randint(0, 10000000)
client_id=username+"_sub_id:"+str(nbr)

client = mqtt.Client(client_id, True, userdata=None, transport="tcp")

client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(cp_mqtt["server"]['host'], int(cp_mqtt['server']['port']), 3600)
print("Listening")
client.loop_forever()
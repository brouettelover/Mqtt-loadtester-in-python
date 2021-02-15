#execute while being in the directory

#Import the libraries
import paho.mqtt.client as mqtt
import sys
import os
import random
import configparser
from optparse import OptionParser
from optparse import OptionGroup

# The username and password are store in the mqtt_conf.ini
cp_mqtt = configparser.ConfigParser()

cp_mqtt.read("mqtt_config.ini")
username = cp_mqtt["account"]['username']
password = cp_mqtt["account"]['password']

#The following codes is for creating a beautiful CLI menu easily
parser = OptionParser()
# Add an option group with the tittle
group = OptionGroup(parser, "Mandatory Options")
# Add an option to the menu
group.add_option("-q", "--qos",
                  action="store", type="int", dest="qos",
                  help="MQTT qos value from 0 to 2")
group.add_option("-c", "--clean_session",
                  action="store", dest="clean_session", default=True,
                  help="True or false")
group.add_option("-t", "--topic",
                  action="store", type="string", dest="topic",
                  help="topic where to subscribe")
parser.add_option_group(group)

group = OptionGroup(parser, "Optionnal Options")
group.add_option("-u", "--username",
                  action="store", type="string", dest="username", default=username,
                  help="MQTT username")
group.add_option("-p", "--password",
                  action="store", type="string", dest="password", default=password,
                  help="MQTT password")
parser.add_option_group(group)

(options, args) = parser.parse_args()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Display the result code of the connection
    print("Connected with result code "+str(rc))

global x
x = 0
# Display the message when it arrive
def on_message(client, userdata, msg):
    # X is my number of message that has been arrived
    global x
    x = x + 1
    #command system change !!!!! change it for linux with "clear" !!!!! maybe there is a beautiful way to do it
    os.system('cls')
    print("The number of message that has been send : " + str(x))
    

# All the ways to subscribe to a server
def sub(qos, username, password, clean_session, topic) :
    #Create a random id with the username + a random int
    nbr = random.randint(0, 10000000)
    client_id=username+"_sub_id:"+str(nbr)
    #Settings for the client
    client = mqtt.Client(client_id, clean_session, userdata=None, transport="tcp")
    client.username_pw_set(username, password)
    #Connect to the broker with port and ttl
    client.connect(cp_mqtt["config"]['server'], cp_mqtt["config"]['port'], 60)
    client.on_connect=on_connect
    #The subject to subscribe with the specific qos
    client.subscribe(topic, qos)
    client.on_message=on_message
    #Maintain the connection forever
    client.loop_forever()

#To specify that those options are mandatory
if(options.qos == None or options.clean_session == None or options.topic == None):
    print("Pls provide all the mandatory options (for help -h)")
else:
    #If you use a different user you need to specify both password and user
    if(options.username == username and options.password != password):
        print("Pls provide a password")
    elif(options.username != username and options.password == password):
        print("Pls provide a username")
    else:
        sub(options.qos, options.username, options.password, options.clean_session, options.topic)
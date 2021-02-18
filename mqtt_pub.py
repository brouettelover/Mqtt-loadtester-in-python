import paho.mqtt.client as mqtt
import random
import os
import time
import threading
from optparse import OptionParser
from optparse import OptionGroup
import configparser

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
group.add_option("-t", "--topic",
                  action="store", type="string", dest="topic",
                  help="topic where to publish")
group.add_option("-n", "--number",
                  action="store", type="long", dest="number_message",
                  help="Number of message to be publish on the topic")
group.add_option("-m", "--message_length",
                  action="store", type="int", dest="message_length",
                  help="Length of the message provide (in oct)")
group.add_option("-c", "--clean_session",
                  action="store", dest="clean_session", default=True,
                  help="True or false")
parser.add_option_group(group)
group = OptionGroup(parser, "Optionnal Options")
group.add_option("-u", "--username",
                  action="store", type="string", dest="username", default=username,
                  help="MQTT username")
group.add_option("-p", "--password",
                  action="store", type="string", dest="password", default=password,
                  help="MQTT password")
group.add_option("-M","--message_length_2",
                   action="store", type="int", dest="message_length_2", default=0,
                   help="if provide need a sleep time and set the length of the message after the sleep time")
group.add_option("-a", action="store", type="int", dest="active_time", default=0,
                  help="active time before sleep")
group.add_option("-s", action="store", type="int", dest="sleeping_time", default=0,
                  help="sleeping time")
group.add_option("-T", action="store", type="int", dest="n_topic", default=1,
                  help="Number of desired topic")
group.add_option("-N", action="store", type="int", dest="n_run", default=0,
                  help="number of runs")
parser.add_option_group(group)
(options, args) = parser.parse_args()
# Create a countdown with the active_time
def countdown():
    global my_timer
    global stop_threads
    my_timer = options.active_time
    for x in range(options.active_time):
        if(stop_threads):
            break
        my_timer = my_timer - 1
        time.sleep(1)
stop_threads = False
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
     # Display the result code of the connection
    print("Connected with result code "+str(rc)) 
def pub_now(client, number_message, n_topic, topic, message_length, qos):
    x = 1
    #create a msg with a specific number of length
    msg = length_conv(message_length)
    # publish the number_message
    while(x <= number_message):
            # publish in all the topics
            for i in range(n_topic):
                #Publish the message
                client.publish(topic + str(i + 1), msg + str(x),qos)
                print(x)
            x = x + 1
    client.disconnect()
# Publish with the sleeping time and active time
def pub_active(client, number_message, n_topic, topic, message_length, message_length_2, qos, n_run, sleeping_time):
    print("Starting publishing for " + str(options.active_time) + "sec")
    #The number of the run that is active now
    run_active = 1
    #The number of the message that has been send
    message_send = 1
    flag_message_length = 0
    # height of the sequence that will be published
    runs_height = number_message / n_run
    # While the n_run is not achieved do
    while(run_active <= n_run):
        #Start my countdown thread with the active time
        global stop_threads
        stop_threads = False
        countdown_thread = threading.Thread(target=countdown)
        countdown_thread.start()
        #Check the flag and attribute the right msg length and swith the flag to the other message length 
        if(flag_message_length == 0):
            msg = length_conv(message_length)
            flag_message_length = 1
        else:
            msg = length_conv(message_length_2)
            flag_message_length = 0
        #While the thread is active do
        while(countdown_thread.is_alive()):
            #While the number of message has not reach the height of the run and my countdow is on do
            while(message_send <= runs_height and my_timer > 0):
                #Publish in the number of topics specified with the correct message length and a specific Qos
                for i in range(n_topic):
                    client.publish(topic + str(i + 1), msg + str(message_send) ,qos) #add + str(message_send) after msg to see the number of messages in the sub
                message_send  = message_send  + 1
                #If all the message were send, stop the countdown and print the current_value
                if(message_send == runs_height):
                    print("All messages was send in : " + str(options.active_time - my_timer) + "sec")
                    stop_threads = True
        #Check if the number of the message in the active time has all been realeased
        if(message_send < runs_height):
            print("Only published : " + str(message_send  - 1) + " Messages on " + str(n_topic) + " Topic(s)")
        else:
            print("Message sends : " + str(message_send  - 1) + " Messages on " + str(n_topic) + " Topic(s)")
        #If there is a sleeping time wait for a certain amount of time
        if(sleeping_time != 0):
            print("Waiting : " + str(sleeping_time) + " sec")
            time.sleep(sleeping_time)
        #Advance one step ahead in the runs
        run_active = run_active + 1
        # reset the number of message sent
        message_send  = 0
    print("End of pub")
    stop_threads = True
    client.disconnect()
#Used for no run set    
def pub_run_0(client, number_message, n_topic, topic, message_length, message_length_2, qos, n_run, sleeping_time):
    print("Starting publishing for " + str(options.active_time) + "sec")
    #The number of the message that has been send
    message_send = 1
    flag_message_length = 0
    # height of the sequence that will be published
    runs_height = number_message
    # While all the message has not being send
    while(message_send <= runs_height):
        #Start my countdown thread with the active time
        global stop_threads
        stop_threads = False
        countdown_thread = threading.Thread(target=countdown)
        countdown_thread.start()
        #Check the flag and attribute the right msg length and swith the flag to the other message length 
        if(flag_message_length == 0):
            msg = length_conv(message_length)
            flag_message_length = 1
        else:
            msg = length_conv(message_length_2)
            flag_message_length = 0
        #While the thread is active do
        while(countdown_thread.is_alive()):
            #While the number of message has not reach the height of the run and my countdow is on do
            while(message_send <= runs_height and my_timer > 0):
                #Publish in the number of topics specified with the correct message length and a specific Qos
                for i in range(n_topic):
                    client.publish(topic + str(i + 1), msg + str(message_send) ,qos) #add + str(message_send) after msg to see the number of messages in the sub
                message_send  = message_send  + 1
                #If all the message were send, stop the countdown and print the current_value
                if(message_send == runs_height):
                    print("All messages was send in  the last run in : " + str(options.active_time - my_timer) + "sec")
                    stop_threads = True
                    
        #Check if the number of the message in the active time has all been realeased
        if(message_send < runs_height):
            print("Only published : " + str(message_send  - 1) + " Messages on " + str(n_topic) + " Topic(s)" )
        else:
            print("All sends : " + str(message_send  - 1) + " Messages on " + str(n_topic) + " Topic(s)")
            break
        #If there is a sleeping time wait for a certain amount of time
        if(sleeping_time != 0):
            print("Waiting : " + str(sleeping_time) + " sec")
            time.sleep(sleeping_time)
    print("End of pub")
    stop_threads = True
    client.disconnect()

# Create a random string with a specific byte length
def length_conv(message_length):
    rand_string = str(os.urandom(message_length))
    return rand_string
# Send to the correct publisher 
def publisher(client, topic, qos, number_message, message_length, message_length_2, active_time, sleeping_time, n_topic, n_run):   
    # If there is no message length 2 set
    if(message_length_2 == 0):
        message_length_2 = message_length
    # If there is no active time set
    if(active_time == 0):
        pub_now(client, number_message, n_topic, topic, message_length, qos)
        if(sleeping_time != 0):
            time.sleep(sleeping_time)
            pub_now(client, number_message, n_topic, topic, message_length, qos)
    else:
        if(n_run == 0):
            pub_run_0(client, number_message, n_topic, topic, message_length, message_length_2, qos, n_run, sleeping_time)
        else:
            pub_active(client, number_message, n_topic, topic, message_length, message_length_2, qos, n_run, sleeping_time)
# Pub settings for the client
def pub(qos, topic, username, password, clean_session, number_message, message_length, message_length_2, active_time, sleeping_time, n_topic, n_run) :
    #Create a random id with the username
    nbr = random.randint(0, 10000000)
    client_id=username+"_pub_id:"+str(nbr)
    #Settings for the client
    client = mqtt.Client(client_id, clean_session, userdata=None, transport="tcp")
    client.username_pw_set(username, password)
    #Connect to the broker
    client.connect(cp_mqtt["config"]['server'], cp_mqtt["config"]['port'], 60)
    client.on_connect=on_connect
    publisher(client, topic, qos, number_message, message_length, message_length_2, active_time, sleeping_time, n_topic, n_run)


#To specify that those options are mandatory
if(options.qos == None or options.clean_session == None or options.topic == None or options.number_message == None or options.message_length == None):
    print("Pls provide all the mandatory options (for help -h)")
else:
    #If you use a different user you need to specify both password and user
    if(options.username == username and options.password != password):
        print("Pls provide a password")
    elif(options.username != username and options.password == password):
        print("Pls provide a username")
    else:
        pub(options.qos, options.topic, options.username, options.password, options.clean_session, options.number_message, options.message_length, options.message_length_2, options.active_time, options.sleeping_time, options.n_topic, options.n_run)
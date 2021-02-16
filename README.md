# Mqtt loadtester in python 
 A simple mqtt loadtester made in python

## Prerequise<br/>
You need to have pip to install the dependencies and obviously python 3

## Install the dependencies<br/>
```
pip install paho-mqtt
pip install configparser
pip install random
pip install optparse
```

#### Change the config.ini
change the files with your paremeters
```
[account]
username = user
password = pass
[config]
server = ip
port = port
```

#### Install <br/>
```
git clone https://github.com/brouettelover/Mqtt-loadtester-in-python/
cd Mqtt-loadtester-in-python 
```

#### To launch the pub or sub just do <br/>
```
python mqtt_sub.py
python mqtt_pub.py
```

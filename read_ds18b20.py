#!/usr/bin/python3

# bulk-read all attached 1-Wire temp sensors
# see https://docs.kernel.org/w1/slaves/w1_therm.html

import time
import json

#import daemon

# MQTT isn't strictly necessary as you can grab whatever you want at the get_temp() call
import paho.mqtt.client as mqtt

# discovery info, see https://www.home-assistant.io/integrations/sensor.mqtt
discovery_payload = {'unique_id': 'douglas-w1-000005f0a55c', 'expire_after': 30, 
                     'name': 'w1-000005f0a55c', 'state_topic': 'stat/douglas/1-wire/000005f0a55c',
                     'device_class': 'temperature', 'unit_of_measurement': '°C',
                     'availability_topic': 'stat/douglas/1-wire/status',
                     'payload_available': 'Online', 'payload_not_available': 'Offline',
                     'device': { 'name': 'Douglas 1-Wire', 'identifiers': ['douglas-w1']}
                     }


def on_connect(client, userdata, flags, rc):
	#print("Connected with result code "+str(rc))
	client.publish("stat/douglas/1-wire/status",payload="Online", qos=0, retain=True)
	client.publish('homeassistant/sensor/000005f0a55c/config', json.dumps(discovery_payload), qos=0, retain=True)

#mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.will_set("stat/douglas/1-wire/status", payload="Offline", qos=0, retain=True)
mqttc.connect('192.168.1.4')
mqttc.loop_start()


bus_base = '/sys/devices/w1_bus_master1/'

def get_temp(addr):
    with open(f'{bus_base}/{addr}/temperature', 'r') as t:
        addr = addr[3:]
        temp = int(t.read().strip())/1000
        #print (addr, temp)
        mqttc.publish(f'stat/douglas/1-wire/{addr}', temp) 
        return(temp)



def bulk_read():
    payload = {}
    with open (bus_base + 'therm_bulk_read', 'r') as bulk:
        trig = bulk.read().strip()
        if trig == '1':  # all temps ready to read
            payload['timestamp'] = time.time()
            payload['sensors'] = []
            with open(bus_base + 'w1_master_slaves', 'r') as s:
                slaves = s.read().splitlines()
                for line in slaves:
                    if line.startswith('28-'): # temperature sensor
                        sensor_id = line[3:]
                        d = {'address': sensor_id, 'temperature': get_temp(line)}
                        payload['sensors'].append(d)
    mqttc.publish('stat/douglas/1-wire/json', json.dumps(payload))


#with daemon.DaemonContext():
while True:
    with open (bus_base + 'therm_bulk_read', 'w') as bulk:
        bulk.write('trigger\n')
    bulk_read()
    mqttc.loop()
    time.sleep(15)


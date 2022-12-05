import serial
from time import sleep
import numpy as np
import struct
import paho.mqtt.client as mqtt


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("AGV/Motores")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.payload==b"Stop":
        client.publish(topic="Camara/Deteccion",payload="Stop", qos=1)
        client.publish(topic="Fin",payload="Motores Terminaron", qos=1)
        client.disconnect()
    else:
        entero=int(msg.payload)
        print(entero)
        ser = serial.Serial('/dev/ttyS0',115200,timeout=1)
        ser.write(entero.to_bytes(1, 'little'))

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.137.1", 1883, 60)


    client.loop_forever()
    
main()
    

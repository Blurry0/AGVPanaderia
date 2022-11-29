#! /usr/bin/python3
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

with open('num_tienda.txt','r') as reader:
    num_tienda=reader.read()
print(int(num_tienda))

with open('num_tienda.txt','w') as writer:
    if int(num_tienda) < 3:
        writer.write(str(int(num_tienda)+1))
    else:
        writer.write('1')
    
continue_reading = True

# This is the default key for authentication
key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

# Data read        
backdata = []

# Create an object of the class MFRC522
MIFAREReader = MFRC522()

#block_num = 8

block_num=4

print("Acerque el tag al lector")

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    json=[]
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("¡Tag detectado!")
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        
        # Print UID
        print("UID del tag: %s %s %s %s" % ('{0:x}'.format(uid[0]), '{0:x}'.format(uid[1]), '{0:x}'.format(uid[2]), '{0:x}'.format(uid[3])))
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)
        
        for block_num in range (4,19):
            if block_num in [7,11,15]:
                continue
            
            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, block_num, key, uid)

            # Check if authenticated
            if status == MIFAREReader.MI_OK:
                print(block_num)

                # Read block_num
                backdata = MIFAREReader.MFRC522_Read(block_num)
                
                if backdata != None:
                    print("dato")
                    
                    backdata = "".join([chr(i) for i in backdata if i!=ord(' ')])
                    json.append(backdata)
                   
                else:
                    print("dato_vacio")
                    print("¡No se pudo leer el bloque!")
                
                    # Make sure to stop reading for cards
                if len(json)>=12:
                    continue_reading = False
                    GPIO.cleanup()
                
            else:
                print("¡Error de autentificación!")
                
print(json)
print(len(json))
json=''.join(json)
json=json.split('}')


myMQTTClient = AWSIoTMQTTClient('Prueba') #Genera una llave aleatoria


Root_CA = "./Certificates/root-ca.pem"
Private_Key = "./Certificates/private.pem.key"
Certificate = "./Certificates/certificate.pem.crt"

myMQTTClient.configureEndpoint("a1bo3h1pmj4c6m-ats.iot.us-east-2.amazonaws.com", 8883)

myMQTTClient.configureCredentials(Root_CA, Private_Key, Certificate)

myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec
print ('Initiating Realtime Data Transfer From Raspberry Pi...')



myMQTTClient.connect()
print("Publishing Message From Raspberry Pi")
sjson='{"Compras":['
for obj in json[:-1]:
    sjson+=obj+'},'
sjson=sjson[:-1] + ']'',"Tienda":'+str(num_tienda)+'}'
myMQTTClient.publish(
        topic="iot/Pan",
        QoS = 1,
        payload=sjson
    )
print(sjson)
import cv2, queue, threading, time
import time
import boto3
import paho.mqtt.client as mqtt
import io
import subprocess
from playsound import playsound
 
 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("Camara/Deteccion")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global video_capture
    global cv2
    global terminado
    global frame
    global image
    global prev
    global frame_rate
    
    print(msg.topic+" "+str(msg.payload.decode('UTF-8')))
    
    #Mensaje de inicializacion recivido
    if str(msg.payload.decode('UTF-8')) == "Pan":
        #Inicializa programa de control de vehiculo  y deteccion de profes
        video_capture.release()
        cv2.destroyAllWindows()
        print("Iniciado deteccion Pan")
        deteeccion_pan=subprocess.run(['xterm', '-T', 'YoloV4', '-e', '/home/pi/Documents/AGVPanaderia/YoloDetect/bin/Release/YoloV4' ,'parking.jpg'])
        video_capture = cv2.VideoCapture(0)
        frame_rate = 2
        prev = 0
        
    elif str(msg.payload.decode('UTF-8')) == "Stop":
        client.publish(topic="Fin",payload="Deteccion Terminaron", qos=1)
        terminado=True
 
def sonido_panes():
    with open('/home/pi/Documents/AGVPanaderia/YoloDetect/pan_detectado.txt','r') as reader:
        pan_detectado_camara=reader.read()
    
    if pan_detectado=="Dona":
        playsound(carpeta_audios+'Dona.mp3')
        
    elif pan_detectado=="Concha":
        playsound(carpeta_audios+'Concha.mp3')
        
    elif pan_detectado=="Muffin":
        playsound(carpeta_audios+'Mofin.mp3')
        
    elif pan_detectado=="Orejita":
        playsound(carpeta_audios+'Orejita.mp3')
        
    elif pan_detectado=="Bolillo":
        playsound(carpeta_audios+'Bolillo.mp3')
             
    playsound(carpeta_audios+'Detectado.mp3')
 

def detectar_profesores(frame):
    global profesor_anterior
    
    try:
        cara=False
        image_binary = cv2.imencode('.jpg', frame)[1].tobytes()
    
        response = rekognition.search_faces_by_image(
             CollectionId='profesores',
             Image={'Bytes':image_binary}                                       
             )
        cara=True    
    except:
        pass
    
    finally:
        if cara:
            found = False
            for match in response['FaceMatches']:
                    
                face = dynamodb.get_item(
                    TableName='profesores',  
                    Key={'RekognitionId': {'S': match['Face']['FaceId']}}
                    )
                
                if 'Item' in face:
                    print ("Found Person: ",face['Item']['FullName']['S'])
                    found = True
                    profesor_encontrado = face['Item']['FullName']['S']
                    
                
            if found and profesor_encontrado!= profesor_anterior:

                if profesor_encontrado=="David Navarro":
                    playsound(carpeta_audios+'Navarro.mp3')
                    print('Saludando Navarro')

                elif profesor_encontrado=="Liz Machado":
                    playsound(carpeta_audios+'Liz.mp3')
                    print('Saludando Liz')
                
                elif profesor_encontrado=="Luis Yepez":
                    playsound(carpeta_audios+'Yepez.mp3')
                    print('Saludando Yepez')
                    
                elif profesor_encontrado=="Adriana":
                    playsound(carpeta_audios+'Adriana.mp3')
                    print('Saludando Adriana')

                elif profesor_encontrado=="Rodrigo Regalado":
                    playsound(carpeta_audios+'Rodrigo.mp3')
                    print('Saludando Rodrigo')
                    
                profesor_anterior=profesor_encontrado
 



carpeta_audios="/home/pi/Documents/AGVPanaderia/Rekognition/Audios/"
rekognition = boto3.client('rekognition', region_name='us-east-2')
dynamodb = boto3.client('dynamodb', region_name='us-east-2')

video_capture = cv2.VideoCapture(0)
frame_rate = 2
prev = 0
profesor_anterior=""
terminado=False

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.137.1", 1883, 60)


client.loop_start()
            
            
while True:
    
    time_elapsed = time.time() - prev
    # Capture frame-by-frame
    err,frame = video_capture.read()

    if time_elapsed > 1./frame_rate:
        
    # Display the resulting frame
        prev = time.time()
        detectar_profesores(frame)
        FPS=1./time_elapsed
        # Using cv2.putText() method
        try:
            image = cv2.putText(frame, "FPS %.2f" % FPS, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (255, 0, 0), 2, cv2.LINE_AA)
            
            
            cv2.imshow('Video', image)
            
            carga_imagen=cv2.waitKey(1) & 0xFF
        except:
            pass
        

    if  terminado== True:
        break

# When everything is done, release the capture
client.publish(topic="AGV/Control",payload="Stop", qos=1)
client.loop_stop()
video_capture.release()
cv2.destroyAllWindows()
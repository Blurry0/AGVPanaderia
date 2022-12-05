import subprocess
import paho.mqtt.client as mqtt


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("AGV/Control")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode('UTF-8')))
    
    #Mensaje de inicializacion recivido
    if msg.payload == b"Start":
        #Inicializa programa de control de vehiculo  y deteccion de profes
        print("Inicializado")
        control_motores=subprocess.Popen(['sudo','python3','/home/pi/Documents/AGVPanaderia/ControlMotor/comunicacion_serial.py'])
        deteccion_profesores=subprocess.Popen(['sudo','python3','/home/pi/Documents/AGVPanaderia/Rekognition/deteccion_profes.py'])
    
    elif msg.payload == b"Stop":
        print("Detenido")
        client.disconnect()

    elif msg.payload == b"DetectRFID":
        #Inicializa programa de control de vehiculo  y deteccion de profes
        lectura_RFID=subprocess.Popen(['sudo','python3','/home/pi/Documents/AGVPanaderia/RFID/read_block.py'])
    
    

#INICIALIZACION DE ARCHVIOS
with open('/home/pi/Documents/AGVPanaderia/RFID/num_tienda.txt','w') as writer:
    writer.write('1')

with open('/home/pi/Documents/AGVPanaderia/YoloDetect/pan_detectado.txt','w') as writer:
    writer.write('')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.137.1", 1883, 60)


client.loop_forever()

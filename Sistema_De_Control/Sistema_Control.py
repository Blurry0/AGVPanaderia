from pynput import keyboard as kb
import paho.mqtt.client as mqtt

# broker_address="192.168.137.1" #APS
broker_address="10.48.211.215" #APS
topicos ={"Motores":"AGV/Motores", "Camara":"Camara/Deteccion", "Control":"AGV/Control"}
process_sim={"Inicio":"Sim/Inicio", "Reset":"Sim/Reset", "Estacion":["Sim/Estacion1", "Sim/Estacion2","Sim/Estacion3"],"Fin":"Sim/Fin"}

client = mqtt.Client()
client.connect(broker_address,1883)
bits = 0b0000
stop = False
tienda = 2
inicio=False
estaciones=False
reinicio=False

def pulsa(tecla):
    global bits
    global client
    
    print(tecla)
    if tecla == kb.KeyCode.from_char('w') or tecla == kb.KeyCode.from_char('s') or tecla == kb.KeyCode.from_char('d') or tecla == kb.KeyCode.from_char('a'):
        if tecla == kb.KeyCode.from_char('w'):
            bits |= 0b0001
        elif tecla == kb.KeyCode.from_char('a'):
            bits |= 0b0010
        elif tecla == kb.KeyCode.from_char('s'):
            bits |= 0b0100
        elif tecla == kb.KeyCode.from_char('d'):
            bits |= 0b1000
        #Enviar "bits" por mqtt a rasp
        client.publish(topicos["Motores"], bits,qos=0)


def suelta(tecla):
    global bits
    global tienda
    global client
    global stop
    global inicio
    global estaciones
    global reinicio

    if tecla == kb.KeyCode.from_char('w') or tecla == kb.KeyCode.from_char('s') or tecla == kb.KeyCode.from_char('d') or tecla == kb.KeyCode.from_char('a'):

        if tecla == kb.KeyCode.from_char('w'):
            bits &= 0b1110
        elif tecla == kb.KeyCode.from_char('a'):
            bits &= 0b1101
        elif tecla == kb.KeyCode.from_char('s'):
            bits &= 0b1011
        elif tecla == kb.KeyCode.from_char('d'):
            bits &= 0b0111
        #Enviar "bits" por mqtt a rasp
        client.publish(topicos["Motores"], bits)

    elif tecla == kb.KeyCode.from_char('k'):
        client.publish(topicos["Control"], "DetectRFID")
        client.publish(process_sim["Estacion"][tienda],"true")
        client.publish(process_sim["Estacion"][tienda],"false")
        if tienda < 2:
            tienda += 1
        else:
            tienda=0
        estaciones=False

    elif tecla == kb.KeyCode.from_char('i'):
        client.publish(topicos["Control"],"Start")
        
    elif tecla == kb.KeyCode.from_char('y'):
        print("Entre")
        client.publish(process_sim["Inicio"],"true")
        client.publish(process_sim["Inicio"],"false")

    elif tecla == kb.KeyCode.from_char('p'):
        client.publish(topicos["Motores"], "Stop")
        stop = True

    elif tecla == kb.KeyCode.from_char('u'):
        client.publish(process_sim["Fin"],"true")
        client.publish(process_sim["Fin"],"false")

    elif tecla == kb.KeyCode.from_char('m'):
        client.publish(topicos["Camara"], "Pan")

    elif tecla == kb.KeyCode.from_char('r'):
        client.publish(process_sim["Reset"],"true")
        client.publish(process_sim["Reset"],"false")

kb.Listener(pulsa,suelta).run()
# Aplicación para escribir bloques de memoria de tags MIFARE 1k
# Desarrollado por Dr. Raúl Crespo S.
# Tecnológico de Monterrey - Campus Ciudad de México

import RPi.GPIO as GPIO
from mfrc522 import MFRC522

def hex_array_str(arr):
    my_str = ""
    for i in range(len(arr)):
        val = arr[i]
        if val < 16:
            my_str = my_str + "0"
        my_str = my_str + str('{0:x}'.format(arr[i])) + " "
    return my_str


input_valid = False
continue_reading = True
# This is the default key for authentication
key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

#Mifare Block number
#block_num = 8

# Variable for the data to write
#data = [0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xAA,0xBB,0xCC,0xDD,0xEE,0xFF]
data = []

# Data read        
backdata = []

# Create an object of the class MFRC522
MIFAREReader = MFRC522()

# Validating the block to write, sector trailer blocks are not permitted
# Validating the data to write, 32 hex characters
# while not(input_valid):
#     # Input data number
#     dato_str = str(input("Ingrese el dato a escribir (32 caract hex): "))
#     if len(dato_str) > 32:
#         print("¡El dato a escribir debe tener menos de 32 caracteres hex!")
#         input_valid = False
#     else:
#         for i in range(0, len(dato_str), 2):
#             data.append(int(dato_str[i:i+2],16))
#         input_valid = True
        
print("Acerque el tag al lector")
datos_escribir =[]
datos1=[ord(i) for i in '{"Pan":"Dona",  ']
datos2=[ord(i) for i in '"Precio":12.50, ']
datos3=[ord(i) for i in '"Fecha":"01-12",']
datos4=[ord(i) for i in '"Can":3}        ']
datos5=[ord(i) for i in '{"Pan":"Orejita"']
datos6=[ord(i) for i in ',"Precio":14.50,']
datos7=[ord(i) for i in '"Fecha":"01-12",']
datos8=[ord(i) for i in '"Can":4}        ']
datos9=[ord(i) for i in '{"Pan":"Bolillo"']
datos10=[ord(i) for i in ',"Precio":3.50, ']
datos11=[ord(i) for i in '"Fecha":"01-12",']
datos12=[ord(i) for i in '"Can":6}        ']
print(datos1)
blockes_no_validos=[7,11,15]
data = [datos1, datos2, datos3, datos4, datos5, datos6, datos7, datos8, datos9, datos10, datos11, datos12]

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
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
        
        i=0
        for block in range(4,19,1):
            if block in blockes_no_validos:
                continue
            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, block, key, uid)
            print("Escribiendo")
            # Check if authenticated
            if status == MIFAREReader.MI_OK:
                
                # Write the data
               
                print(i)
                MIFAREReader.MFRC522_Write(block, data[i])
                i+=1
            
                print("¡Escritura exitosa al bloque %s!" % block)

                # Check to see if it was written
                backdata = MIFAREReader.MFRC522_Read(block)
                
                if backdata != None:
                    print("Ahora el bloque " + str(block) + " tiene el dato: " + "".join([chr(i) for i in backdata]))
                else:
                    print("¡No se pudo verificar lectura del bloque!")            

                # Stop


            else:
                print("Error de autentificación")
                                # Make sure to stop reading for cards
        MIFAREReader.MFRC522_StopCrypto1()
        continue_reading = False
        GPIO.cleanup()

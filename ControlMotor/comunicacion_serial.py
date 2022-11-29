import serial
from time import sleep
import numpy as np
import struct

class SerialCommunication:
    
    bytes_array = []
    decoded_bytes=[]
    
    def __init__(self,port="/dev/ttyS0",
                 baud_rate=115200,
                 timeout=1):
        
        self.ser = serial.Serial(port,baud_rate,timeout=timeout)
        self.ser.reset_input_buffer()

    
            
    def sendMotorDataToArduino(self):
        print("Sending")
        entero=0
        self.ser.write(entero.to_bytes(1, 'little'))
        #self.ser.write(0b00000011)

if __name__ == "__main__":
    ser=SerialCommunication()
    while True:
        ser.sendMotorDataToArduino()
    

#     
#     while True:
#         if ser.state == ser.WAITING:
#             ser.waitingIniByte()
#             
#         elif ser.state ==ser.READING:
#             ser.readingTill16BytesRead()
#             
#         elif ser.state == ser.VALIDATING:
#             ser.checkingIfBufferIsValid()
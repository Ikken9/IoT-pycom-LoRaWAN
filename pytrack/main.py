from network import LoRa
import socket
import time
import binascii
import pycom
import struct
import math as m

from pysense import Pysense
from pytrack import Pytrack
from LIS2HH12 import LIS2HH12
from L76GNSS import L76GNSS

pytrack = Pytrack()
gps = L76GNSS(pytrack, timeout=20)
li = LIS2HH12(pytrack)

# Disable heartbeat LED
pycom.heartbeat(False)

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915)

# create an OTAA authentication parameters, change them to the provided credentials
app_eui = binascii.unhexlify('0000000000000002')
app_key = binascii.unhexlify('FADF3F7331B6C399060715B68C71CF9A')
dev_eui = binascii.unhexlify('70B3D57ED00552BE')

#Uncomment for US915 / AU915 & Pygate
for i in range(0,8):
     lora.remove_channel(i)
for i in range(16,65):
     lora.remove_channel(i)
for i in range(66,72):
     lora.remove_channel(i)

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    pycom.rgbled(0x0A0A08) # white
    time.sleep(2.5)
    print('Not yet joined...')

print('Joined LoRa network')
pycom.rgbled(0x00CC00) # green


# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)



while True:
     s.setblocking(True)
     pycom.rgbled(0x000014)

     send_data = b''

     print('\n\n-----------------------------------')
     print('\n\n** 3-Axis Accelerometer (LIS2HH12)')
     print('Acceleration', li.acceleration())
     print('Roll', li.roll())
     print('Pitch', li.pitch())

     acc_x = bytearray(struct.pack('f',li.acceleration()[0]))
     acc_y = bytearray(struct.pack('f',li.acceleration()[1]))
     acc_z = bytearray(struct.pack('f',li.acceleration()[2]))
     send_data += acc_x + acc_y + acc_z

     print('\n\n** GPS Sensor (L76GNSS)')
     coordenadas = gps.coordinates()
     print('Coordinates\nLongitud: ' + coordenadas[0] + '\nLatitud: ' + coordenadas[1])
     send_data += coordenadas[0] + coordenadas[1]

     print('Sending data (uplink)...')
     s.send(send_data)
     s.setblocking(False)
     print('Data Sent: ', bytes(send_data))
     pycom.rgbled(0x140000)
     time.sleep(1)
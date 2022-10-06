from network import LoRa
import socket
import time
import binascii
import pycom
import struct
import math as m

from pysense import Pysense
from pytrack import Pytrack
from SI7006A20 import SI7006A20 
from MPL3115A2 import MPL3115A2, ALTITUDE, PRESSURE
from LIS2HH12 import LIS2HH12
from LTR329ALS01 import LTR329ALS01
from L76GNSS import L76GNSS

pysense = Pysense()
pytrack = Pytrack()
si = SI7006A20(pysense)
li = LIS2HH12(pysense)
lt = LTR329ALS01(pysense)
gps = L76GNSS(pytrack)

mpPress = MPL3115A2(pysense, mode=PRESSURE)

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

    print('\n\n** Digital Ambient Light Sensor (LTR-329ALS-01)')
    print('Light', lt.light())
    red = bytearray(struct.pack('H',lt.light()[0]))
    blue = bytearray(struct.pack('H',lt.light()[1]))
    send_data += red + blue

    print('\n\n** GPS Sensor (L76GNSS)')
    print('Coordinates', gps.getCoordinates())
    lon = bytearray(struct.pack('Longitude',gps.getCoordinates()[0]))
    lat = bytearray(struct.pack('Latitude',gps.getCoordinates()[1]))
    send_data += lon + lat

    print('\n\n** Humidity and Temperature Sensor (SI7006A20)')
    print('Humidity', si.humidity())
    print('Temperature', si.temperature())
    temperature = bytearray(struct.pack('f',si.temperature()))
    send_data += temperature

    mpPress = MPL3115A2(pysense, mode=PRESSURE)
    print('\n\n** Barometric Pressure Sensor with Altimeter (MPL3115A2)')
    print('Pressure (hPa)', mpPress.pressure()/100)

    mpAlt = MPL3115A2(pysense ,mode=ALTITUDE)
    print('Altitude', mpAlt.altitude())
    print('Temperature', mpAlt.temperature())

    print('Sending data (uplink)...')
    s.send(send_data)
    s.setblocking(False)
    print('Data Sent: ', bytes(send_data))
    pycom.rgbled(0x140000)
    time.sleep(1)
# coding=utf-8
# Based on RPI code from https://github.com/switchdoclabs/SDL_Pi_HDC1000/blob/master/SDL_Pi_HDC1000.py
# Rewritten for micropython by Hans Christian Winther-Sorensen
#
# SDL_Pi_HDC1000
# Raspberry Pi Driver for the SwitchDoc Labs HDC1000 Breakout Board
#
# SwitchDoc Labs
# January 2017
#
# Version 1.1
import array
import time
import machine

# constants

# I2C Address
HDC1000_ADDRESS = 0x40  # 1000000
# Registers
HDC1000_TEMPERATURE_REGISTER = 0x00
HDC1000_HUMIDITY_REGISTER = 0x01
HDC1000_CONFIGURATION_REGISTER = 0x02
HDC1000_MANUFACTURERID_REGISTER = 0xFE
HDC1000_DEVICEID_REGISTER = 0xFF
HDC1000_SERIALIDHIGH_REGISTER = 0xFB
HDC1000_SERIALIDMID_REGISTER = 0xFC
HDC1000_SERIALIDBOTTOM_REGISTER = 0xFD

# Configuration Register Bits

HDC1000_CONFIG_RESET_BIT = 0x8000
HDC1000_CONFIG_HEATER_ENABLE = 0x2000
HDC1000_CONFIG_ACQUISITION_MODE = 0x1000
HDC1000_CONFIG_BATTERY_STATUS = 0x0800
HDC1000_CONFIG_TEMPERATURE_RESOLUTION = 0x0400
HDC1000_CONFIG_HUMIDITY_RESOLUTION_HBIT = 0x0200
HDC1000_CONFIG_HUMIDITY_RESOLUTION_LBIT = 0x0100

HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT = 0x0000
HDC1000_CONFIG_TEMPERATURE_RESOLUTION_11BIT = 0x0400

HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT = 0x0000
HDC1000_CONFIG_HUMIDITY_RESOLUTION_11BIT = 0x0100
HDC1000_CONFIG_HUMIDITY_RESOLUTION_8BIT = 0x0200

I2C_SLAVE = 0x0703


class HDC1000(object):
    def __init__(self, i2c, addr=HDC1000_ADDRESS):
        assert isinstance(i2c, machine.I2C)
        self.i2c = i2c
        self.address = addr

        config = HDC1000_CONFIG_ACQUISITION_MODE

        s = [HDC1000_CONFIGURATION_REGISTER, config >> 8, 0x00]
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)  # sending config register bytes
        time.sleep(0.015)  # From the data sheet

    def read_temperature(self):
        s = [HDC1000_TEMPERATURE_REGISTER]  # temp
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)
        time.sleep(0.0625)  # From the data sheet

        data = self.i2c.readfrom(self.address, 2)  # read 2 byte temperature data
        buf = array.array('B', data)
        # print ( "Temp: %f 0x%X %X" % (  ((((buf[0]<<8) + (buf[1]))/65536.0)*165.0 ) - 40.0   ,buf[0],buf[1] )  )

        # Convert the data
        temp = (buf[0] * 256) + buf[1]
        cTemp = (temp / 65536.0) * 165.0 - 40
        return cTemp

    def read_humidity(self):
        # Send humidity measurement command, 0x01(01)
        time.sleep(0.015)  # From the data sheet

        s = [HDC1000_HUMIDITY_REGISTER]  # hum
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)
        time.sleep(0.0625)  # From the data sheet

        data = self.i2c.readfrom(self.address, 2)  # read 2 byte humidity data
        buf = array.array('B', data)
        # print ( "Humidity: %f 0x%X %X " % (  ((((buf[0]<<8) + (buf[1]))/65536.0)*100.0 ),  buf[0], buf[1] ) )
        humidity = (buf[0] * 256) + buf[1]
        humidity = (humidity / 65536.0) * 100.0
        return humidity

    def read_config_register(self):
        # Read config register

        s = [HDC1000_CONFIGURATION_REGISTER]  # temp
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)
        time.sleep(0.0625)  # From the data sheet

        data = self.i2c.readfrom(self.address, 2)  # read 2 byte config data

        buf = array.array('B', data)

        # print "register=%X %X"% (buf[0], buf[1])
        return buf[0] * 256 + buf[1]

    def turn_heater_on(self):
        # Read config register
        config = self.read_config_register()
        config = config | HDC1000_CONFIG_HEATER_ENABLE
        s = [HDC1000_CONFIGURATION_REGISTER, config >> 8, 0x00]
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)  # sending config register bytes
        time.sleep(0.015)  # From the data sheet

    def turn_heater_off(self):
        # Read config register
        config = self.read_config_register()
        config = config & ~HDC1000_CONFIG_HEATER_ENABLE
        s = [HDC1000_CONFIGURATION_REGISTER, config >> 8, 0x00]
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)  # sending config register bytes
        time.sleep(0.015)  # From the data sheet

    def set_humidity_resolution(self, resolution):
        # Read config register
        config = self.read_config_register()
        config = (config & ~0x0300) | resolution
        s = [HDC1000_CONFIGURATION_REGISTER, config >> 8, 0x00]
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)  # sending config register bytes
        time.sleep(0.015)  # From the data sheet

    def set_temperature_resolution(self, resolution):
        # Read config register
        config = self.read_config_register()
        config = (config & ~0x0400) | resolution

        s = [HDC1000_CONFIGURATION_REGISTER, config >> 8, 0x00]
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)  # sending config register bytes
        time.sleep(0.015)  # From the data sheet

    def read_battery_status(self):
        # Read config register
        config = self.read_config_register()
        config = config & ~ HDC1000_CONFIG_HEATER_ENABLE

        if config == 0:
            return True
        else:
            return False

    def read_manufacturer_id(self):
        s = [HDC1000_MANUFACTURERID_REGISTER]  # temp
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)
        time.sleep(0.0625)  # From the data sheet

        data = self.i2c.readfrom(self.address, 2)  # read 2 byte config data

        buf = array.array('B', data)
        return buf[0] * 256 + buf[1]

    def read_device_id(self):
        s = [HDC1000_DEVICEID_REGISTER]  # temp
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)
        time.sleep(0.0625)  # From the data sheet

        data = self.i2c.readfrom(self.address, 2)  # read 2 byte config data

        buf = array.array('B', data)
        return buf[0] * 256 + buf[1]

    def read_serial_number(self):
        serialNumber = 0

        s = [HDC1000_SERIALIDHIGH_REGISTER]  # temp
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)
        time.sleep(0.0625)  # From the data sheet
        data = self.i2c.readfrom(self.address, 2)  # read 2 byte config data
        buf = array.array('B', data)
        serialNumber = buf[0] * 256 + buf[1]

        s = [HDC1000_SERIALIDMID_REGISTER]  # temp
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)
        time.sleep(0.0625)  # From the data sheet
        data = self.i2c.readfrom(self.address, 2)  # read 2 byte config data
        buf = array.array('B', data)
        serialNumber = serialNumber * 256 + buf[0] * 256 + buf[1]

        s = [HDC1000_SERIALIDBOTTOM_REGISTER]  # temp
        s2 = bytearray(s)
        self.i2c.writeto(self.address, s2)
        time.sleep(0.0625)  # From the data sheet
        data = self.i2c.readfrom(self.address, 2)  # read 2 byte config data
        buf = array.array('B', data)
        serialNumber = serialNumber * 256 + buf[0] * 256 + buf[1]

        return serialNumber

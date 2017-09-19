import wx
import serial
import glob
import threading
from wx.lib.pubsub import pub
from wx.lib.pubsub import setupkwargs
import time
import os
import platform
import logging
import common


def list_serial_ports():
    """"
        scan current connected port names
    """
    system_name = platform.system()

    if system_name == "Windows":
        # Scan for available ports.
        available = []

        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append(i)
                s.close()
            except serial.SerialException:
                pass
        return available

    else:
        # Assume Linux
        return glob.glob('/dev/ttyA*') + glob.glob('/dev/ttyUSB*')


def get_serial_ports():

    strippedPortNames = []
    lengthOfPortNameList = 0
    portNames = list_serial_ports()

    for i in portNames:
        tmpPortNames = i[8:]
        strippedPortNames.append(tmpPortNames)

    lengthOfPortNameList = len(portNames)
    print('Stripped port names: ', strippedPortNames)
    return strippedPortNames, lengthOfPortNameList


class PollPortName(threading.Thread):
    def __init__(self):

        self.scannedSerialPort = None
        self.serialPortList = []

        th = threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()    # start the thread


    def run(self):
        self.connect_port()

        while True:

            # do we have something connected to the serial port?
            if (self.serialPortList):
                wx.CallAfter(pub.sendMessage, "TOPIC_PORTNAME", serialPort=self.scannedSerialPort, serialPortName=self.serialPortList[0][8:])
                self.serialPortList = glob.glob('/dev/ttyA*') + glob.glob('/dev/ttyUSB*')
            else:
                wx.CallAfter(pub.sendMessage, "TOPIC_PORTNAME", serialPort=None, serialPortName='No port')
                self.connect_port()

            time.sleep(common.DELAY_1)

    def connect_port(self):

        self.serialPortList = glob.glob('/dev/ttyA*') + glob.glob('/dev/ttyUSB*')

        # if nothing is connected to serial port then just don't do anything
        if (self.serialPortList):
            logging.info('serialPortList=%s', self.serialPortList)

            self.scannedSerialPort = serial.Serial(port = self.serialPortList[0],
                                                   baudrate = 9600,
                                                   parity = serial.PARITY_NONE,
                                                   stopbits = serial.STOPBITS_ONE,
                                                   bytesize = serial.EIGHTBITS,
                                                   timeout = 1)

        else:
            #logging.info('No remote controller connected to serial port')
            time.sleep(common.DELAY_1)

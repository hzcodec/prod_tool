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
                self.serialPortList = glob.glob('/dev/ttyA*') + glob.glob('/dev/ttyUSB*')
                wx.CallAfter(pub.sendMessage, "TOPIC_PORTNAME", serialPort=self.scannedSerialPort, serialPortName=self.serialPortList[0][8:])

            else:
                print 'Still no connection'
                self.connect_port()


            # if port exists
            # if (os.path.exists(portName) == True and self.lock == False):
            #     self.portIsDisconnected = False
            #     self.portIsConnected = True
            #     self.lock = True
            #     self.sentPortName = portName
            #     logging.info('Port is connected to: %s', portName)
            #     wx.CallAfter(pub.sendMessage, "TOPIC_PORTNAME", serialPort=ser, serialPortName=portName)
            #
            # # if port does not exists
            # elif (os.path.exists(portName) == False and self.lock == True):
            #     self.portIsDisconnected = True
            #     self.portIsConnected = False
            #     self.lock = False
            #     self.lock2 = True
            #     self.sentPortName = 'Connection lost'
            #     logging.info('Port is disconnected')
            #     wx.CallAfter(pub.sendMessage, "TOPIC_PORTNAME", serialPort=None, serialPortName='None')
            #
            # if (self.portIsConnected == True and self.portIsClosed == True):
            #     logging.info('Reconnect: %s', portName)
            #     time.sleep(1)
            #     self.connect_port()
            #
            # #if (ser.isOpen() and self.portIsConnected == True):
            # if (self.portIsConnected == True):
            #     self.portIsClosed = False
            #
            # elif (self.lock2 == True):
            #     ser.close()
            #     self.portIsClosed = True
            #     self.lock2 = False
            #     logging.info('Port closed')

            time.sleep(1)

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
            print 'Nothing connected to serial port'

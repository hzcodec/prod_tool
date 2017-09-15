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

    return strippedPortNames, lengthOfPortNameList


class PollPortName(threading.Thread):
    def __init__(self):
        logging.basicConfig(format="%(filename)s: %(funcName)s() - %(message)s", level=logging.INFO)
        logging.info('Polling USB port started')

        self.portIsConnected = False
        self.portIsDisconnected = False
        self.portIsClosed = False
        self.lock = False
        self.lock2 = False
        self.sentPortName = 'Connect USB cable'
        self.tmpList = []

        th = threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()    # start the thread

    def run(self):
        ser, portName = self.connect_port()

        while True:

            if (portName == 'No device'):
                self.tmpList = glob.glob('/dev/ttyA*') + glob.glob('/dev/ttyUSB*')

                if not (self.tmpList):
                    pass
                else:
                    portName = self.tmpList[0]

            # if port exists
            if (os.path.exists(portName) == True and self.lock == False):
                self.portIsDisconnected = False
                self.portIsConnected = True
                self.lock = True
                self.sentPortName = portName
                print '\nPort is connected to:', portName

            # if port does not exists
            elif (os.path.exists(portName) == False and self.lock == True):
                self.portIsDisconnected = True
                self.portIsConnected = False
                self.lock = False
                self.lock2 = True
                self.sentPortName = 'Connection lost'
                print '\nPort is disconnected'

            if (self.portIsConnected == True and self.portIsClosed == True):
                print 'Reconnect: ' + portName
                time.sleep(1)
                ser, portName = self.connect_port()

            if (ser.isOpen() and self.portIsConnected == True):
                self.portIsClosed = False

            elif (self.lock2 == True):
                ser.close()
                self.portIsClosed = True
                self.lock2 = False
                print 'Port closed'

            wx.CallAfter(pub.sendMessage, "TOPIC_PORTNAME", msg=self.sentPortName)
            time.sleep(1)

    def connect_port(self):
        try:
            tempList = glob.glob('/dev/ttyA*') + glob.glob('/dev/ttyUSB*')
            print 'Read port names:', tempList

            ser = serial.Serial()
            ser.braudrate = 9600
            ser.port = tempList[0]
            ser.open()

        except:
            print 'No connection'
            tempList.append('No device')
            #sys.exit()

        if ser.isOpen():
            print("Serial port is open")

        return ser, tempList[0]

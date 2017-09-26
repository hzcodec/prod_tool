import wx
import serial
import logging
import time
import platform
import glob
from wx.lib.pubsub import pub
from wx.lib.pubsub import setupkwargs
import common
import poll_port as pp


class DownLoaderForm(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        logging.basicConfig(format="%(filename)s: %(funcName)s() - %(message)s", level=logging.INFO)
        #logging.info('Length of PARAMETER_NAMES list: %d', len(PARAMETER_NAMES))

        self.lengthOfPortNameList = 0
        self.serialPort = None
        self.strippedSerialPortNames = None
        self.lock = False

        downloadSizer = self.setup_serial_sizer()
        versionSizer = self.setup_version_sizer()
        configSizer = self.setup_config_sizer()

        self.connected = False # flag indicating if connection to serial port is established

        topSizer = wx.BoxSizer(wx.VERTICAL)
        topSizer.Add(downloadSizer, 0, wx.TOP|wx.LEFT, 10)
        topSizer.Add(versionSizer, 0, wx.TOP|wx.LEFT, 10)
        topSizer.Add(configSizer, 0, wx.TOP|wx.LEFT, 10)
        self.SetSizer(topSizer)

        pub.subscribe(self.configListener, 'TOPIC_CONFIG_LISTENER')
        pub.subscribe(self.serialListener, 'TOPIC_SERIAL_LISTENER')
        pub.subscribe(self.portScannedName, 'TOPIC_PORTNAME')

        self.btnSaveParam.Enable(False)

        pp.PollPortName() # start polling port thread
        time.sleep(common.DELAY_03)

    def get_remote_controller_version(self, select):
        time.sleep(common.DELAY_05)
        logging.info('Read remote controller version from serial port: %s, select=%d', self.serialPort, select)

        # if port is connected
        if select == 1:
            self.remoteVersion = pp.serial_read('r_v', 70, self.serialPort)

            rVersion = self.remoteVersion.split("r_v")
            print self.remoteVersion
            self.lblRemoteVersion.SetForegroundColour(common.BLACK)
            self.lblRemoteVersion.SetLabel(rVersion[1])

            self.connected = True
        else:
            self.lblRemoteVersion.SetLabel(' ')
            self.connected = False

    def get_ascender_version(self, select):
        time.sleep(common.DELAY_05)

        # if port is connected
        if select == 1:

            self.ascenderVersion = pp.serial_read('v', 60, self.serialPort)
            aVersion = self.ascenderVersion.split("v")

            if aVersion[1][2:9] != 'Unjo 50':
                self.lblAscenderVersion.SetForegroundColour(common.RED)
                self.lblAscenderVersion.SetLabel('\nIs Ascender connected to remote controller?')
            else:
                self.lblAscenderVersion.SetForegroundColour(common.BLACK)
                self.lblAscenderVersion.SetLabel(aVersion[1])

        else:
            self.lblAscenderVersion.SetForegroundColour(common.RED)
            self.lblAscenderVersion.SetLabel(' ')

        time.sleep(common.DELAY_05)

    def serialListener(self, message, fname=None):
        logging.info('')
        # TODO: shall mySer be initialized in __init__? It is but maybe not used anymore instead serialPort shall be used
        self.mySer = message

    def configListener(self, message, fname=None):
        """
            Handle configuration data read from 'Open'.
            All parameters are stored in configParameters.
        """
        fileLength = sum(1 for line in message)

        logging.info('File name: %s, length: %d', fname, fileLength)
        self.configParameters = message
        self.configurationFileName = fname

        # resize gauge according to configuration file length
        self.gauge.SetRange(fileLength-1)

    def portScannedName(self, serialPort, serialPortName):
        self.serialPort = serialPort

        if (serialPort == None):
            #logging.info('Port is not available: %s', serialPort)
            self.lblConnect.SetForegroundColour(common.RED)
            self.lblConnect.SetLabel('No connection')
            self.lock = False
            self.get_remote_controller_version(common.Port.PORT_NOT_AVAILABLE)
            self.get_ascender_version(common.Port.PORT_NOT_AVAILABLE)

        else:
            #logging.info('Port is available @ port name: %s', serialPortName)
            self.lblConnect.SetForegroundColour(common.GREEN)
            self.lblConnect.SetLabel("Connected to " + serialPortName)

            # can only to this once otherwise the GUI i fucked up
            if (self.lock == False):
                self.get_remote_controller_version(common.Port.PORT_AVAILABLE)
                self.get_ascender_version(common.Port.PORT_AVAILABLE)
                self.lock = True

                # TODO: send message to trace, ...
                # calibration, downloader, prodtest and trace are receiver
                pub.sendMessage('TOPIC_SERIAL_LISTENER', message=self.serialPort)

    def print_parameters(self):
        """
            Update filename in Configuration sizer.
            Then extract parameters.
        """
        logging.info('')
        self.config_parameters()

    def config_parameters(self):
        """
            Configure parameters via serial IF.
            Parameters are configured with 'param set' command when
            is selected via Open.
            Save param button is disabled during configuration.
        """
        if (self.connected == True):

            self.btnSaveParam.Enable(False)
            parListLength = len(self.configParameters)
            logging.info('Par list length: %s', parListLength)
            font = wx.Font(11, wx.DEFAULT, wx.ITALIC, wx.NORMAL)
            self.txtFileName.SetFont(font)
            self.txtFileName.SetLabel(self.configurationFileName)

            # get all parameters and its corresponding command
            for parIndex in range(0, parListLength):
                par1 = self.configParameters[parIndex]
                par2 = par1.split(',')
                par3 = par2[1].strip('\n')
                local_cmd = 'param set ' + par2[0] + par3

                print '[%d] - %s' % (parIndex, local_cmd)
                # TODO: this is commented for debug reason, should be uncomment for production
                #pp.serial_cmd(local_cmd, self.mySer)
                time.sleep(common.DELAY_03)
                self.gauge.SetValue(parIndex)
                wx.Yield()

            self.btnSaveParam.Enable(True)
        else:
            self.lblConnect.SetForegroundColour(common.RED)
            self.lblConnect.SetLabel("Port not Connected")

    def setup_serial_sizer(self):
        txtSerialPort = wx.StaticText(self, wx.ID_ANY, 'Serial Port:')
        txtSerPortSizer = wx.BoxSizer(wx.HORIZONTAL)
        txtSerPortSizer.Add(txtSerialPort, 0, wx.TOP, common.TEXT_SERIAL_PORT_BORDER)

        statBoxSerial = wx.StaticBox(self, wx.ID_ANY, '  Serial connection    ')
        statBoxSerial.SetBackgroundColour(common.GREY)
        statBoxSerial.SetForegroundColour(common.BLACK)
        statBoxSizer = wx.StaticBoxSizer(statBoxSerial, wx.HORIZONTAL)

        self.lblConnect = wx.StaticText(self, label= 'Not connected')

        txtNull = wx.StaticText(self, wx.ID_ANY, ' ')

        statBoxSizer.Add(txtSerPortSizer, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 15)
        statBoxSizer.Add(self.lblConnect, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 25)
        statBoxSizer.Add(txtNull, 0, wx.LEFT, 782) # this magic number is just to get the statBoxSerial larger

        return statBoxSizer

    def setup_version_sizer(self):
        statBoxDownload = wx.StaticBox(self, wx.ID_ANY, '  Version')
        statBoxDownload.SetBackgroundColour(common.GREY)
        statBoxDownload.SetForegroundColour(common.BLACK)
        statBoxSizer = wx.StaticBoxSizer(statBoxDownload, wx.VERTICAL)

        txtNull  = wx.StaticText(self, wx.ID_ANY, ' ')
        txtNull2 = wx.StaticText(self, wx.ID_ANY, ' ')

        ascenderVersionHeadline = wx.StaticText(self, -1, "Ascender Version:")
        self.lblAscenderVersion = wx.StaticText(self, -1, "\nno version")
        ascenderASizer = wx.BoxSizer(wx.HORIZONTAL)
        ascenderASizer.Add(ascenderVersionHeadline, 0, wx.TOP|wx.RIGHT, 20)

        ascenderBSizer = wx.BoxSizer(wx.HORIZONTAL)
        ascenderBSizer.Add(self.lblAscenderVersion, 0, wx.TOP, 3)
        ascenderSizer = wx.BoxSizer(wx.HORIZONTAL)
        ascenderSizer.Add(ascenderASizer, 0, wx.ALL, 5)
        ascenderSizer.Add(ascenderBSizer, 0, wx.ALL, 5)

        remoteVersionHeadline = wx.StaticText(self, -1, "Remote Version:")
        self.lblRemoteVersion = wx.StaticText(self, -1, "\nno version")
        remoteASizer = wx.BoxSizer(wx.HORIZONTAL)
        remoteASizer.Add(remoteVersionHeadline, 0, wx.TOP|wx.RIGHT, 20)
        remoteBSizer = wx.BoxSizer(wx.HORIZONTAL)
        remoteBSizer.Add(self.lblRemoteVersion, 0, wx.TOP, 0)
        remoteSizer = wx.BoxSizer(wx.HORIZONTAL)
        remoteSizer.Add(remoteASizer, 0, wx.ALL, 5)
        remoteSizer.Add(remoteBSizer, 0, wx.ALL, 10)

        statBoxSizer.Add(ascenderSizer, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 10)
        statBoxSizer.Add(remoteSizer, 0, wx.BOTTOM|wx.LEFT, 10)
        statBoxSizer.Add(txtNull, 0, wx.LEFT, 1000)
        statBoxSizer.Add(txtNull2, 0, wx.BOTTOM, 5)

        return statBoxSizer

    def setup_config_sizer(self):
        statBoxDownload = wx.StaticBox(self, wx.ID_ANY, '  Configuration')
        statBoxDownload.SetBackgroundColour(common.GREY)
        statBoxDownload.SetForegroundColour(common.BLACK)
        statBoxSizer = wx.StaticBoxSizer(statBoxDownload, wx.VERTICAL)

        txtNull = wx.StaticText(self, wx.ID_ANY, ' ')

        self.txtConfiguration = wx.StaticText(self, -1, "Configuration file:")
        self.txtFileName = wx.StaticText(self, -1, "No config file selected")

        self.gauge = wx.Gauge(self, range = 55, size = (250, 25))
        gaugeSizer = wx.BoxSizer(wx.HORIZONTAL)
        gaugeSizer.Add(self.gauge, 0, wx.LEFT, 90)

        configSizer = wx.BoxSizer(wx.HORIZONTAL)
        configSizer.Add(self.txtConfiguration, 0, wx.TOP|wx.LEFT, 10)
        configSizer.Add(self.txtFileName, 0, wx.TOP|wx.LEFT, 10)
        configSizer.Add(gaugeSizer, 0, wx.TOP|wx.LEFT, 5)

        self.btnSaveParam= wx.Button(self, wx.ID_ANY, 'Param Save')
        self.Bind(wx.EVT_BUTTON, self.onSaveParam, self.btnSaveParam)

        statBoxSizer.Add(configSizer, 0, wx.ALL, 15)
        statBoxSizer.Add(self.btnSaveParam, 0, wx.ALL, 15)
        statBoxSizer.Add(txtNull, 0, wx.LEFT, 1000)

        return statBoxSizer

    def onConnect(self, event):
        self.get_remote_controller_version()

    def onCombo(self, event):
        logging.info('')

    def onSaveParam(self, event):
        # TODO: add check if param file has been loaded
        logging.info('')
        pp.serial_cmd('param save', self.mySer)
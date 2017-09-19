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

# current parameters
PARAMETER_NAMES = ['motor.cl.kp', 'motor.cl.ki', 'motor.cl.kt', 'motor.cl.max', 'motor.cl.min', \
                   'motor.sl.kp', 'motor.sl.ki', 'motor.sl.kt', 'motor.sl.max', 'motor.sl.min', \
                    'trajec.acc', 'trajec.ret', 'throttle.zero', 'throttle.down', 'throttle.up', \
                    'throttle.deadband_on', 'throttle.deadband_off', 'throttle.has_switch', 'num_motor_ch', \
                    'power_out', 'power_in', 'brake_temp_ok', 'brake_temp_hi', 'brake_max_id', \
                    'angle_offset', 'alignment_current', \
                    'sin_bias', 'sin_gain', 'cos_bias', 'cos_gain', \
                    'brake_test.pos_ratio', 'brake_test.neg_ratio', 'psu_ok', 'led.brightness_hi', 'led.brightness_lo', \
                    'idreg.kp', 'idreg.ki', 'idreg.kt', 'power_margin', 'power_factor', \
                    'speed_filter', 'max_motor_temp', 'idle_timeout', 'remote_ctrl_timeout', 'soc_lim_run_up', \
                    'max_drive_temp', 'dominant_throttle_on', 'rope_stuck_on', 'iq_alpha', 'speed_alpha', \
                    'mx', 'mi', 'delay_start', 'speed_lim', 'undershoot', 'ti']


def serial_cmd(cmd, serial):
    # send command to serial port
    try:
        serial.write(cmd + '\r');
    except:
        logging.info('Not connected')


def serial_read(cmd, no, serial):
    # send command to serial port
    serial.write(cmd+'\r');
    #serial.reset_input_buffer()
    serial.reset_output_buffer()
    serial.flush()

    # read data from serial port
    c = serial.read(no)
    return c


class DownLoaderForm(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        logging.basicConfig(format="%(filename)s: %(funcName)s() - %(message)s", level=logging.INFO)
        logging.info('Length of PARAMETER_NAMES list: %d', len(PARAMETER_NAMES))

        self.ser = None
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

        # TODO: rename configListener in trace.py and in main.py
        pub.subscribe(self.configListener, 'TOPIC_CONFIG_LISTENER')
        pub.subscribe(self.serialListener, 'TOPIC_SERIAL_LISTENER')
        pub.subscribe(self.portScannedName, 'TOPIC_PORTNAME')

        self.parameter_names_length = len(PARAMETER_NAMES)
        self.btnSaveParam.Enable(False)

        pp.PollPortName() # start polling port thread
        time.sleep(common.DELAY_03)

    def get_remote_controller_version(self, select):
        time.sleep(common.DELAY_05)
        #logging.info('Read remote controller version from serial port: %s', self.serialPort)

        if (select == 1):
            self.remoteVersion = serial_read('r_v', 70, self.serialPort)

            rVersion = self.remoteVersion.split("r_v")
            print self.remoteVersion
            self.lblRemoteVersion.SetForegroundColour(common.BLACK)
            self.lblRemoteVersion.SetLabel(rVersion[1])
        else:
            self.lblRemoteVersion.SetLabel(' ')

    def get_ascender_version(self, select):
        time.sleep(common.DELAY_05)

        if (select == 1):

            self.ascenderVersion = serial_read('v', 60, self.serialPort)
            aVersion = self.ascenderVersion.split("v")
            print aVersion[1]

            #if (aVersion[1][2:6] == 'Unjo'):
            self.lblAscenderVersion.SetForegroundColour(common.BLACK)
            self.lblAscenderVersion.SetLabel(aVersion[1])

        else:
                self.lblAscenderVersion.SetForegroundColour(common.RED)
                self.lblAscenderVersion.SetLabel(' ')


        time.sleep(common.DELAY_05)

    def serialListener(self, message, fname=None):
        logging.info('')
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
            self.get_remote_controller_version(0)
            self.get_ascender_version(0)

        else:
            #logging.info('Port is available @ port name: %s', serialPortName)
            self.lblConnect.SetForegroundColour(common.GREEN)
            self.lblConnect.SetLabel("Connected to " + serialPortName)

            # can only to this once otherwise the GUI i fucked up
            if (self.lock == False):
                self.get_remote_controller_version(1)
                self.get_ascender_version(1)
                self.lock = True

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
                local_cmd = 'param set ' + PARAMETER_NAMES[parIndex] + par3

                print '[%d] - %s' % (parIndex, local_cmd)
                serial_cmd(local_cmd, self.mySer)
                time.sleep(common.DELAY_03)
                self.gauge.SetValue(parIndex)
                wx.Yield()

            self.btnSaveParam.Enable(True)

        else:
            self.lblConnect.SetForegroundColour(common.RED)
            self.lblConnect.SetLabel("Port not Connected")

    def setup_serial_sizer(self):
        txtSerialPort = wx.StaticText(self, wx.ID_ANY, 'Select serial port')
        txtSerPortSizer = wx.BoxSizer(wx.HORIZONTAL)
        txtSerPortSizer.Add(txtSerialPort, 0, wx.TOP, common.TEXT_SERIAL_PORT_BORDER)

        # get current port names like ACM0 from /dev/ttyACM0
        strippedPortNames, self.lengthOfPortNameList = pp.get_serial_ports()

        self.comboBox = wx.ComboBox(self, choices=strippedPortNames)
        self.comboBox.SetSelection(0) # preselect ACM0
        self.comboBox.Bind(wx.EVT_COMBOBOX, self.onCombo)

        comboSizer = wx.BoxSizer(wx.HORIZONTAL)
        comboSizer.Add(self.comboBox, 0, wx.TOP, 10)

        statBoxSerial = wx.StaticBox(self, wx.ID_ANY, '  Serial connection    ')
        statBoxSerial.SetBackgroundColour(common.GREY)
        statBoxSerial.SetForegroundColour(common.BLACK)
        statBoxSizer = wx.StaticBoxSizer(statBoxSerial, wx.HORIZONTAL)

        btnConnect = wx.Button(self, wx.ID_ANY, 'Connect')
        self.Bind(wx.EVT_BUTTON, self.onConnect, btnConnect)
        self.lblConnect = wx.StaticText(self, label= 'Not connected')

        txtNull = wx.StaticText(self, wx.ID_ANY, ' ')

        statBoxSizer.Add(txtSerPortSizer, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 15)
        statBoxSizer.Add(comboSizer, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 10)
        statBoxSizer.Add(btnConnect, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 20)
        statBoxSizer.Add(self.lblConnect, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 25)
        statBoxSizer.Add(txtNull, 0, wx.LEFT, 545) # this is just to get the statBoxSerial larger

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
        serial_cmd('param save', self.mySer)
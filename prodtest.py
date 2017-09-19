import wx
import time
import logging
from wx.lib.pubsub import pub
from wx.lib.pubsub import setupkwargs
import common

BORDER1 = 5
TEXT_SERIAL_PORT_BORDER = 10


def serial_cmd(cmd, serial):
    # send command to serial port
    try:
        serial.write(cmd + '\r');
    except:
        logging.info('Not connected')

def serial_read(cmd, no, serial):
    # send command to serial port
    serial.write(cmd+'\r');
    serial.reset_input_buffer()
    serial.reset_output_buffer()
    serial.flush()

    # read data from serial port
    c = serial.read(no)
    return c


class ProdTestForm(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

         # Add a panel so it looks the correct on all platforms
         #self.panel = wx.Panel(self, wx.ID_ANY)

        # flag is function is active
        self.toggle = False

        # initialize variables, need to be done if connection not has been done
        self.oldClMax            = 0.0
        self.oldClMin            = 0.0
        self.oldSlKi             = 0.0
        self.oldSlMax            = 0.0
        self.oldSlMin            = 0.0
        self.oldHasSwitch        = 0
        self.oldPowerMargin      = 0.0
        self.oldPowerFactor      = 0.0
        self.oldBrightnessLo     = 0.0
        self.oldBrakeTempOk      = 0.0
        self.oldBrakeTempHi      = 0.0
        self.oldBrakeMaxId       = 0.0
        self.oldBrakePosRatio    = 0.0
        self.oldTrajecAcc        = 0.0
        self.oldTrajecRet        = 0.0
        self.oldDominantThrottle = 0.0
        self.oldMaxMotorTemp     = 0.0
        self.oldNumMotorCh       = 0.0
        self.oldIdleTimeout      = 0.0
        self.oldRopeStuckOn      = 0
        self.oldIqAlpha          = 0.00
        self.oldSpeedAlpha       = 0.00
        self.oldUndershoot       = 0.00
        self.oldSpeedLim         = 0.00
        self.oldDelayStart       = 0

        configParamsSizer = self.setup_config_params()
        enhancedMeasSizer = self.setup_test_enahanced_measuring()
        testRun = self.setup_test_run()
        multiTextControl = self.setup_multi_text_control()

        leftTopSizer = wx.BoxSizer(wx.VERTICAL)
        leftTopSizer.Add(configParamsSizer, 0, wx.ALL|wx.EXPAND, BORDER1)
        leftTopSizer.Add(enhancedMeasSizer, 0, wx.ALL|wx.EXPAND, BORDER1)
        leftTopSizer.Add(testRun, 0, wx.ALL|wx.EXPAND, BORDER1)
        leftTopSizer.Add(multiTextControl, 0, wx.ALL|wx.EXPAND, BORDER1)
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(leftTopSizer, 0, wx.ALL, BORDER1)

        self.SetSizer(topSizer)
        self.lock_text_controls()
        pub.subscribe(self.serialListener, 'serialListener')
        pub.subscribe(self.configListener, 'configListener')

        logging.basicConfig(format="%(filename)s: %(funcName)s() - %(message)s", level=logging.INFO)

        # TODO: is this OK?
        self.configParameters = 0

    def serialListener(self, message, fname=None):
        self.mySer = message

    def configListener(self, message, fname=None):
        self.configParameters = message
        self.extract_parameters(self.configParameters)

    def extract_parameters(self, par):
        #logging.info('length: %s', len(par))
        for i in range(0, len(par)):
            stripPar = par[i].strip('\n')
            splitPar = stripPar.split(',')
            #print splitPar[0], splitPar[1]

            # update text control fields in --Set parameters-- box
            if (splitPar[0] == 'motor.cl.max'):
                self.txtCtrl_cl_max.SetValue(splitPar[1])
                self.oldClMax = float(splitPar[1])
            if (splitPar[0] == 'motor.cl.min'):
                self.txtCtrl_cl_min.SetValue(splitPar[1])
                self.oldClMin = float(splitPar[1])
            if (splitPar[0] == 'motor.sl.ki'):
                self.txtCtrl_sl_ki.SetValue(splitPar[1])
                self.oldSlKi = float(splitPar[1])
            if (splitPar[0] == 'motor.sl.max'):
                self.txtCtrl_sl_max.SetValue(splitPar[1])
                self.oldSlMax = float(splitPar[1])
            if (splitPar[0] == 'motor.sl.min'):
                self.txtCtrl_sl_min.SetValue(splitPar[1])
                self.oldSlMin = float(splitPar[1])
            if (splitPar[0] == 'throttle.has_switch'):
                self.txtCtrl_has_switch.SetValue(splitPar[1])
                self.oldHasSwitch = float(splitPar[1])
            if (splitPar[0] == 'power_margin'):
                self.txtCtrl_power_margin.SetValue(splitPar[1])
                self.oldPowerMargin = float(splitPar[1])
            if (splitPar[0] == 'power_factor'):
                self.txtCtrl_power_factor.SetValue(splitPar[1])
                self.oldPowerFactor = float(splitPar[1])
            if (splitPar[0] == 'led.brightness_lo'):
                self.txtCtrl_brightness_lo.SetValue(splitPar[1])
                self.oldBrightnessLo = float(splitPar[1])
            if (splitPar[0] == 'brake_temp_ok'):
                self.txtCtrl_brake_temp_ok.SetValue(splitPar[1])
                self.oldBrakeTempOk = float(splitPar[1])
            if (splitPar[0] == 'brake_temp_hi'):
                self.txtCtrl_brake_temp_hi.SetValue(splitPar[1])
                self.oldBrakeTempHi = float(splitPar[1])
            if (splitPar[0] == 'brake_max_id'):
                self.txtCtrl_brake_max_id.SetValue(splitPar[1])
                self.oldBrakeMaxId = float(splitPar[1])
            if (splitPar[0] == 'brake_test.pos_ratio'):
                self.txtCtrl_brake_pos_ratio.SetValue(splitPar[1])
                self.oldBrakePosRatio = float(splitPar[1])
            if (splitPar[0] == 'trajec.acc'):
                self.txtCtrl_trajec_acc.SetValue(splitPar[1])
                self.oldTrajecAcc = float(splitPar[1])
            if (splitPar[0] == 'trajec.ret'):
                self.txtCtrl_trajec_ret.SetValue(splitPar[1])
                self.oldTrajecRet = float(splitPar[1])
            if (splitPar[0] == 'dominant_throttle_on'):
                self.txtCtrl_dominant_throttle_on.SetValue(splitPar[1])
                self.oldDominantThrottle = float(splitPar[1])
            if (splitPar[0] == 'max_motor_temp'):
                self.txtCtrl_max_motor_temp.SetValue(splitPar[1])
                self.oldMaxMotorTemp = float(splitPar[1])
            if (splitPar[0] == 'num_motor_ch'):
                self.txtCtrl_num_motor_ch.SetValue(splitPar[1])
                self.oldNumMotorCh = float(splitPar[1])
            if (splitPar[0] == 'idle_timeout'):
                self.txtCtrl_idle_timeout.SetValue(splitPar[1])
                self.oldIdleTimeout = float(splitPar[1])
            if (splitPar[0] == 'rope_stuck_on'):
                self.txtCtrl_rope_stuck_on.SetValue(splitPar[1])
                self.oldRopeStuckOn = float(splitPar[1])
            if (splitPar[0] == 'iq_alpha'):
                self.txtCtrl_iq_alpha.SetValue(splitPar[1])
                self.oldIqAlpha = float(splitPar[1])
            if (splitPar[0] == 'speed_alpha'):
                self.txtCtrl_speed_alpha.SetValue(splitPar[1])
                self.oldSpeedAlpha = float(splitPar[1])
            if (splitPar[0] == 'undershoot'):
                self.txtCtrl_undershoot.SetValue(splitPar[1])
                self.oldUndershoot = float(splitPar[1])
            if (splitPar[0] == 'delay_start'):
                self.txtCtrl_delay_start.SetValue(splitPar[1])
                self.oldDelayStart = float(splitPar[1])

    def setup_config_params(self):

        self.param_cl_max = wx.StaticText(self, wx.ID_ANY, 'cl.max')
        self.txtCtrl_cl_max = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_cl_min = wx.StaticText(self, wx.ID_ANY, 'cl.min')
        self.txtCtrl_cl_min = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_sl_ki = wx.StaticText(self, wx.ID_ANY, 'sl.ki')
        self.txtCtrl_sl_ki = wx.TextCtrl(self, wx.ID_ANY,'0.00')

        param_sl_max = wx.StaticText(self, wx.ID_ANY, 'sl.max')
        self.txtCtrl_sl_max = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_sl_min = wx.StaticText(self, wx.ID_ANY, 'sl.min')
        self.txtCtrl_sl_min = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_has_switch = wx.StaticText(self, wx.ID_ANY, 'has_switch')
        self.txtCtrl_has_switch = wx.TextCtrl(self, wx.ID_ANY,'0')

        param_power_margin = wx.StaticText(self, wx.ID_ANY, 'power_margin')
        self.txtCtrl_power_margin = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_power_factor = wx.StaticText(self, wx.ID_ANY, 'power_factor')
        self.txtCtrl_power_factor = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_brightness_lo = wx.StaticText(self, wx.ID_ANY, 'brightness_lo')
        self.txtCtrl_brightness_lo = wx.TextCtrl(self, wx.ID_ANY,'0.00')

        param_brake_temp_ok = wx.StaticText(self, wx.ID_ANY, 'brake_temp_ok')
        self.txtCtrl_brake_temp_ok = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_brake_temp_hi = wx.StaticText(self, wx.ID_ANY, 'brake_temp_hi')
        self.txtCtrl_brake_temp_hi = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_brake_max_id = wx.StaticText(self, wx.ID_ANY, 'brake_max_id')
        self.txtCtrl_brake_max_id = wx.TextCtrl(self, wx.ID_ANY,'0.00')

        param_brake_pos_ratio = wx.StaticText(self, wx.ID_ANY, 'brake_pos_ratio')
        self.txtCtrl_brake_pos_ratio = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_trajec_acc = wx.StaticText(self, wx.ID_ANY, 'trajec.acc')
        self.txtCtrl_trajec_acc = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_trajec_ret = wx.StaticText(self, wx.ID_ANY, 'trajec.ret')
        self.txtCtrl_trajec_ret = wx.TextCtrl(self, wx.ID_ANY,'0.00')

        param_dominant_throttle_on = wx.StaticText(self, wx.ID_ANY, 'dominant_throttle_on')
        self.txtCtrl_dominant_throttle_on = wx.TextCtrl(self, wx.ID_ANY,'0')
        param_max_motor_temp = wx.StaticText(self, wx.ID_ANY, 'max_motor_temp')
        self.txtCtrl_max_motor_temp = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_num_motor_ch = wx.StaticText(self, wx.ID_ANY, 'num_motor_ch')
        self.txtCtrl_num_motor_ch = wx.TextCtrl(self, wx.ID_ANY,'0')

        param_idle_timeout = wx.StaticText(self, wx.ID_ANY, 'idle_timeout')
        self.txtCtrl_idle_timeout = wx.TextCtrl(self, wx.ID_ANY,'0')

        btnConfigure = wx.Button(self, wx.ID_ANY, ' Configure   ')
        self.Bind(wx.EVT_BUTTON, self.onConfigure, btnConfigure)
        btnSaveParam = wx.Button(self, wx.ID_ANY, ' Param Save')
        self.Bind(wx.EVT_BUTTON, self.onSaveParam, btnSaveParam)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(btnConfigure, 0, wx.LEFT, 10)
        btnSizer.Add(btnSaveParam, 0, wx.LEFT, 10)

        paramSizer1 = wx.BoxSizer(wx.VERTICAL)
        paramSizer1.Add(self.param_cl_max, 0, wx.TOP, 10)
        paramSizer1.Add(self.txtCtrl_cl_max, 0, wx.TOP, 10)
        paramSizer1.Add(param_cl_min, 0, wx.TOP, 10)
        paramSizer1.Add(self.txtCtrl_cl_min, 0, wx.TOP, 10)
        paramSizer1.Add(param_sl_ki, 0, wx.TOP, 10)
        paramSizer1.Add(self.txtCtrl_sl_ki, 0, wx.TOP, 10)

        paramSizer2 = wx.BoxSizer(wx.VERTICAL)
        paramSizer2.Add(param_sl_max, 0, wx.TOP, 10)
        paramSizer2.Add(self.txtCtrl_sl_max, 0, wx.TOP, 10)
        paramSizer2.Add(param_sl_min, 0, wx.TOP, 10)
        paramSizer2.Add(self.txtCtrl_sl_min, 0, wx.TOP, 10)
        paramSizer2.Add(param_has_switch, 0, wx.TOP, 10)
        paramSizer2.Add(self.txtCtrl_has_switch, 0, wx.TOP, 10)

        paramSizer3 = wx.BoxSizer(wx.VERTICAL)
        paramSizer3.Add(param_power_margin, 0, wx.TOP, 10)
        paramSizer3.Add(self.txtCtrl_power_margin, 0, wx.TOP, 10)
        paramSizer3.Add(param_power_factor, 0, wx.TOP, 10)
        paramSizer3.Add(self.txtCtrl_power_factor, 0, wx.TOP, 10)
        paramSizer3.Add(param_brightness_lo, 0, wx.TOP, 10)
        paramSizer3.Add(self.txtCtrl_brightness_lo, 0, wx.TOP, 10)

        paramSizer4 = wx.BoxSizer(wx.VERTICAL)
        paramSizer4.Add(param_brake_temp_ok, 0, wx.TOP, 10)
        paramSizer4.Add(self.txtCtrl_brake_temp_ok, 0, wx.TOP, 10)
        paramSizer4.Add(param_brake_temp_hi, 0, wx.TOP, 10)
        paramSizer4.Add(self.txtCtrl_brake_temp_hi, 0, wx.TOP, 10)
        paramSizer4.Add(param_brake_max_id, 0, wx.TOP, 10)
        paramSizer4.Add(self.txtCtrl_brake_max_id, 0, wx.TOP, 10)

        paramSizer5 = wx.BoxSizer(wx.VERTICAL)
        paramSizer5.Add(param_brake_pos_ratio, 0, wx.TOP, 10)
        paramSizer5.Add(self.txtCtrl_brake_pos_ratio, 0, wx.TOP, 10)
        paramSizer5.Add(param_trajec_acc, 0, wx.TOP, 10)
        paramSizer5.Add(self.txtCtrl_trajec_acc, 0, wx.TOP, 10)
        paramSizer5.Add(param_trajec_ret, 0, wx.TOP, 10)
        paramSizer5.Add(self.txtCtrl_trajec_ret, 0, wx.TOP, 10)

        paramSizer6 = wx.BoxSizer(wx.VERTICAL)
        paramSizer6.Add(param_dominant_throttle_on, 0, wx.TOP, 10)
        paramSizer6.Add(self.txtCtrl_dominant_throttle_on, 0, wx.TOP, 10)
        paramSizer6.Add(param_max_motor_temp, 0, wx.TOP, 10)
        paramSizer6.Add(self.txtCtrl_max_motor_temp, 0, wx.TOP, 10)
        paramSizer6.Add(param_num_motor_ch, 0, wx.TOP, 10)
        paramSizer6.Add(self.txtCtrl_num_motor_ch, 0, wx.TOP, 10)

        paramSizer7 = wx.BoxSizer(wx.VERTICAL)
        paramSizer7.Add(param_idle_timeout, 0, wx.TOP, 10)
        paramSizer7.Add(self.txtCtrl_idle_timeout, 0, wx.TOP, 10)

        paramTopSizer = wx.BoxSizer(wx.HORIZONTAL)
        paramTopSizer.Add(paramSizer1, 0, wx.ALL, 10)
        paramTopSizer.Add(paramSizer2, 0, wx.ALL, 10)
        paramTopSizer.Add(paramSizer3, 0, wx.ALL, 10)
        paramTopSizer.Add(paramSizer4, 0, wx.ALL, 10)
        paramTopSizer.Add(paramSizer5, 0, wx.ALL, 10)
        paramTopSizer.Add(paramSizer6, 0, wx.ALL, 10)
        paramTopSizer.Add(paramSizer7, 0, wx.ALL, 10)

        statBoxConfigParams = wx.StaticBox(self, wx.ID_ANY, '  Set paramters')
        statBoxConfigParams.SetBackgroundColour(common.GREY)
        statBoxConfigParams.SetForegroundColour(common.BLACK)
        statBoxSizer = wx.StaticBoxSizer(statBoxConfigParams, wx.VERTICAL)

        statBoxSizer.Add(paramTopSizer, 0, wx.ALL, 10)
        statBoxSizer.Add(btnSizer, 0, wx.ALL, 10)

        return statBoxSizer

    def setup_test_enahanced_measuring(self):

        param_rope_stuck_on = wx.StaticText(self, wx.ID_ANY, 'rope_stuck_on')
        self.txtCtrl_rope_stuck_on = wx.TextCtrl(self, wx.ID_ANY,'0')
        param_iq_alpha = wx.StaticText(self, wx.ID_ANY, 'iq_alpha')
        self.txtCtrl_iq_alpha = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_speed_alpha = wx.StaticText(self, wx.ID_ANY, 'speed_alpha')
        self.txtCtrl_speed_alpha = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_undershoot = wx.StaticText(self, wx.ID_ANY, 'undershoot')
        self.txtCtrl_undershoot = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_speed_lim = wx.StaticText(self, wx.ID_ANY, 'speed_lim')
        self.txtCtrl_speed_lim = wx.TextCtrl(self, wx.ID_ANY,'0.00')
        param_delay_start = wx.StaticText(self, wx.ID_ANY, 'delay_start')
        self.txtCtrl_delay_start = wx.TextCtrl(self, wx.ID_ANY,'0')

        btnConfigure = wx.Button(self, wx.ID_ANY, ' Configure   ')
        self.Bind(wx.EVT_BUTTON, self.onConfigure, btnConfigure)
        self.btnTestInject = wx.Button(self, wx.ID_ANY, ' Test Inject ')
        self.Bind(wx.EVT_BUTTON, self.onTestInject, self.btnTestInject)
        btnGetIq = wx.Button(self, wx.ID_ANY, '    Get iq          ')
        self.Bind(wx.EVT_BUTTON, self.onGetIq, btnGetIq)
        btnSaveParam = wx.Button(self, wx.ID_ANY, ' Param Save')
        self.Bind(wx.EVT_BUTTON, self.onSaveParam, btnSaveParam)

        paramSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        paramSizer1.Add(param_rope_stuck_on, 0, wx.LEFT, 10)
        paramSizer1.Add(param_iq_alpha, 0, wx.LEFT, 14)
        paramSizer1.Add(param_speed_alpha, 0, wx.LEFT, 44)
        paramSizer1.Add(param_undershoot, 0, wx.LEFT, 24)
        paramSizer1.Add(param_speed_lim, 0, wx.LEFT, 24)
        paramSizer1.Add(param_delay_start, 0, wx.LEFT, 24)

        paramSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        paramSizer2.Add(self.txtCtrl_rope_stuck_on, 0, wx.RIGHT, 10)
        paramSizer2.Add(self.txtCtrl_iq_alpha, 0, wx.LEFT, 15)
        paramSizer2.Add(self.txtCtrl_speed_alpha, 0, wx.LEFT, 15)
        paramSizer2.Add(self.txtCtrl_undershoot, 0, wx.LEFT, 15)
        paramSizer2.Add(self.txtCtrl_speed_lim, 0, wx.LEFT, 15)
        paramSizer2.Add(self.txtCtrl_delay_start, 0, wx.LEFT, 15)

        paramSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        paramSizer3.Add(btnConfigure, 0, wx.RIGHT, 10)
        paramSizer3.Add(self.btnTestInject, 0, wx.LEFT, 15)
        paramSizer3.Add(btnGetIq, 0, wx.LEFT, 15)
        paramSizer3.Add(btnSaveParam, 0, wx.LEFT, 15)

        statBoxTestEnhanced = wx.StaticBox(self, wx.ID_ANY, '  Enhanced Measuring')
        statBoxTestEnhanced.SetBackgroundColour(common.GREY)
        statBoxTestEnhanced.SetForegroundColour(common.BLACK)
        statBoxSizer = wx.StaticBoxSizer(statBoxTestEnhanced, wx.VERTICAL)

        statBoxSizer.Add(paramSizer1, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 10)
        statBoxSizer.Add(paramSizer2, 0, wx.BOTTOM|wx.LEFT, 15)
        statBoxSizer.Add(paramSizer3, 0, wx.BOTTOM|wx.LEFT, 15)

        return statBoxSizer

    def setup_test_run(self):

        self.btnTestRunUp = wx.Button(self, wx.ID_ANY, 'Up')
        self.btnTestRunDown = wx.Button(self, wx.ID_ANY, 'Down')
        btnTestStop = wx.Button(self, wx.ID_ANY, 'Stop')
        self.Bind(wx.EVT_BUTTON, self.onTestRunUp, self.btnTestRunUp)
        self.Bind(wx.EVT_BUTTON, self.onTestRunDown, self.btnTestRunDown)
        self.Bind(wx.EVT_BUTTON, self.onTestStop, btnTestStop)

        speed = wx.StaticText(self, wx.ID_ANY, 'Speed')

        txtNull  = wx.StaticText(self, wx.ID_ANY, ' ')

        self.spinCtrlSpeed = wx.SpinCtrl(self, value='0')
        self.spinCtrlSpeed.SetRange(0, common.MOTOR_SPEED)

        paramSizer1 = wx.BoxSizer(wx.VERTICAL)
        paramSizer1.Add(speed, 0, wx.LEFT, 30)
        paramSizer1.Add(self.spinCtrlSpeed, 0, wx.TOP, 10)

        paramSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        paramSizer2.Add(self.btnTestRunUp, 0, wx.TOP|wx.LEFT, 25)
        paramSizer2.Add(self.btnTestRunDown, 0, wx.TOP|wx.LEFT, 25)
        paramSizer2.Add(btnTestStop, 0, wx.TOP|wx.LEFT, 25)

        statBoxTestRun = wx.StaticBox(self, wx.ID_ANY, '  Test Run')
        statBoxTestRun.SetBackgroundColour(common.GREY)
        statBoxTestRun.SetForegroundColour(common.BLACK)
        statBoxSizer = wx.StaticBoxSizer(statBoxTestRun, wx.HORIZONTAL)

        statBoxSizer.Add(paramSizer1, 0, wx.ALL, 10)
        statBoxSizer.Add(paramSizer2, 0, wx.ALL, 10)
        statBoxSizer.Add(txtNull, 0, wx.LEFT, 1000)

        return statBoxSizer

    def setup_multi_text_control(self):
        headline = '       - ACX/TCX logging - \n'
        self.txtMultiCtrl = wx.TextCtrl(self, -1, headline, size=(790, 230), style=wx.TE_MULTILINE)
        self.txtMultiCtrl.SetInsertionPoint(0)

        return self.txtMultiCtrl

    def onConnect(self, event):
        print 'Connect'
        serial_cmd('v', self.mySer)

    def onConfigure(self, event):
        """
	        Update parameter fields. Check if there has been a change.
	        unicode mess ;-)
        """
        logging.info('')

        # ----------------------------------------------------------------------------------------------------
        # cl max
        # ----------------------------------------------------------------------------------------------------
        newClMax = float(self.txtCtrl_cl_max.GetValue())
        if (newClMax != self.oldClMax):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set motor.cl.max ' + self.txtCtrl_cl_max.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('cl.max updated' + "\n")
            self.oldClMax = newClMax

        # ----------------------------------------------------------------------------------------------------
        # cl min
        # ----------------------------------------------------------------------------------------------------
        newClMin = float(self.txtCtrl_cl_min.GetValue())
        if (newClMin != self.oldClMin):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set motor.cl.min ' + self.txtCtrl_cl_min.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('cl.min updated' + "\n")
            self.oldClMin = newClMin

        # ----------------------------------------------------------------------------------------------------
        # sl.ki
        # ----------------------------------------------------------------------------------------------------
        newSlKi = float(self.txtCtrl_sl_ki.GetValue())
        if (newSlKi != self.oldSlKi):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set motor.sl.ki ' + self.txtCtrl_sl_ki.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('sl.ki updated' + "\n")
            self.oldSlKi = newSlKi

        # ----------------------------------------------------------------------------------------------------
        # sl.max
        # ----------------------------------------------------------------------------------------------------
        newSlMax = float(self.txtCtrl_sl_max.GetValue())
        if (newSlMax != self.oldSlMax):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set motor.sl.max ' + self.txtCtrl_sl_ki.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('sl.max updated' + "\n")
            self.oldSlMax = newSlMax

        # ----------------------------------------------------------------------------------------------------
        # sl.min
        # ----------------------------------------------------------------------------------------------------
        newSlMin = float(self.txtCtrl_sl_min.GetValue())
        if (newSlMin != self.oldSlMin):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set motor.sl.min ' + self.txtCtrl_sl_ki.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('sl.min updated' + "\n")
            self.oldSlMin = newSlMin

        # ----------------------------------------------------------------------------------------------------
        # has_switch
        # ----------------------------------------------------------------------------------------------------
        newHasSwitch = int(self.txtCtrl_has_switch.GetValue())
        if (newHasSwitch != self.oldHasSwitch):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set throttle.has_switch ' + self.txtCtrl_has_switch.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('has_switch updated' + "\n")
            self.oldHasSwitch = newHasSwitch

        # ----------------------------------------------------------------------------------------------------
        # power_margin
        # ----------------------------------------------------------------------------------------------------
        newPowerMargin = float(self.txtCtrl_power_margin.GetValue())
        if (newPowerMargin != self.oldPowerMargin):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set power_margin ' + self.txtCtrl_power_margin.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('power_margin updated' + "\n")
            self.oldPowerMargin = newPowerMargin

        # ----------------------------------------------------------------------------------------------------
        # power_factor
        # ----------------------------------------------------------------------------------------------------
        newPowerFactor = float(self.txtCtrl_power_factor.GetValue())
        if (newPowerFactor != self.oldPowerFactor):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set power_factor ' + self.txtCtrl_power_factor.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('power_factor updated' + "\n")
            self.oldPowerFactor = newPowerFactor

        # ----------------------------------------------------------------------------------------------------
        # brightness_lo
        # ----------------------------------------------------------------------------------------------------
        newBrightnessLo = float(self.txtCtrl_brightness_lo.GetValue())
        if (newBrightnessLo != self.oldBrightnessLo):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set led.brightness_lo ' + self.txtCtrl_brightness_lo.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('brightness_lo updated' + "\n")
            self.oldBrightnessLo = newBrightnessLo

        # ----------------------------------------------------------------------------------------------------
        # brake_temp_ok
        # ----------------------------------------------------------------------------------------------------
        newBrakeTempOk = float(self.txtCtrl_brake_temp_ok.GetValue())
        if (newBrakeTempOk != self.oldBrakeTempOk):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set brake_temp_ok ' + self.txtCtrl_brake_temp_ok.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('brake_temp_ok updated' + "\n")
            self.oldBrakeTempOk = newBrakeTempOk

        # ----------------------------------------------------------------------------------------------------
        # brake_temp_hi
        # ----------------------------------------------------------------------------------------------------
        newBrakeTempHi = float(self.txtCtrl_brake_temp_hi.GetValue())
        if (newBrakeTempHi != self.oldBrakeTempHi):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set brake_temp_hi ' + self.txtCtrl_brake_temp_hi.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('brake_temp_hi updated' + "\n")
            self.oldBrakeTempHi = newBrakeTempHi

        # ----------------------------------------------------------------------------------------------------
        # brake_max_id
        # ----------------------------------------------------------------------------------------------------
        newBrakeMaxId = float(self.txtCtrl_brake_max_id.GetValue())
        if (newBrakeMaxId != self.oldBrakeMaxId):
            time.sleep(common.DELAY_1)
            # unicode mess ;-)
            local_cmd = 'param set brake_max_id ' + self.txtCtrl_brake_max_id.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('brake_max_id updated' + "\n")
            self.oldBrakeMaxId = newBrakeMaxId

        # ----------------------------------------------------------------------------------------------------
        # brake_pos_ratio
        # ----------------------------------------------------------------------------------------------------
        newBrakePosRatio = float(self.txtCtrl_brake_pos_ratio.GetValue())
        if (newBrakePosRatio != self.oldBrakePosRatio):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set brake_test.pos_ratio ' + self.txtCtrl_brake_pos_ratio.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('brake_pos_ratio updated' + "\n")
            self.oldBrakePosRatio = newBrakePosRatio

        # ----------------------------------------------------------------------------------------------------
        # trajec.acc
        # ----------------------------------------------------------------------------------------------------
            newTrajecAcc = float(self.txtCtrl_trajec_acc.GetValue())
        if (newTrajecAcc != self.oldTrajecAcc):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set brake_test.pos_ratio ' + self.txtCtrl_trajec_acc.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('trajec.acc updated' + "\n")
            self.oldTrajecAcc = newTrajecAcc

        # ----------------------------------------------------------------------------------------------------
        # trajec.ret
        # ----------------------------------------------------------------------------------------------------
        newTrajecRet = float(self.txtCtrl_trajec_ret.GetValue())
        if (newTrajecRet != self.oldTrajecRet):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set brake_test.pos_ratio ' + self.txtCtrl_trajec_ret.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('trajec.ret updated' + "\n")
            self.oldTrajecRet = newTrajecRet

        # ----------------------------------------------------------------------------------------------------
        # Dominant throttle
        # ----------------------------------------------------------------------------------------------------
        newDominantThrottle = int(self.txtCtrl_dominant_throttle_on.GetValue())
        if (newDominantThrottle > 1 or newDominantThrottle < 0):
            self.txtCtrl_dominant_throttle_on.SetForegroundColour((common.RED))

        else:
            if (newDominantThrottle != self.oldDominantThrottle):
                self.txtCtrl_dominant_throttle_on.SetForegroundColour((common.BLACK))
                time.sleep(common.DELAY_1)
                local_cmd = 'param set dominant_throttle_on ' + self.txtCtrl_dominant_throttle_on.GetValue().encode('ascii', 'ignore')
                serial_cmd(local_cmd, self.mySer)
                self.txtMultiCtrl.AppendText('dominant_throttle_on updated' + "\n")
                self.oldDominantThrottle = newDominantThrottle

        # ----------------------------------------------------------------------------------------------------
        # max_motor_temp
        # ----------------------------------------------------------------------------------------------------
        newMaxMotorTemp = float(self.txtCtrl_max_motor_temp.GetValue())
        if (newMaxMotorTemp != self.oldMaxMotorTemp):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set max_motor_temp ' + self.txtCtrl_max_motor_temp.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('max_motor_temp updated' + "\n")
            self.oldMaxMotorTemp = newMaxMotorTemp

        # ----------------------------------------------------------------------------------------------------
        # num_motor_ch
        # ----------------------------------------------------------------------------------------------------
            newNumMotorCh = float(self.txtCtrl_num_motor_ch.GetValue())
        if (newNumMotorCh != self.oldNumMotorCh):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set num_motor_ch ' + self.txtCtrl_num_motor_ch.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('num_motor_ch updated' + "\n")
            self.oldNumMotorCh = newNumMotorCh

        # ----------------------------------------------------------------------------------------------------
        # idle_timeout
        # ----------------------------------------------------------------------------------------------------
        newIdleTimeout = float(self.txtCtrl_idle_timeout.GetValue())
        if (newIdleTimeout != self.oldIdleTimeout):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set idle_timeout ' + self.txtCtrl_idle_timeout.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('idle_timeout updated' + "\n")
            self.oldIdleTimeout = newIdleTimeout

        # ----------------------------------------------------------------------------------------------------
        # rope_stuck_no
        # ----------------------------------------------------------------------------------------------------
        newRopeStuckOn = int(self.txtCtrl_rope_stuck_on.GetValue())
        if (newRopeStuckOn > 1 or newRopeStuckOn < 0):
                self.txtCtrl_rope_stuck_on.SetForegroundColour((common.RED))

        else:
            if (newRopeStuckOn != self.oldRopeStuckOn):
                self.txtCtrl_rope_stuck_on.SetForegroundColour((common.BLACK))
                time.sleep(common.DELAY_1)
                local_cmd = 'param set rope_stuck_on ' + self.txtCtrl_rope_stuck_on.GetValue().encode('ascii', 'ignore')
                serial_cmd(local_cmd, self.mySer)
                self.txtMultiCtrl.AppendText('rope_stuck_on updated' + "\n")
                self.oldRopeStuckOn = newRopeStuckOn

        # ----------------------------------------------------------------------------------------------------
        # iq alpha
        # ----------------------------------------------------------------------------------------------------
        newIqAlpha = float(self.txtCtrl_iq_alpha.GetValue())
        if (newIqAlpha != self.oldIqAlpha):
            time.sleep(common.DELAY_1)
            # unicode mess ;-)
            local_cmd = 'param set iq_alpha ' + self.txtCtrl_iq_alpha.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('iq_alpha updated' + "\n")
            self.oldIqAlpha = newIqAlpha

        # ----------------------------------------------------------------------------------------------------
        # speed alpha
        # ----------------------------------------------------------------------------------------------------
        newSpeedAlpha = float(self.txtCtrl_speed_alpha.GetValue())
        if (newSpeedAlpha != self.oldSpeedAlpha):
            time.sleep(common.DELAY_1)
            # unicode mess ;-)
            local_cmd = 'param set speed_alpha ' + self.txtCtrl_speed_alpha.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('speed_alpha updated' + "\n")
            self.oldSpeedAlpha = newSpeedAlpha

        # ----------------------------------------------------------------------------------------------------
        # undershoot
        # ----------------------------------------------------------------------------------------------------
        newUndershoot = float(self.txtCtrl_undershoot.GetValue())
        if (newUndershoot != self.oldUndershoot):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set undershoot ' + self.txtCtrl_undershoot.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('undershoot updated' + "\n")
            self.oldUndershoot = newUndershoot

        # ----------------------------------------------------------------------------------------------------
        # speed_lim
        # ----------------------------------------------------------------------------------------------------
        newSpeedLim = float(self.txtCtrl_speed_lim.GetValue())
        if (newSpeedLim != self.oldSpeedLim):
            time.sleep(common.DELAY_1)
            local_cmd = 'param set speed_lim ' + self.txtCtrl_speed_lim.GetValue().encode('ascii', 'ignore')
            serial_cmd(local_cmd, self.mySer)
            self.txtMultiCtrl.AppendText('speed_lim updated' + "\n")
            self.oldSpeedLim = newSpeedLim

        # ----------------------------------------------------------------------------------------------------
        # delay_start
        # ----------------------------------------------------------------------------------------------------
        newDelayStart = int(self.txtCtrl_delay_start.GetValue())
        if (newDelayStart > 80000 or newDelayStart < 0):
                self.txtCtrl_delay_start.SetForegroundColour((common.RED))

        else:
            if (newDelayStart != self.oldDelayStart):
                self.txtCtrl_delay_start.SetForegroundColour((common.BLACK))
                time.sleep(common.common.DELAY_1)
                # unicode mess ;-)
                local_cmd = 'param set delay_start ' + self.txtCtrl_delay_start.GetValue().encode('ascii', 'ignore')
                serial_cmd(local_cmd, self.mySer)
                self.txtMultiCtrl.AppendText('delay_start updated' + "\n")
                self.oldDelayStart = newDelayStart

    def lock_text_controls(self):
        self.txtCtrl_cl_max.Disable()
        self.txtCtrl_cl_min.Disable()
        self.txtCtrl_sl_ki.Disable()
        self.txtCtrl_sl_max.Disable()
        self.txtCtrl_sl_min.Disable()
        self.txtCtrl_has_switch.Disable()
        self.txtCtrl_power_margin.Disable()
        self.txtCtrl_power_factor.Disable()
        self.txtCtrl_brightness_lo.Disable()
        self.txtCtrl_brake_temp_ok.Disable()
        self.txtCtrl_brake_temp_hi.Disable()
        self.txtCtrl_brake_max_id.Disable()
        self.txtCtrl_brake_pos_ratio.Disable()
        self.txtCtrl_trajec_acc.Disable()
        self.txtCtrl_trajec_ret.Disable()
        self.txtCtrl_dominant_throttle_on.Disable()
        self.txtCtrl_max_motor_temp.Disable()
        self.txtCtrl_num_motor_ch.Disable()
        self.txtCtrl_idle_timeout.Disable()
        self.txtCtrl_rope_stuck_on.Disable()
        self.txtCtrl_iq_alpha.Disable()
        self.txtCtrl_speed_alpha.Disable()
        self.txtCtrl_undershoot.Disable()
        self.txtCtrl_speed_lim.Disable()
        self.txtCtrl_delay_start.Disable()

    def onTestInject(self, event):
        if (self.toggle == False):
            logging.info('Inject ON')
            self.txtMultiCtrl.AppendText('Inject On' + "\n")
            serial_cmd('param set ti 1', self.mySer)
            self.btnTestInject.SetBackgroundColour(common.RED)
            self.toggle = True

        else:
            logging.info('Inject OFF')
            self.txtMultiCtrl.AppendText('Inject Off' + "\n")
            serial_cmd('param set ti 0', self.mySer)
            self.btnTestInject.SetBackgroundColour(common.WHITE)
            self.toggle = False

    def onGetIq(self, event):
        logging.info('')
        try:
            self.txtMultiCtrl.AppendText('get_iq ' + "\n")
            rv = serial_read('get_iq', 64, self.mySer)
            self.txtMultiCtrl.AppendText(rv[6:21])
            self.txtMultiCtrl.AppendText(rv[22:36])
            self.txtMultiCtrl.AppendText(rv[37:59] + "\n")
        except:
            logging.info('No data received')

    def onSaveParam(self, event):
        logging.info('')
        serial_cmd('param save', self.mySer)
        self.txtMultiCtrl.AppendText('Parameter saved\n')

    def onTestRunUp(self, event):
        logging.info('')
        speedValue = self.spinCtrlSpeed.GetValue()
        self.txtMultiCtrl.AppendText('Up command: speed=' + str(speedValue) + "\n")
        self.btnTestRunDown.Enable(False)
        serial_cmd('e', self.mySer)
        time.sleep(1)
        serial_cmd('brake 0', self.mySer)
        time.sleep(1)
        serial_cmd('speed -' + str(speedValue), self.mySer)

    def onTestRunDown(self, event):
        logging.info('')
        speedValue = self.spinCtrlSpeed.GetValue()
        self.txtMultiCtrl.AppendText('Down command: speed=' + str(speedValue) + "\n")
        self.btnTestRunUp.Enable(False)
        serial_cmd('e', self.mySer)
        time.sleep(1)
        serial_cmd('brake 0', self.mySer)
        time.sleep(1)
        serial_cmd('speed ' + str(speedValue), self.mySer)

    def onTestStop(self, event):
        logging.info('')
        self.txtMultiCtrl.AppendText('Stop command ' + "\n")
        serial_cmd('speed 0', self.mySer)
        time.sleep(1)
        serial_cmd('d', self.mySer)
        time.sleep(1)
        serial_cmd('brake 1', self.mySer)
        self.btnTestRunUp.Enable(True)
        self.btnTestRunDown.Enable(True)
        self.runningUp = False
        self.runningDown = False

    def onCombo(self, event):
        print 'Selected port: '

import wx
import trace
import downloader
import calibration
import common
import prodtest
import trace
from wx.lib.pubsub import pub
from wx.lib.pubsub import setupkwargs
import datetime
import sys
import base64

# TODO: handle csv file with correct library

def print_const():
    app = wx.GetApp()


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.exitDialog =  wx.MessageDialog( self, common.MSG_QUIT, "Quit", wx.YES_NO)

        self.Centre()

        # create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # Create the tab windows
        self.tabDownLoader = downloader.DownLoaderForm(nb)
        tabCalib = calibration.CalibForm(nb)
        self.tabProdTest = prodtest.ProdTestForm(nb)
        tabTrace = trace.TraceTestForm(nb)

        # add the windows to tabs and name them
        nb.AddPage(self.tabDownLoader, "Common")
        nb.AddPage(tabCalib, "Calibrate")
        nb.AddPage(self.tabProdTest, "Prod Test")
        nb.AddPage(tabTrace, "Performance Test")

        self.setup_menu()

        # set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

    def setup_menu(self):
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        unlockMenu = wx.Menu()
        aboutMenu = wx.Menu()

        fileMenu.Append(wx.ID_OPEN, "Open", "Open")
        fileMenu.Append(wx.ID_SAVE, "Save", "Save")
        fileMenu.Append(wx.ID_EXIT, "Exit", "Close")
        unlockMenu.Append(101, "&Lock\tCTRL+L", "Lock")
        unlockMenu.Append(102, "&UnLock\tCTRL+U", "UnLock")
        aboutMenu.Append(103, "&About\tCTRL+A", "Open")

        #disable 'Save' menu
        fileMenu.Enable(wx.ID_SAVE, False)

        menuBar.Append(fileMenu, "&File")
        menuBar.Append(unlockMenu, "&Enable Params")
        menuBar.Append(aboutMenu, "&About")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.onOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.onSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onLock, id=101)
        self.Bind(wx.EVT_MENU, self.onUnLock, id=102)
        self.Bind(wx.EVT_MENU, self.onAbout, id=103)

    def onOpen(self, event):
        print_const()
        openFileDialog = wx.FileDialog(self, "Open", "", "", "ACX/TCX config files (*.txt)|*.txt", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        openFileDialog.GetPath()
        #print openFileDialog.GetPath()

        with open(openFileDialog.GetPath()) as f:
            lines = f.readlines()

        # pass configuration parameters to downloader and prodtest
        pub.sendMessage('TOPIC_CONFIG_LISTENER', message=lines, fname=openFileDialog.GetFilename())
        self.tabDownLoader.print_parameters()
        openFileDialog.Destroy()

    def onSave(self, event):
        saveFileDialog = wx.FileDialog(self, "Save As", "", "", "ACX/TCX config files (*.txt)|*.txt", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        saveFileDialog.ShowModal()
        saveFileDialog.GetPath()

        print self.tabProdTest.configParameters

        saveFileDialog.Destroy()

    def onLock(self, event):
        self.tabProdTest.lock_text_controls()

    def onQuit(self, event):
        rv = self.exitDialog.ShowModal()
        if rv == wx.ID_YES:
            self.Close(True)

    def onUnLock(self, event):
        dialog = wx.TextEntryDialog(self, message="Enter Password", caption="Password query", style=wx.OK|wx.CANCEL|wx.TE_PASSWORD)
        dialog.SetValue("")
        result = dialog.ShowModal()

        # check password if OK button was pressed
        if result == wx.ID_OK:
            passwd = dialog.GetValue()

            if (passwd == 'Woodpecker'):
                self.tabProdTest.unLock_text_controls()

    def onAbout(self, event):
        licence = """

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THIS SOFTWARE.
        """
        description = """Version 1.16.

Requires software/hardware at least versions -
Ascender:
    Unjo 500:01 00153 C
    220:02 00150 A
    220:02 00111 C

Remote:
    Unjo 500:01 00155 PB2
    220:02 00121 D
    """

        info = wx.AboutDialogInfo()
        info.SetName("Production Test Tool for ActSafe's ACX/TCX")
        info.SetDescription(description)
        info.SetCopyright('(C) 2017 - Unjo AB')
        info.SetWebSite('http://www.unjo.com')
        info.SetLicence(licence)
        wx.AboutBox(info)



class mainApp(wx.App):
   def OnInit(self):
       self.frame = MainFrame(None, -1, title=common.HEADLINE, style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX, size=common.WINDOW_SIZE)
       self.frame.Show()
       return True

def check_licens():
    print('Check current licens')
    now = datetime.datetime.now().strftime("%Y-%m-%d   %H:%M")
    print('Today is:', now)

    try:
        licFile = open("licensfile.lic", "r")
        licDate = licFile.readline()
        decodecDate = base64.b64decode(licDate.decode())

        strippedDate = decodecDate.strip('\n')
        splitDate = strippedDate.split('-')
        trigger = 0

        if (int(splitDate[0]) <= int(now[0:4])):  # year
            if (int(splitDate[1]) < int(now[6:7])): # month
                trigger = 1
            else:
                if (int(splitDate[2]) < int(now[8:10])): # day
                    trigger = 1

        if (trigger == 0):
            print 'License OK. Will expire:', strippedDate
        else:
            print 'License has expiered:', strippedDate
            sys.exit()

    except IOError:
        print 'No license file! Application is terminated.'
        sys.exit()




#=====================================================================================================================================
#  Main
#=====================================================================================================================================
if __name__ == '__main__':
    check_licens()

    app = mainApp()
    app.MainLoop()

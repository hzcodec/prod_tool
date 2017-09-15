import wx
import trace
import downloader
import common


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

        # add the windows to tabs and name them
        nb.AddPage(self.tabDownLoader, "Common")

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

    def onOpen(selfself, event):
        pass

    def onSave(self, event):
        pass

    def onLock(self, event):
        pass

    def onQuit(self, event):
        rv = self.exitDialog.ShowModal()

    def onUnLock(self, event):
        pass

    def onAbout(self, event):
        pass



class mainApp(wx.App):
   def OnInit(self):
       self.frame = MainFrame(None, -1, title=common.HEADLINE, style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX, size=common.WINDOW_SIZE)
       self.frame.Show()
       return True

if __name__ == '__main__':
    app = mainApp()
    app.MainLoop()

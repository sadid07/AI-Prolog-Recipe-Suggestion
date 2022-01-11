import wx
from main_frame import MainFrame

if __name__ == "__main__":
    #Initialize APP, chat window and display it
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
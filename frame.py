# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class botframe
###########################################################################

class botframe ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"FoodBot", pos = wx.DefaultPosition, size = wx.Size( 383,543 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText1 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Chat History:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )

        bSizer2.Add( self.m_staticText1, 0, wx.ALL, 5 )

        self.chat_window = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
        bSizer2.Add( self.chat_window, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        listbox_optionsChoices = []
        self.listbox_options = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, listbox_optionsChoices, 0 )
        self.listbox_options.SetSelection( 0 )
        bSizer3.Add( self.listbox_options, 1, wx.ALL, 5 )

        self.edit_number = wx.SpinCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 9999, 500 )
        self.edit_number.Hide()

        bSizer3.Add( self.edit_number, 1, wx.ALL, 5 )

        self.btn_send = wx.Button( self.m_panel1, wx.ID_ANY, u"Send >>>", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.btn_send, 0, wx.ALL|wx.EXPAND, 5 )


        bSizer2.Add( bSizer3, 0, wx.EXPAND, 5 )


        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )
        bSizer1.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 0 )


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.btn_send.Bind( wx.EVT_BUTTON, self.btn_sendOnButtonClick )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def btn_sendOnButtonClick( self, event ):
        event.Skip()



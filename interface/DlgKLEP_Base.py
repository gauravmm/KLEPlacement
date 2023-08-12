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
## Class DlgKLEP_Base
###########################################################################


class DlgKLEP_Base(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="KLE Placement",
            pos=wx.DefaultPosition,
            size=wx.Size(465, 367),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizerMain = wx.BoxSizer(wx.VERTICAL)

        bSizerMain.SetMinSize(wx.Size(-1, 600))
        self.m_staticText2 = wx.StaticText(
            self,
            wx.ID_ANY,
            "Your Keyboard-Layout-Editor JSON:",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticText2.Wrap(-1)

        bSizerMain.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.txtKLEJson = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_MULTILINE,
        )
        self.txtKLEJson.SetMinSize(wx.Size(-1, 300))

        bSizerMain.Add(self.txtKLEJson, 1, wx.ALL | wx.EXPAND, 5)

        self.m_staticline2 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL
        )
        bSizerMain.Add(self.m_staticline2, 0, wx.EXPAND | wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(
            self, wx.ID_ANY, "Reference Prefix", wx.DefaultPosition, wx.DefaultSize, 0
        )
        self.m_staticText4.Wrap(-1)

        self.m_staticText4.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                True,
                wx.EmptyString,
            )
        )
        self.m_staticText4.SetForegroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        )
        self.m_staticText4.SetToolTip(
            "Specify which components to lay out automatically using their prefix."
        )

        bSizerMain.Add(self.m_staticText4, 0, wx.ALL, 5)

        choicePrefixChoices = []
        self.choicePrefix = wx.Choice(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choicePrefixChoices, 0
        )
        self.choicePrefix.SetSelection(0)
        bSizerMain.Add(self.choicePrefix, 0, wx.ALL | wx.EXPAND, 5)

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1Apply = wx.Button(self, wx.ID_APPLY)
        m_sdbSizer1.AddButton(self.m_sdbSizer1Apply)
        self.m_sdbSizer1Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer1.AddButton(self.m_sdbSizer1Cancel)
        m_sdbSizer1.Realize()

        bSizerMain.Add(m_sdbSizer1, 0, wx.EXPAND, 5)

        self.SetSizer(bSizerMain)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass

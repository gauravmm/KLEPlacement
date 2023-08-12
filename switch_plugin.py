import logging
import os
import pprint
import sys
import time
import traceback
from pathlib import Path

import pcbnew
import wx

logger = logging.getLogger("switcher")
logger.setLevel(logging.DEBUG)


class ItemSwitcherPlugin(pcbnew.ActionPlugin):
    def __init__(self):
        super().__init__()
        self.version = "0.0.1"

    def defaults(self):
        self.name = "Switch Positions"
        self.category = "Layout"
        self.description = (
            "Switch the positions of two groups or footprints. Select two and run."
        )
        self.icon_file_name = str(Path(__file__).parent / "switch-icon.png")
        self.show_toolbar_button = True

    def Run(self):
        # grab PCB editor frame
        wx_frame = wx.FindWindowByName("PcbFrame")
        board = pcbnew.GetBoard()

        for lH in list(logger.handlers):
            logger.removeHandler(lH)
        logger.addHandler(
            logging.FileHandler(
                filename=board.GetFileName() + ".switcher.log", mode="w"
            )
        )

        # set up logger
        logger.info(
            f"Plugin v{self.version} running on KiCad {pcbnew.GetBuildVersion()} and Python {sys.version} on {sys.platform}."
        )

        RunActual(wx_frame, board)


def RunActual(wx_frame: wx.Window, board: pcbnew.BOARD):
    selected_groups = [x for x in board.Groups() if x.IsSelected()]
    if len(selected_groups) > 0:
        if len(selected_groups) == 2:
            switch(*selected_groups)
        else:
            logger.error("Select exactly two groups to switch")
            logger.info(f"Selected groups: {selected_groups}")
            wx.MessageBox(
                f"Select exactly two groups to switch ({len(selected_groups)} selected)",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )

        return

    selected_footprints = [x for x in board.GetFootprints() if x.IsSelected()]
    if len(selected_footprints) > 0:
        if len(selected_footprints) == 2:
            switch(*selected_footprints)
        else:
            logger.error("Select exactly two footprints to switch")
            logger.info(f"Selected footprints: {selected_footprints}")
            wx.MessageBox(
                f"Select exactly two footprints to switch ({len(selected_footprints)} selected)",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )

        return

    logger.error("Select two groups or footprints to switch")
    wx.MessageBox(
        f"Select two groups or footprints to switch.", "Error", wx.OK | wx.ICON_ERROR
    )


def switch(item1: pcbnew.EDA_ITEM, item2: pcbnew.EDA_ITEM):
    pos1 = item1.GetPosition()
    rot1 = item1.GetOrientation()
    item1.SetPosition(item2.GetPosition())
    item1.SetOrientation(item2.GetOrientation())
    item2.SetPosition(pos1)
    item2.SetOrientation(rot1)

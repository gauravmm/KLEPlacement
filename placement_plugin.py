import logging
import os
import pprint
import string
import sys
import time
import traceback
from pathlib import Path
from .interface.DlgKLEP import DlgKLEP
from kle-py.damsenviet.kle import Keyboard


import pcbnew
import wx


logger = logging.getLogger("hierpcb")
logger.setLevel(logging.DEBUG)


class KLEPlacementPlugin(pcbnew.ActionPlugin):
    def __init__(self):
        super().__init__()
        self.version = "0.0.1"

    def defaults(self):
        self.name = "KLE Placement"
        self.category = "Layout"
        self.description = "Place footprints according to a KLE layout. Paste in your unmodified KLE plugin and hit the run button!"
        self.icon_file_name = str(Path(__file__).parent / "place_icon.png")
        self.show_toolbar_button = True

    def Run(self):
        # grab PCB editor frame
        wx_frame = wx.FindWindowByName("PcbFrame")
        board = pcbnew.GetBoard()

        for lH in list(logger.handlers):
            logger.removeHandler(lH)
        logger.addHandler(
            logging.FileHandler(
                filename=board.GetFileName() + ".kleplacement.log", mode="w"
            )
        )

        # set up logger
        logger.info(
            f"Plugin v{self.version} running on KiCad {pcbnew.GetBuildVersion()} and Python {sys.version} on {sys.platform}."
        )

        RunActual(wx_frame, board)


def RunActual(wx_frame: wx.Window, board: pcbnew.BOARD):
    def prefixof(x: pcbnew.FOOTPRINT) -> str:
        return x.GetReference().rstrip(string.digits)

    options = sorted(set(prefixof(x) for x in board.GetFootprints()))
    dlg = DlgKLEP(options)
    if dlg.ShowModal() == wx.ID_OK:
        logger.info("OK")
        prefix: str = options[dlg.choicePrefix.GetSelection()]
        items = [x for x in board.GetFootprints() if prefixof(x) == prefix]
        logger.info(f"Loaded {len(items)} items using prefix `{prefix}`.")

        kle_text = dlg.txtKLEJson.GetValue()
        logger.debug(f"KLE text: {kle_text}")

        # Parse the KLE text:

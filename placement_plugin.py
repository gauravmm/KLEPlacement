import json
import logging
import os
import pprint
import string
import sys
import time
import traceback
from pathlib import Path
from .interface.DlgKLEP import DlgKLEP
from damsenviet.kle import Keyboard

import hjson
import pcbnew
import wx


logger = logging.getLogger("kleplacement")
logger.setLevel(logging.DEBUG)

key_U = 19.05  # The size of 1U in mm


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
    dlg = DlgKLEP(wx_frame, options)
    if dlg.ShowModal() == wx.ID_OK:
        logger.info("OK")
        prefix: str = options[dlg.choicePrefix.GetSelection()]
        items = [x for x in board.GetFootprints() if prefixof(x) == prefix]
        logger.info(f"Loaded {len(items)} items using prefix `{prefix}`.")

        kle_text = dlg.txtKLEJson.GetValue()
        logger.debug(f"KLE text: {kle_text}")

        # Parse the KLE text:
        kbrd = Keyboard.from_json(hjson.loads(f"[{kle_text}]"))
        # Sort the keys by column-major order:
        template_keys = sorted(kbrd.keys, key=lambda x: x.x * 1000 + x.y)
        items = sorted(
            items, key=lambda x: x.GetPosition().x * 1000 + x.GetPosition().y
        )

        # Check that the number of keys matches the number of footprints:
        if len(template_keys) != len(items):
            logger.error(
                f"Number of keys ({len(template_keys)}) does not match number of footprints ({len(items)})."
            )
            if (
                wx.MessageBox(
                    f"Number of keys ({len(template_keys)}) does not match number of footprints ({len(items)}). Continue anyway?",
                    "Error",
                    wx.YES_NO | wx.CANCEL | wx.ICON_ERROR,
                )
                != wx.YES
            ):
                return

        # Find the top-left position of all keys:
        min_x = min(item.GetX() for item in items)
        min_y = min(item.GetY() for item in items)

        for key, item in zip(template_keys, items):
            x = int(pcbnew.FromMM(key.x * key_U))
            y = int(pcbnew.FromMM(key.y * key_U))
            item.SetPosition(pcbnew.VECTOR2I(x + min_x, y + min_y))
            item.SetOrientationDegrees(key.rotation_angle)

            label = key.labels[0].text

            logger.info(
                f"Placed {item.GetReference()} at ({x}, {y}; {key.rotation_angle}) for key {label}."
            )
            logger.debug(key.__dict__)

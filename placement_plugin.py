from collections import defaultdict
import json
import logging
import os
import pprint
import string
import sys
import time
import traceback
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import pcbnew
import wx

from .simplekleparser import KeySpec

from .cfgman import ConfigMan
from .interface.DlgKLEP import DlgKLEP
from .simplekleparser import parse_kle

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
        self.icon_file_name = str(Path(__file__).parent / "keyboard.png")
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

        with ConfigMan(Path(board.GetFileName() + ".klep.json")) as cfg:
            RunActual(cfg, wx_frame, board)


def RunActual(cfg: ConfigMan, wx_frame: wx.Window, board: pcbnew.BOARD):
    def prefixof(x: pcbnew.FOOTPRINT) -> str:
        return x.GetReference().rstrip(string.digits)

    options = sorted(set(prefixof(x) for x in board.GetFootprints()))
    dlg = DlgKLEP(cfg, wx_frame, options)
    if dlg.ShowModal() == wx.ID_OK:
        logger.info("OK")
        prefix: str = options[dlg.choicePrefix.GetSelection()]
        items = [x for x in board.GetFootprints() if prefixof(x) == prefix]
        logger.info(f"Loaded {len(items)} items using prefix `{prefix}`.")

        kle_text = dlg.txtKLEJson.GetValue()
        logger.debug(f"KLE text: {kle_text}")

        # Parse the KLE text:
        kbrd: List[KeySpec] = parse_kle(kle_text)
        # Sort the keys by column-major order:
        kbrd = sorted(kbrd, key=lambda x: x.x * 1000 + x.y)
        items = sorted(
            items, key=lambda x: x.GetPosition().x * 1000 + x.GetPosition().y
        )

        # Check that the number of keys matches the number of footprints:
        if len(kbrd) != len(items):
            logger.error(
                f"Number of keys ({len(kbrd)}) does not match number of footprints ({len(items)})."
            )
            if (
                wx.MessageBox(
                    f"Number of keys ({len(kbrd)}) does not match number of footprints ({len(items)}). Continue anyway?",
                    "Error",
                    wx.YES_NO | wx.CANCEL | wx.ICON_ERROR,
                )
                != wx.YES
            ):
                return

        # Find the top-left position of all keys:
        min_x = min(item.GetX() for item in items)
        min_y = min(item.GetY() for item in items)
        # Find the same limit in virtual key-space:
        # We need this to offer the don't-move-correctly-placed-footprints option.
        min_key_x = min(key.x for key in kbrd)
        min_key_y = min(key.y for key in kbrd)

        def get_key_coords(key: KeySpec) -> (int, int):
            x = min_x + int(pcbnew.FromMM((key.x - min_key_x) * key_U))
            y = min_y + int(pcbnew.FromMM((key.y - min_key_y) * key_U))
            return x, y

        matched = correct_keys(items, kbrd, get_key_coords)

        for key, item in matched.items():
            x, y = get_key_coords(key)
            item.SetPosition(pcbnew.VECTOR2I(x, y))
            item.SetOrientationDegrees(key.r + 180)

            logger.info(
                f"Placed {item.GetReference()} at ({x}, {y}; {key.r}) for key `{key.label}`."
            )


def correct_keys(
    items: List[pcbnew.FOOTPRINT],
    keys: List[KeySpec],
    get_key_coords: Callable[[KeySpec], Tuple[int, int]],
) -> Dict[KeySpec, pcbnew.FOOTPRINT]:
    # Find keys and footprints that are already placed correctly:
    # We can't rely on sorting by position because the user might have moved
    # some of them.
    BIN_SIZE = int(1e4)
    bins: Dict[Tuple[int, int, int], List[pcbnew.FOOTPRINT]] = defaultdict(list)
    for item in items:
        # We need to round the position to the nearest BIN_SIZE because
        # of imprecision in the floating-point math we do.
        binkey = (
            int(item.GetPosition().x // BIN_SIZE),
            int(item.GetPosition().y // BIN_SIZE),
        )
        bins[binkey].append(item)
        logger.debug(f"Footprint {item.GetReference()} in {binkey}")

    # Now we can check for overlaps:
    rv: Dict[KeySpec, pcbnew.FOOTPRINT] = {}
    unmatched_keys = []
    for key in keys:
        x, y = get_key_coords(key)
        binkey = (int(x // BIN_SIZE), int(y // BIN_SIZE))
        candidates = bins[binkey]

        if len(candidates) > 0:
            # We found a candidate!
            item = candidates.pop()
            rv[key] = item
            logger.info(
                f"Matched {item.GetReference()} at ({x}, {y}; {key.r}) for key `{key.label}`."
            )
        else:
            logger.debug(f"Cannot find key at {binkey}")
            # No candidate found.
            unmatched_keys.append(key)

    # Match up the remaining keys and footprints. Keep the original key order,
    # but sort the footprints by position.
    # Begin by flattening the remaining footprints into a list:
    remaining_items = sorted(
        (item for sublist in bins.values() for item in sublist),
        key=lambda x: x.GetPosition().y * 1e6 + x.GetPosition().x,
    )
    return dict(zip(unmatched_keys, remaining_items))

    # for key, item in zip(unmatched_keys, remaining_items):
    #     rv[key] = item
    # return rv

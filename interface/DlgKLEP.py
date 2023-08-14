import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from ..cfgman import ConfigMan

import wx

from .DlgKLEP_Base import DlgKLEP_Base

logger = logging.getLogger("hierpcb")

DEFAULT_CONFIG = r"""[{x:0.5},"Esc",{x:1.25},"F1","F2","F3","F4","F5","F6"],
[{y:0.5,x:0.5,a:7,h:2},"",{x:0.25,a:4},"~\n`","!\n1","@\n2","#\n3","$\n4","%\n5","^\n6"],
[{x:1.75,w:1.5},"Tab","Q","W","E","R","T"],
[{x:0.5,a:7,h:1.5},"",{x:0.25,a:4,w:1.75},"CapsLock","A","S","D","F","G"],
[{x:1.75,w:2.25},"Shift","Z","X","C","V","B"],
[{y:-0.5,x:0.5,a:7,h:1.5},""],
[{y:-0.5,x:1.75,a:4,w:1.25},"Ctrl",{w:1.25},"Win",{w:1.25},"LAlt",{a:7,w:1.25},""],
[{r:30,rx:8.5,ry:4,y:0.5,x:1.5,a:4},"LAlt","Super"],
[{x:0.5,h:2},"Space",{h:2},"Bksp",{a:7},""],
[{x:2.5},""]
"""

DEFAULT_PREFIX = "SW"


class DlgKLEP(DlgKLEP_Base):
    def __init__(self, cfg: ConfigMan, parent: wx.Window, prefixes: List[str]):
        # Set up the user interface from the designer.
        super().__init__(parent)
        # Populate the dialog with data:
        self.prefixes = prefixes
        self.cfg = cfg
        # Populate the list of available sub-PCBs:
        self.choicePrefix.SetItems(prefixes)

        self.txtKLEJson.SetValue(cfg.get("interface", "kle", default=DEFAULT_CONFIG))

        try:
            idx = prefixes.index(cfg.get("interface", "prefix", default=DEFAULT_PREFIX))
        except ValueError:
            idx = 0

        self.choicePrefix.SetSelection(idx)

    def apply(self, event):
        # Write that back to the config:
        logger.info("Apply")
        val = self.txtKLEJson.GetValue()
        self.cfg.set("interface", "kle", value=val)
        logger.info("Config written:\n{val}")

        try:
            prx = self.prefixes[self.choicePrefix.GetSelection()]
            self.cfg.set("interface", "prefix", value=prx)
            logger.info("Prefix written: {prx}")
        except IndexError:
            logger.info("Prefix not written: no prefix!")

        self.EndModal(wx.ID_OK)

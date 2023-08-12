import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import wx

from .DlgKLEP_Base import DlgKLEP_Base

logger = logging.getLogger("hierpcb")


class DlgHPCBRun(DlgKLEP_Base):
    def __init__(self, parent: wx.Window, prefixes: List[str]):
        # Set up the user interface from the designer.
        super().__init__(parent)
        # Populate the dialog with data:
        self.prefixes = prefixes
        # Populate the list of available sub-PCBs:
        self.choicePrefix.SetItems(prefixes)

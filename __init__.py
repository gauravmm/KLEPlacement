from pathlib import Path
import sys

with Path("C:\\Users\\User\\Desktop\\kleplace.log").open("w") as f:
    f.write("Hello World\n")
    sys.path.append(str(Path(__file__).absolute().parent / "lib"))
    try:
        from .switch_plugin import ItemSwitcherPlugin
        from .placement_plugin import KLEPlacementPlugin

        ItemSwitcherPlugin().register()
        KLEPlacementPlugin().register()
    except Exception as e:
        f.write(str(e))
    f.write("Bye")

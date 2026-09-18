from pathlib import Path
import sys

with Path("kleplace.log").open("w") as f:
    sys.path.append(str(Path(__file__).absolute().parent / "lib"))
    try:
        from .placement_plugin import KLEPlacementPlugin

        KLEPlacementPlugin().register()
    except Exception as e:
        f.write(str(e))
    f.write("Bye")

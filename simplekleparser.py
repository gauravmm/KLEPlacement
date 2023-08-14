# This is a very simple and dumb parser for KLE files. It exists because
# [damsenviet.kle](https://github.com/DamSenViet/kle-py/) doesn't handle
# rotations and I don't want to figure out how to make it do that.

from dataclasses import dataclass
import json
from math import radians, sin, cos
from pprint import pprint
from typing import List


@dataclass(frozen=True)
class KeySpec:
    label: str
    # Position and size in key units
    x: float
    y: float
    w: float
    h: float
    # Angle in degrees:
    r: float = 0.0

    def __str__(self) -> str:
        return f"{self.label or '<?>'}(<{self.x}, {self.y}>, [{self.w}, {self.h}], {self.rotation_angle} deg)"


@dataclass
class ParserState:
    x: float = 0.0
    y: float = 0.0
    w: float = 1.0
    h: float = 1.0
    r: float = 0.0
    rx: float = 0.0
    ry: float = 0.0


def parse_kle(inpstr: str) -> List[KeySpec]:
    # Precondition the input string so we don't need to use the hjson parser:
    # Replace the keys with quoted ones:
    for key in ["rx", "ry", "x", "y", "w", "h", "r", "a"]:
        inpstr = inpstr.replace(f"{key}:", f'"{key}":')
    # Wrap it in a list:
    loaded = json.loads("[" + inpstr + "]")

    # pprint(loaded)
    state = ParserState()
    rv: List[KeySpec] = []
    for row in loaded:
        for col in row:
            # Move to next position:
            if isinstance(col, dict):
                state.w = col.get("w", state.w)
                state.h = col.get("h", state.h)

                rx = col.get("rx", None)
                if rx:
                    state.rx = rx
                    state.x = rx

                ry = col.get("ry", None)
                if ry:
                    state.ry = ry
                    state.y = ry

                state.x += col.get("x", 0)
                state.y += col.get("y", 0)
                state.r = col.get("r", state.r)
                continue
            # Otherwise, it's a key:
            if isinstance(col, str):
                # Nominal x and y:
                kx = state.x + state.w / 2 - state.rx
                ky = state.y + state.h / 2 - state.ry
                r = radians(state.r)

                # Position after rotation:
                x = kx * cos(r) - ky * sin(r) + state.rx
                y = kx * sin(r) + ky * cos(r) + state.ry

                key = KeySpec(label=col, x=x, y=y, w=state.w, h=state.h, r=-state.r)
                # Move the pointer:
                state.x += state.w

                # Reset some states:
                state.w = state.h = 1.0

                rv.append(key)

            else:
                raise ValueError(f"Unexpected value: {col}")
        # Reset the row:
        state.y += state.h
        state.x = state.rx

    return rv


if __name__ == "__main__":
    inp = r"""[{x:0.5},"Esc",{x:1.25},"F1","F2","F3","F4","F5","F6"],
[{y:0.5,x:0.5,a:7,h:2},"",{x:0.25,a:4},"~\n`","!\n1","@\n2","#\n3","$\n4","%\n5","^\n6"],
[{x:1.75,w:1.5},"Tab","Q","W","E","R","T"],
[{x:0.5,a:7,h:1.5},"",{x:0.25,a:4,w:1.75},"CapsLock","A","S","D","F","G"],
[{x:1.75,w:2.25},"Shift","Z","X","C","V","B"],
[{y:-0.5,x:0.5,a:7,h:1.5},""],
[{y:-0.5,x:1.75,a:4,w:1.25},"Ctrl",{w:1.25},"Win",{w:1.25},"LAlt",{a:7,w:1.25},""],
[{r:30,rx:8.5,ry:4,y:0.5,x:1.5,a:4},"LAlt","Super"],
[{x:0.5,h:2},"Space",{h:2},"Bksp",{a:7},""],
[{x:2.5},""]"""

    pprint(parse(inp))

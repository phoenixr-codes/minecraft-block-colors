from itertools import *
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from PIL import Image

Color = tuple[int, int, int]

def avg_color(im: Image.Image) -> Color:
    colors = im.getcolors(maxcolors=2**16)
    assert colors is not None
    colors_array = np.array(list(chain.from_iterable(map(lambda x: (x[1] for _ in range(x[0])), colors))))
    avg = np.round(sum(colors_array) / len(colors_array)).astype(int)
    return avg


def rgb_as_hex(rgb: Color) -> str:
    return f"{rgb[0]:0>2X}{rgb[1]:0>2X}{rgb[2]:0>2X}"


def main():
    root = Path(tempfile.gettempdir()) / "bedrock-samples"
    output = Path("colors.txt")

    if root.exists():
        subprocess.run([
            "git",
            "-C",
            str(root),
            "pull",
        ])
    else:
        subprocess.run([
            "git",
            "clone",
            "-d",
            "1",
            "https://github.com/Mojang/bedrock-samples.git",
            str(root),
        ])

    output.unlink(missing_ok=True)
    with output.open("a") as f:
        blocks = root / "resource_pack" / "textures" / "blocks"
        for file in blocks.iterdir():
            if not file.is_file() or file.suffix != ".png":
                continue
            im = Image.open(file).convert("RGBA")
            avg = rgb_as_hex(avg_color(im))
            file_name = file.name
            
            f.write(f"#{avg} {file_name}\n")

if __name__ == "__main__":
    main()

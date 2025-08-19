from itertools import *
import json
from pathlib import Path
import fnmatch
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
            "--depth",
            "1",
            "https://github.com/Mojang/bedrock-samples.git",
            str(root),
        ])

    output.unlink(missing_ok=True)
    blacklist = list(filter(lambda line: not line.startswith("#"), Path("blacklist.txt").read_text().splitlines()))
    with output.open("a") as out_file:
        blocks = root / "resource_pack" / "textures" / "blocks"

        with (root / "resource_pack" / "blocks.json").open("r") as f:
            texture_map = json.load(f)

        for block, data in texture_map.items():
            if block == "format_version":
              # not a block
              continue
            continue_outer = False
            for pattern in blacklist:
                if fnmatch.fnmatch(block, pattern):
                    # block in blacklist
                    continue_outer = True
            if continue_outer:
                continue
            texture = data.get("textures")
            if texture is None:
                # skip textureless
                continue
            if isinstance(texture, dict):
                # skip blocks with multiple textures
                continue
            file = (blocks / texture).with_suffix(".png")
            if not file.is_file() or file.suffix != ".png":
                continue
            im = Image.open(file)
            if im.has_transparency_data:
                # skip blocks with transparency
                continue
            if im.width != im.height:
                # skip non-square textures
                continue
            im = im.convert("RGBA")
            avg = rgb_as_hex(avg_color(im))
            file_name = file.name
            
            out_file.write(f"#{avg} {block}\n")


if __name__ == "__main__":
    main()

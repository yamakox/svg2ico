from pathlib import Path
from PIL import Image
import cairosvg
import io
import re

PRESET_ICO_SIZES = dict(
    default=[256, 128, 64, 48, 32, 24, 16], 
    favicon=[48, 32, 16], 
)

# MARK: public functions

def convert(preset: str, input: str, output: str|None=None) -> str:
    '''
    Convert a SVG file to an ICO file.

    Args:
        preset (str): The preset name of icon sizes defined by PRESET_ICO_SIZES.
        input (str): The path to the SVG file to convert. You can also pass the path of the other image format file.
        output (str|None): The path to the output ICO file. If not provided, the input file name will be used.
    
    Returns:
        The path to the output ICO file.
    '''
    if preset not in PRESET_ICO_SIZES:
        raise Exception(f'Invalid icon preset: {preset}')
    
    input_path = Path(input)
    output_path = Path(output) if output else input_path.with_suffix('.ico')
    
    if input_path.suffix.lower() == '.svg':
        png_data = cairosvg.svg2png(bytestring=_read_svg(input_path))
        image = Image.open(io.BytesIO(png_data))
    else:
        image = Image.open(input_path)
    
    _make_ico(PRESET_ICO_SIZES[preset], image, output_path)
    return str(output_path)


# MARK: private functions

def _make_ico(icon_sizes: list[int], orig_image: Image, output_path: Path):
    w, h = orig_image.size
    if w == h:
        image = orig_image
    elif w > h:
        image = Image.new('RGBA', size=(w, w), color=(0, 0, 0, 0))
        image.paste(orig_image, (0, (w - h)>>1))
    else:
        image = Image.new('RGBA', size=(h, h), color=(0, 0, 0, 0))
        image.paste(orig_image, ((h - w)>>1, 0))
    images = []
    for size in icon_sizes:
        images.append(image.resize((size, size), Image.Resampling.LANCZOS))
    images[0].save(
        output_path,
        format='ICO',
        append_images=images[1:],
    )

def _read_svg(input_path: Path) -> bytes:
    with open(input_path, 'r') as f:
        svg_str = f.read()
    # "light-dark" style attribute exported by draw.io causes 
    #       the following error at cairosvg:
    # invalid literal for int() with base 16: 'ig'
    mod_str = re.sub(r' style="[^"]*light-dark[^"]*"', '', svg_str)
    return mod_str.encode('utf-8')

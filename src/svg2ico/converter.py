from pathlib import Path
from PIL import Image
import cairosvg
import io

ICO_SIZES = [256, 128, 64, 48, 32, 24, 16]

# MARK: public functions

def convert(input: str, output: str|None=None) -> str:
    '''
    Convert a SVG file to an ICO file.

    Args:
        input (str): The path to the SVG file to convert. You can also pass the path of the other image format file.
        output (str|None): The path to the output ICO file. If not provided, the input file name will be used.
    
    Returns:
        The path to the output ICO file.
    '''
    input_path = Path(input)
    output_path = Path(output) if output else input_path.with_suffix('.ico')
    if input_path.suffix.lower() == '.svg':
        png_data = cairosvg.svg2png(url=input_path.as_posix())
        image = Image.open(io.BytesIO(png_data))
    else:
        image = Image.open(input_path)
    _make_ico(image, output_path)

    return str(output_path)


# MARK: private functions

def _make_ico(image: Image, output_path: Path):
    images = []
    for size in ICO_SIZES:
        images.append(image.resize((size, size), Image.Resampling.LANCZOS))
    images[0].save(
        output_path,
        format='ICO',
        append_images=images[1:],
    )

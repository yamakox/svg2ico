import click
from .converter import PRESET_ICO_SIZES

PRESETS = list(PRESET_ICO_SIZES.keys())

@click.command(help='''Convert a SVG file to a Windows .ico file.
                        If you don't provide an input file name,
                        this program will show the window to drag and drop the SVG file.
                        If you don't provide an output file name,
                        the input file name will be used with a .ico extension.''')
@click.option("--preset", type=click.Choice(PRESETS, case_sensitive=False), default=PRESETS[0], help="The preset name of icon sizes: " + ", ".join(PRESETS))
@click.option("-i", "--input", type=str, help="The input file name to convert to a Windows .ico file.")
@click.option("-o", "--output", type=str, help="The output file name (.ico or .icns). If not provided, the input file name will be used with a .ico or .icns extension.")
@click.version_option()
def main(preset, input, output):
    if input is None:
        _run_gui(preset)
    else:
        from .converter import convert
        convert(preset, input, output)

def _run_gui(preset):
    from .gui import MainApp
    app = MainApp(preset)
    app.MainLoop()

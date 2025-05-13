import click

@click.command(help='''Convert a SVG file to a Windows .ico file.
                        If you don't provide an input file name,
                        this program will show the window to drag and drop the SVG file.
                        If you don't provide an output file name,
                        the input file name will be used with a .ico extension.''')
@click.option("-i", "--input", type=str, help="The input file name to convert to a Windows .ico file.")
@click.option("-o", "--output", type=str, help="The output file name. If not provided, the input file name will be used with a .ico extension.")
@click.version_option()
def main(input, output):
    if input is None:
        _run_gui()
    else:
        from .converter import convert
        convert(input, output)

def _run_gui():
    from .gui import MainApp
    app = MainApp()
    app.MainLoop()

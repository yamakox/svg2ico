import wx
import wx.lib.scrolledpanel as scrolled
from .converter import convert
from PIL import Image
from pathlib import Path
from .converter import PRESET_ICO_SIZES

WINDOW_SIZE = (510, 400)
BITMAP_SIZE = 48
PRESETS = list(PRESET_ICO_SIZES.keys())

class MainApp(wx.App):
    def __init__(self, preset: str, *args, **kw):
        self.preset = preset
        super().__init__(*args, **kw)

    def OnInit(self):
        self.frame = MainFrame(self.preset, None)
        self.frame.Show()
        return True

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window: 'MainFrame'):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        preset = self.window.get_selected_preset()
        if not preset:
            wx.MessageBox(
                f'icon preset is not selected.', 
                parent=self.window, 
                style=wx.OK_DEFAULT|wx.ICON_ERROR, 
            )
            return
        self.window.preview_sizer.Clear(True)
        for filename in filenames:
            self.__convert(preset, filename)
        return True
    
    def __convert(self, preset, filename):
        try:
            output = convert(preset, filename)
            image = (Image.open(output)  # 1枚目(256x256)のみ読み込む
                     .resize((BITMAP_SIZE, BITMAP_SIZE), Image.Resampling.LANCZOS)
                     .convert('RGBA')
            )
            self.window.add_preview(_convert_image_to_bitmap(image))
        except Exception as excep:
            wx.MessageBox(
                f'Error occurred: {str(excep)}', 
                parent=self.window, 
                style=wx.OK_DEFAULT|wx.ICON_ERROR, 
            )

class MainFrame(wx.Frame):
    def __init__(self, preset: str, *args, **kw):
        super().__init__(*args, **kw)
        base_path = Path(__file__).parent.resolve()

        self.SetSize(self.FromDIP(wx.Size(*WINDOW_SIZE)))
        self.SetTitle('svg2ico')
        self.SetIcon(wx.Icon(str(base_path / 'example.drawio.ico')))

        panel = wx.Panel(self)
        sizer = wx.FlexGridSizer(3, 1, gap=wx.Size(10, 10))
        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(0)

        preset_panel = wx.Panel(panel)
        preset_sizer = wx.GridSizer(1, len(PRESETS), gap=wx.Size(10, 10))
        style = wx.RB_GROUP
        self.preset_buttons: dict[str, wx.RadioButton] = {}
        for i in PRESETS:
            self.preset_buttons[i] = wx.RadioButton(preset_panel, label=i, style=style)
            preset_sizer.Add(self.preset_buttons[i], flag=wx.ALIGN_CENTER)
            style = 0
        self.preset_buttons[preset].SetValue(True)
        preset_panel.SetSizer(preset_sizer)
        sizer.Add(preset_panel, flag=wx.TOP|wx.ALIGN_CENTER)     # 0行目

        self.preview_panel = scrolled.ScrolledPanel(panel)
        self.preview_panel.SetAutoLayout(True)
        self.preview_sizer = wx.WrapSizer(wx.HORIZONTAL)
        self.preview_panel.SetSizer(self.preview_sizer)
        #self.preview = wx.StaticBitmap(panel, bitmap=self.blank_bitmap)
        sizer.Add(self.preview_panel, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM)     # 1行目

        label = wx.StaticText(panel, label="Drag and drop a SVG file here")
        sizer.Add(label, flag=wx.ALIGN_CENTER)      # 2行目

        panel.SetSizerAndFit(sizer)

        panel.SetDropTarget(FileDropTarget(self))

    def add_preview(self, bitmap: wx.Bitmap):
        sb = wx.StaticBitmap(self.preview_panel, bitmap=bitmap)
        self.preview_sizer.Add(sb, proportion=0, flag=wx.ALL, border=10)
        self.preview_panel.SetupScrolling(scroll_x=True, scroll_y=True, scrollIntoView=True, scrollToTop=False)

    def get_selected_preset(self) -> str:
        for i in self.preset_buttons.keys():
            if self.preset_buttons[i].GetValue():
                return i
        return None

# MARK: private functions

def _convert_image_to_bitmap(image: Image) -> wx.Bitmap:
    w, h = image.size
    rgba_data = image.tobytes()

    # RGBとAlphaを分離
    rgb_data = bytearray()
    alpha_data = bytearray()
    for i in range(0, len(rgba_data), 4):
        r, g, b, a = rgba_data[i:i+4]
        rgb_data.extend((r, g, b))
        alpha_data.append(a)

    wx_image = wx.Image(w, h)
    wx_image.SetData(bytes(rgb_data))   # RGB部分を設定
    wx_image.SetAlpha(bytes(alpha_data))  # アルファチャンネル設定

    return wx_image.ConvertToBitmap()

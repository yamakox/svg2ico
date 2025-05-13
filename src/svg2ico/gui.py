import wx
from .converter import convert
from PIL import Image
from pathlib import Path

BITMAP_SIZE = 64

class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None)
        self.frame.Show()
        return True

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            self.__convert(filename)
        return True
    
    def __convert(self, filename):
        try:
            output = convert(filename)
            image = (Image.open(output)  # 1枚目(256x256)のみ読み込む
                     .resize((BITMAP_SIZE, BITMAP_SIZE), Image.Resampling.LANCZOS)
                     .convert('RGBA')
            )
            self.window.preview.SetBitmap(_convert_image_to_bitmap(image))
        except Exception as excep:
            self.window.preview.SetBitmap(self.window.blank_bitmap)
            wx.MessageBox(
                f'Error occurred: {str(excep)}', 
                parent=self.window, 
                style=wx.OK_DEFAULT|wx.ICON_ERROR, 
            )

class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.blank_bitmap = wx.Bitmap(BITMAP_SIZE, BITMAP_SIZE)
        base_path = Path(__file__).parent.resolve()

        self.SetSize(self.FromDIP(wx.Size(400, 300)))
        self.SetTitle('svg2ico')
        self.SetIcon(wx.Icon(str(base_path / 'example.ico')))

        panel = wx.Panel(self)
        sizer = wx.FlexGridSizer(4, 1, wx.Size(10, 10))
        sizer.AddGrowableRow(0)
        sizer.AddGrowableRow(3)
        sizer.AddGrowableCol(0)
        panel.SetSizer(sizer)
        sizer.AddSpacer(0)  # 0行目
        label = wx.StaticText(panel, label="Drag and drop a SVG file here")
        sizer.Add(label, flag=wx.ALIGN_CENTER)      # 1行目
        self.preview = wx.StaticBitmap(panel, bitmap=self.blank_bitmap)
        sizer.Add(self.preview, flag=wx.ALIGN_CENTER)     # 2行目
        sizer.AddSpacer(0)  # 3行目

        panel.SetDropTarget(FileDropTarget(self))

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

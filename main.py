import os
import sys
import logging

import wx
import pcbnew

try:
    import easyeda2kicad.__main__ as easyeda2kicad
except ImportError:
    easyeda2kicad = None

# TODO:
#  - update library tables
#  - download folder selection

logger = logging.getLogger()


def download_part(lcsc_id, dir):
    os.makedirs(os.path.dirname(dir), exist_ok=True)
    easyeda2kicad.main(["--full", f"--lcsc_id={lcsc_id}", "--output", dir, "--overwrite"])


class Plugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "EasyEDA Parts"
        self.category = "Library download"
        self.description = "Download footprints, symbols and 3d models from EasyEDA."
        self.show_toolbar_button = True
        path, filename = os.path.split(os.path.abspath(__file__))
        self.icon_file_name = os.path.join(path, "icon.png")

    def Run(self):
        dialog = Dialog(None)
        dialog.Centre()
        dialog.Show()


class Dialog(wx.Dialog):
    def __init__(self, parent):
        if sys.platform != "darwin":
            self.app = wx.App()
        wx.Dialog.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="EasyEDA Parts",
            pos=wx.DefaultPosition,
            size=wx.Size(400, 300),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX,
        )

        board = pcbnew.GetBoard()
        download_dir = f"{os.path.dirname(board.GetFileName())}/libs/easyeda/easyeda"

        content = wx.BoxSizer(wx.VERTICAL)

        grid = wx.GridSizer(2, 2, 5, 5)

        text_lcsc_id_title = wx.StaticText(self, wx.ID_ANY, "LCSC ID:")
        grid.Add(text_lcsc_id_title, 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        text_edit_lcsc_id = wx.TextCtrl(self, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER)
        text_edit_lcsc_id.SetHint("e.g. C2040")
        grid.Add(text_edit_lcsc_id, 0, wx.EXPAND)

        download_button = wx.Button(self, wx.ID_ANY, "Download")
        download_button.Bind(wx.EVT_BUTTON,
                             lambda event: self._on_download_click(text_edit_lcsc_id.GetValue(), download_dir))
        grid.Add(download_button, 0, wx.EXPAND)

        done_button = wx.Button(self, wx.ID_OK, "Done")
        grid.Add(done_button, 0, wx.EXPAND)

        if easyeda2kicad: content.Add(grid, 0, flag=wx.EXPAND | wx.ALL, border=10)

        text_log = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString,
                               wx.DefaultPosition, wx.DefaultSize,
                               wx.TE_MULTILINE | wx.TE_READONLY)
        logger.addHandler(TextCtrlHandler(text_log))
        content.Add(text_log, 1, wx.EXPAND, 5)

        self.SetSizer(content)
        self.Layout()
        self.Centre(wx.BOTH)

        logger.info(f"Download folder: {download_dir}")

        if not easyeda2kicad:
            logger.error("easyeda2kicad not found, please install it first with `pip install easyeda2kicad`")

    def _on_download_click(self, lcsc_id, download_dir):
        download_part(lcsc_id, download_dir)


class TextCtrlHandler(logging.Handler):
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.WriteText, s)

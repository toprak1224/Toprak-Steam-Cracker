import os
import sys
import webview

def _static_path():
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "static")

def run(api):
    static = _static_path()
    url = "file:///" + os.path.join(static, "index.html").replace("\\", "/")

    window = webview.create_window(
        title="Toprak Steam Cracker",
        url=url,
        js_api=api,
        width=1280,
        height=820,
        min_size=(960, 640),
        background_color="#0a0a0f",
        frameless=False,
        easy_drag=False,
        text_select=False,
    )
    api.set_window(window)
    webview.start(debug=False, http_server=False)

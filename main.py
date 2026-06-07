import os
import sys

def main():

    system32 = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
    if system32 not in os.environ.get('PATH', ''):
        os.environ['PATH'] = system32 + ';' + os.environ.get('PATH', '')

    from ui_web.bridge import API
    import ui_web.window as web_window

    api = API()
    web_window.run(api)

if __name__ == "__main__":
    main()

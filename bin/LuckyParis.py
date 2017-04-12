from UI.server import *
import webbrowser

def setup():
    svr = LPServer("", 8080)

    webbrowser.open('http://127.0.0.1:8080')
    svr.serve_forever()

setup()
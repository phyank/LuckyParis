from UI.server import *
import webbrowser



def setup():
    svr = LPServer("", 18080)

    webbrowser.open('http://127.0.0.1:18080')
    svr.serve_forever()

setup()
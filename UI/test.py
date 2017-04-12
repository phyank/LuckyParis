from UI.server import *

def test():
    svr = LPServer("", 8080)
    svr.serve_forever()

test()
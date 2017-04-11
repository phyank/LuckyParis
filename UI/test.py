from UI.server import *

def test():
    svr = HTTPServer(("", 8080), MyRequestHandler)
    svr.serve_forever()

test()
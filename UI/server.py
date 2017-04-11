# A light weight server in Django style powered by Python Standard Lib
# See views.py to learn how to write a view

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse, io, shutil, os
from http import HTTPStatus
from UI.views import *


class MyRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.content = ""
        self.commands = ['/test']
        self.error_message_format=DEFAULT_ERROR_MESSAGE

        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):

        self.do_response("GET")

    def do_POST(self):

        self.do_response("POST")

    def serve_file(self, path):
        
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return False
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return False
        ctype = 'text/plain'

        try:

            f = open(os.path.dirname(__file__)+path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return False

        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            shutil.copyfileobj(f, self.wfile)

            return True
        except:
            f.close()
            raise

    def do_response(self, method):

        if method == "POST":
            query = urllib.parse.splitquery(self.path)
            requestPath = query[0]

            data = self.rfile.read(int(self.headers['content-length']))

            data = urllib.parse.unquote(data.decode("utf-8", 'ignore'))

            dataDict = {}

            for i in data.split("&"):
                key, _, value = i.partition("=")
                dataDict[key] = value

            responsefromView=command_selector(requestPath, "POST", dataDict)


        else:
            query = urllib.parse.splitquery(self.path)
            requestPath = query[0]

            dataDict={}

            if '?' in self.path:

                if query[1]:

                    for i in query[1].split('&'):
                        k = i.split('=')

                        print(k[0])

                        dataDict[k[0]] = urllib.parse.unquote(k[1])
                else:
                    pass

            responsefromView = command_selector(requestPath, "GET", dataDict)

        if not responsefromView :
            self.serve_file(requestPath)
            return

        self.content = responsefromView.content

        f = io.BytesIO()

        f.write(self.content)

        f.seek(0)

        self.send_response(responsefromView.status)

        for i in responsefromView.head:
            self.send_header(i, responsefromView.head[i])

        self.end_headers()

        shutil.copyfileobj(f, self.wfile)



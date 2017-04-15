# A light weight server in Django style powered by Python Standard Lib
# See views.py to learn how to write a view

from http.server import BaseHTTPRequestHandler,HTTPServer
import urllib.parse, io, shutil
from http import HTTPStatus
from UI.views import *

MIME_LIST={"css":"text/css","js":"application/x-javascript","jpg":"image/jpeg",
           "jpeg":"image/jpeg","png":"image/png","gif":"image/gif","ico":"image/x-ico"}


class MyRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.content = ""
        self.error_message_format=DEFAULT_ERROR_MESSAGE # You can define your error page here

        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):

        self.do_response("GET")

    def do_POST(self):

        self.do_response("POST")

    def MIME_identify(self,path):
        ctype = "text/plain"
        try:

            fileType=path
            while "." in fileType:
                _, _, fileType = fileType.partition(".")

            ctype=MIME_LIST[fileType]

        except:
            pass

        #print("Path:"+path+"\nType:"+ctype)
        return ctype

    # This function serve static files. You'd better serve
    # HTML templates in views.py. You should define a MIME
    # type in MIME_LIST before serve a new type of files

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


        try:

            f = open(os.path.dirname(__file__)+path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return False

        ctype = self.MIME_identify(path)

        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.send_header("Cache-Control","no-store")
            self.end_headers()
            shutil.copyfileobj(f, self.wfile)

            return True
        except:
            f.close()
            raise

    def do_response(self, method):

        path_and_query = urllib.parse.splitquery(self.path) # Separate the query from the path
        requestPath = path_and_query[0]
        if path_and_query[1]: query = path_and_query[1]
        else: query=""

        dataDict = {}

        if method == "POST":


            data = self.rfile.read(int(self.headers['content-length']))

            data = urllib.parse.unquote(data.decode("utf-8", 'ignore'))

            for i in data.split("&"):
                key, _, value = i.partition("=")
                dataDict[key] = value

            responsefromView=command_selector(requestPath, "POST", dataDict)


        else: #method=="GET"

            if '?' in self.path:

                if query:

                    for i in query.split('&'):
                        k = i.split('=')

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


class LPServer(HTTPServer):
    def __init__(self,addr, port, bind_and_active=True):
        HTTPServer.__init__(self,(addr,port),MyRequestHandler,bind_and_active)


def test():
    svr = LPServer("", 8080)
    svr.serve_forever()

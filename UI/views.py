from jinja2 import Template
import os

from database.mainDB import MainDB

TEST_PAGE="""<!DOCTYPE html>
<html>
<head>
<link href="/css/test.css" rel="stylesheet" />
</head>
<body>
<div class="test">
<p>Test:红帽子</p>
<p>设置PyCharm支持中文</p>
</div>
<div>
<img src="/static/image/test.jpg" />
</body>
</html>
"""

DEFAULT_ERROR_MESSAGE = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: %(code)d</p>
        <p>Message: %(message)s.</p>
        <p>Error code explanation: %(code)s - %(explain)s.</p>
    </body>
</html>
"""

class FileOpeningError:
    pass

class UIStatus:
    def __init__(self):
        self.ifLogIn=False

        self.username=""
        self.password=""

class ViewsResponse:
    def __init__(self, content, head={}, status=200):
        self.status=status
        self.head=head
        self.content=content.encode("UTF-8")
        if status==200:
            self.head["Content-type"] = "text/html;charset=UTF-8"
        if len(self.content)!=0:
            self.head["Content-Length"]=str(len(self.content))


class ViewsRedirect(ViewsResponse):
    def __init__(self,url="/"):
        ViewsResponse.__init__(self,"",head={"Location":url},status=301)


uiStatus=UIStatus()
db=MainDB()


def open_file_as_string(filepath):

    filepath=os.path.dirname(__file__)+filepath

    if os.path.exists(filepath):
        try:
            f=open(filepath, "rb")
            result = (f.read()).decode('utf-8','ignore')
            f.close()
            return result
        except:
            raise FileOpeningError
    else:
        raise FileNotFoundError


def command_selector(command,method,data):

    if command=="/test":
        return test(method,data)

    elif command=="/":
        return index(method,data)

    elif command=="/login":
        return login(method, data)

    elif command=="/search":
        return search(method, data)

    elif command=="/logout":
        return logout(method,data)


    else:
        return


#Views:

def index(method,data):
    if method=="GET":
        if uiStatus.ifLogIn:
            indexT=Template(open_file_as_string('/static/template/index.html'))
            db_data=db.get_summer_course()
            result=indexT.render(db_data)
            return ViewsResponse(result)

        else:
            return ViewsRedirect("/login")
    else:
        return ViewsRedirect("/")

def login(method,data):
    if uiStatus.ifLogIn:
        return ViewsRedirect("/")
    elif method=="GET":
        return ViewsResponse(open_file_as_string("/static/template/login.html"))
    elif method=="POST":
        #TODO: Check
        uiStatus.username,uiStatus.password = data['user'],data['pass']
        uiStatus.ifLogIn = True
        return ViewsRedirect("/")
    else:
        return ViewsRedirect("/")

def logout(method,data):
    uiStatus.username, uiStatus.password="",""
    uiStatus.ifLogIn=False
    return ViewsRedirect("/login")

def search(method,data):

    if method == "GET":
        return ViewsRedirect("/")

    else:
        if not data["keywords"]:
            return ViewsRedirect("/")
        else:
            db_result = db.search(data["keywords"])
            searchT = Template(open_file_as_string('/static/template/index.html'))
            result = searchT.render(db_result)
            return ViewsResponse(result)

def test(method,data):

    if method=="POST":
        for i in data:
            print("key:"+i+"\n"+"value:"+data[i])
        return ViewsResponse(TEST_PAGE)
    elif method=="GET":
        if not data:
            return ViewsResponse(TEST_PAGE)
        else:
            c=""
            for i in data:
                c += i + ':' + data[i] + "\r\n"
            return ViewsResponse(c)
    else:
        return ViewsRedirect('/css/test.css')



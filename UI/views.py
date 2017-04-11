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





def command_selector(command,method,data):
    if command=="/test":
        return test(method,data)

    else:
        return


#Views:

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



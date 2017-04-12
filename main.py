from utils.login.session import SessionFactory
from utils.spider.spiders import SummerSpider

class LoginError:
    pass

class CtlCenter:
    def __init__(self):
        self.loginTool = SessionFactory()
        self.summerSpider = SummerSpider()
        self.session=0
    def get_session(self,type,usr,passwd):
        try:
            self.session = self.loginTool.create(type, usr, passwd)
            return 0
        except LoginError:
            return 1

def main():
    ctl=CtlCenter()
    while True:
        command=input("$>")
        command.split(" ")
        if command[0]=="login":
            if ctl.get_session(command[1], command[2], command[3])==1:
                print("登录失败！")
                continue
            else:
                print("登陆成功！")
                continue

main()
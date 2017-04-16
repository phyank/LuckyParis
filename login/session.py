# factory
from bin.settings import (NORMAL_CHECK_URL_TEMPLATE,
                       ELE_LOGIN_URL, SUMMER_CHECK_URL_TEMPLATE, JACCOUNT_URL,
                       CACHE_SESSION_PATH,SLEEP_DURATION)

from urllib.parse import unquote
from time import sleep
from functools import wraps
from io import BytesIO
import shutil
import requests
import logging
import re
import pickle
import os

#logger = logging.getLogger(__name__)

#FIXME:Use mainStatus to report, No printing.
class Session(object):
    MAX_LOGIN_TRAIL = 10
    SLEEP_DURATION=3
    CHECK_URL=SUMMER_CHECK_URL_TEMPLATE % 2
    ''' 包装requests.session，进行登录后的验证和处理教务网的message和session过期
    '''
    def __init__(self, mainStatus, mainStatusmutex):
        self.mainStatus=mainStatus
        self.mutex=mainStatusmutex
        self.form={}
        self.try_count=0
        self.raw_session=0

        self.report_status(1,"会话初始化")

    def prepare(self):
        def __parse_jaccount_page(html):
            search_pattern = r'\<input type=\"hidden\" name=\"(\w+)\" value=\"([a-zA-Z0-9_+/=]+)\"\>'
            for match in re.finditer(search_pattern, html):
                yield match.groups()
        try:
            self.raw_session = requests.Session()
            jaccount_response = self.raw_session.get(ELE_LOGIN_URL)
            self.form = dict(__parse_jaccount_page(jaccount_response.text))
            captcha_url = JACCOUNT_URL + re.search(
                r'\<img src=\"(captcha\?\d+)\"',
                jaccount_response.text).group(1)

            capfile=open(os.path.join("UI","static","image","captcha.jpg"),"wb")
            shutil.copyfileobj(BytesIO(self.raw_session.get(captcha_url, stream=True).content)
                            ,capfile)
            capfile.close()
            return True

        except: return False


    def login(self,username,password,captcha):
            self.form.update({'v': '',
                         'user': username,
                         'pass': password,
                         'captcha': captcha})
            post_response = self.raw_session.post(
                JACCOUNT_URL+'ulogin', data=self.form)

            self.try_count+=1
            if '教学信息服务网' in post_response.text:
                self.report_status(2,"登录成功！")
                self.raw_session.head(self.CHECK_URL)
                return True
            else:
                self.report_status(3,"登录失败，等待继续尝试。")
                return False

    def check_session(self,response):
        if response.status_code>399:
            print(response.text)
        if 'outTimePage.aspx' in response.url:
            self.report_status(5,"会话过期，请重新登录！")
            return False
        try:
            message = unquote(response.url.split('message=')[1])
            if '刷新' in message:
                self.report_status(7,"请求过于频繁！:"+message)
                print("Sleeping...")
                sleep(SLEEP_DURATION)
                return True
            else:
                self.report_status(6,"未知错误:"+message)
                return False
        except:
            self.report_status(2,"会话状态正常。")
            return False

    def report_status(self,code,msg,addition=""):
        self.status=code

        with self.mutex:
            self.mainStatus.logInStatus = code
            self.mainStatus.logInMessage = msg
            if addition:
                self.mainStatus.messageToUI=addition

    def get(self, *args, **kwargs):
        ifcontinue=True
        response=0
        while ifcontinue:
            response = self.raw_session.get(*args, **kwargs)
            ifcontinue=self.check_session(response)
        return response

    def post(self, url, data, asp_dict, *args, **kwargs):
        if '__VIEWSTATE' not in data:
             data.update(asp_dict)
        ifcontinue=True
        response = 0
        while ifcontinue:
            response = self.raw_session.post(url=url, data=data, *args, **kwargs)
            ifcontinue=self.check_session(response)
        return response

    def head(self, *args, **kwargs):
        ifcontinue=True
        response = 0
        while ifcontinue:
            response = self.raw_session.head(*args, **kwargs)
            ifcontinue=self.check_session(response)
        return response



class SummerSession(Session):
    CHECK_URL = SUMMER_CHECK_URL_TEMPLATE % 2
    SLEEP_DURATION = 2

# FIXME: This should be a singleton.
class SessionFactory(object):
    ''' Abstract session factory with CHECK_URL_TEMPLATE not specified.
    '''
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def create(self, description):
        session = Session(self.username, self.password)
        if description['type'] == 'summer':
            session.CHECK_URL = SUMMER_CHECK_URL_TEMPLATE % description['round']
            return session
        elif description['type'] == 'normal':
            session.CHECK_URL = NORMAL_CHECK_URL_TEMPLATE % description['round']
            return session
        else:
            raise ValueError("ListPage has no type %s" % description)

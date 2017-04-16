from login.session import SummerSession
from spider.parsers import SummerParser
# TODO: use relative import here
from bin.settings import (SUMMER_SUBMIT_URL, SELECT_SUMMER_COURSE_URL,
                        COURSE_DATA_PATH, SUMMER_URL, TONGSHI_NAMES,SLEEP_DURATION)

from time import sleep
import re
import json
#import logging

from spider.parsers import ElectorParser

# logger = logging.getLogger(__name__)
# cid_logger = logging.getLogger('cid')
# fh = logging.FileHandler('/tmp/course_record.log')
# fh.setLevel(logging.INFO)
# fh.setFormatter(logging.Formatter('[+] %(asctime)s - %(message)s'))
# cid_logger.addHandler(fh)
#
# cid_logger.error('Logger Started.')

#FIXME:Use mainStatus to report, No printing.
# FIXME: add a factory and refactor it with spider.
class SummerElector(object):
    SUBMIT_URL = SUMMER_SUBMIT_URL
    URL = SUMMER_URL
    SLEEP_DURATION = 2
    def __init__(self,session,mainStatus,mainDBdict,mutex):

        self.mutex=mutex

        self.session = session

        self.db=mainDBdict

        self.mainStatus=mainStatus

        temp0=self.session.get(self.URL)

        temp1=SummerParser(temp0)

        self.asp_dict = temp1.get_asp_args()

        self.seen_available = set()

        print("elector init")

    def get_non_full_tongshi_cid(self, wanted_types=TONGSHI_NAMES):
        sleep(self.SLEEP_DURATION)
        for tr in self.session.get(self.URL).text.split('<tr class="tdcolour')[1:]:
            try:
                cid, ctype, is_full = [tr.split('<td')[i] for i in [3, 5, 9]]
                cid = re.search(r'\>(\w+)\s*\</td\>', cid).group(1)
                ctype = re.search(r'\>(&?\w+;?)\s*\</td\>', ctype).group(1)
                is_full = re.search(r'人数(\w+)\s*\</td\>', is_full).group(1) \
                    == '满'
                if ctype.strip() in wanted_types and not is_full:
                    if False:
                        yield cid

                # data logger
                if cid not in self.seen_available and not is_full:
                    self.seen_available.add(cid)
                    #cid_logger.info('%s is available' % cid)
                elif cid in self.seen_available and is_full:
                    self.seen_available.remove(cid)
                    #cid_logger.info('%s is full' % cid)
            except AttributeError:
                pass

    # TODO: Implement this with sqlite
    def _load_db(self):
        ''' 加载课程数据
        '''
        with open(COURSE_DATA_PATH, 'r') as f:
            self.db = json.load(f)

    def grab_course_by_cid(self, cid):
        ''' 抢该课号的课程里第一个老师的课.
        '''
        for record in self.db:
            if record['cid'] == cid:
                self.select_course_by_bsid(record['bsid'])

    def _submit(self):
        ''' 进行选课提交
        '''
        submit_response = self.session.post(url=self.SUBMIT_URL,
                                            data={'btnSubmit': '选课提交'},
                                            asp_dict=self.asp_dict)
        result=self.session.get(submit_response.url)
        return result

    #FIXME:if self.URL in url
    def select_course_by_bsid(self, bsid):

        self._select_course_by_bsid(bsid)
        result=self._submit()

        url=result.url

        parser=ElectorParser()
        parser.feed(result.text)


        if self.session.status in [5,6]:
            return False

        if self.URL in url:
            for i in parser.tablehref:
                if str(bsid) in i:
                    with self.mutex:
                        self.mainStatus.electorStatus=2
                        self.mainStatus.electorMessage='%s submit success' % bsid
                        self.mainStatus.electorRetryCounter=0
                        self.mainStatus.messageToUI = '%s submit success' % bsid
                    #logger.info('%s submit success' % bsid)
                    return True
        with self.mutex:
            self.mainStatus.electorStatus=3
            self.mainStatus.electorMessage='%s submit failed' % bsid
            self.mainStatus.electorRetryCounter+=1
        #logger.info('%s submit failed' % bsid)
        return False

    def get_asp_by_bsid(self, bsid):
        for record in self.db:
            if record['bsid'] == bsid:
                return record['asp']
        raise KeyError("bsid %s not found in database." % bsid)

    def _select_course_by_bsid(self, bsid):
        return self.session.post(
            url=SELECT_SUMMER_COURSE_URL,
            data={'LessonTime1$btnChoose':
                  '选定此教师', 'myradiogroup': bsid},
            asp_dict=self.get_asp_by_bsid(bsid))



    #FIXME:Use mainStatus to report, No printing.
    def run(self, wanted_types=TONGSHI_NAMES):
        #logger.debug('Elector Started...')
        while True:
            for cid in self.get_non_full_tongshi_cid(wanted_types):
                self.grab_course_by_cid(cid)


if __name__ == '__main__':
    elector = SummerElector('username', 'password')
    elector.run()

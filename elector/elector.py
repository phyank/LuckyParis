from ..login.session import SummerSession
from ..spider.parsers import SummerParser
# TODO: use relative import here
from ..settings import (SUMMER_SUBMIT_URL, SELECT_SUMMER_COURSE_URL,
                        COURSE_DATA_PATH, SUMMER_URL, TONGSHI_NAMES)

from time import sleep
import re
import json
import logging

logger = logging.getLogger(__name__)


# FIXME: add a factory and refactor it with spider.
class SummerElector(object):
    SUBMIT_URL = SUMMER_SUBMIT_URL
    URL = SUMMER_URL
    SLEEP_DURATION = 2
    def __init__(self, username, password):
        self.session = SummerSession(username, password)
        self._load_db()
        self.asp_dict = SummerParser(self.session.get(self.URL)).get_asp_args()

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
                    if cid != 'LA936':
                        yield cid
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
        return self.session.get(submit_response.url)

    def select_course_by_bsid(self, bsid):
        self._select_course_by_bsid(bsid)
        if self.URL in self._submit().url:
            logger.info('%s submit success' % bsid)
        else:
            logger.info('%s submit failed' % bsid)

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
            asp_dict=json.loads(self.get_asp_by_bsid(bsid)))

    def run(self, wanted_types=TONGSHI_NAMES):
        logger.debug('Elector Started...')
        while True:
            for cid in self.get_non_full_tongshi_cid(wanted_types):
                self.grab_course_by_cid(cid)


if __name__ == '__main__':
    elector = SummerElector('username', 'password')
    elector.run()

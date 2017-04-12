import sqlite3 as db
import os, json

class TestCourse:
    def __init__(self):
        self.B="B"
        self.C="C"
        self.D="D"
        self.E="E"

testdict=[{"B":"wowo","C":"yeahyeah","D":"haha","E":"fafa"},
          {"B": "wowo", "C": "yeahyeah", "D": "haha", "E": "fafa"},
          {"B": "wowo", "C": "yeahyeah", "D": "haha", "E": "fafa"}]

class MainDB:

    def __init__(self):
        print("db init")
    #
    #     self.ifExist = os.path.exists('db.sqlite3')
    #
    #     self.connection=db.connect('db.sqlite3')
    #     self.cursor=self.connection.cursor()
    #
    #     if not self.ifExist:
    #         self.cursor.execute('''CREATE TABLE "SummerClass(   cid text,
    #                                                             min_member real,
    #                                                             type text
    #                                                             credit text
    #                                                             hours text,
    #                                                             time text,
    #                                                             teacher_job text,
    #                                                             asp text,
    #                                                             remark text,
    #                                                             max_number text,
    #                                                             name text,
    #                                                             now_member text,
    #                                                             bsid text,
    #                                                             teacher text)
    #         ''')

    def get_summer_course(self):
        return {'dicts':testdict}

    def search(self,keywords):
        return {'dicts':[{"B":keywords,"C":keywords,"D":keywords,"E":keywords}]}
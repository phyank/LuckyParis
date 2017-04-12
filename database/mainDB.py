import sqlite3
import os, json
from database.load import *


class MainDB:
    def __init__(self):
        print("db init")

        self.dictkeys=['bsid','name','cid','teacher','teacher_job','remark','type',\
                       'credit','hours','max_member','min_member','now_member','time','asp']

        self.ifExist = os.path.exists('db.sqlite3')

        if not self.ifExist:
            connection = sqlite3.connect('db.sqlite3')
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE 
                                    SummerClass(   bsid    integer key not null,
                                                                name    nchar(15),
                                                                cid     nchar(8),
                                                                teacher nchar(10),
                                                                teacher_job ntext,
                                                                remark  ntext,
                                                                type    nchar(5),
                                                                credit  nchar(4),
                                                                hours   integer,
                                                                max_member integer,
                                                                min_member integer,
                                                                now_member integer,
                                                                time    ntext,
                                                                asp     ntext )
            ''')


            connection.commit()

            connection.close()



    def check_dict(self,item):

        for i in self.dictkeys:
            if i in item:
                pass
            else:
                item[i]="NULL"
        return item

    def search_subcommand_generator(self,columns,keywords):

        subcommand = " "

        counter1 = 0
        for column in columns:

            subsubcommand = ""
            counter2 = 0
            for keyword in keywords:
                i = column + " =" + " '" + keyword + "'"
                if counter2:
                    subsubcommand = subsubcommand + " OR " + i
                else:
                    subsubcommand += i

                counter2 += 1

            if counter1:
                subcommand = subcommand + " OR " + subsubcommand
            else:
                subcommand += subsubcommand

            counter1 += 1

        subcommand += ""

        return subcommand

    def search(self,keywords):
        connection = sqlite3.connect("db.sqlite3")
        cursor = connection.cursor()

        if keywords == "-all":
            cursor.execute('select name,cid,teacher,credit,type,bsid from SummerClass')
            resulttuple = cursor.fetchall()
        else:
            keywords=keywords.split(" ")

            command="SELECT name,cid,teacher,credit,type,bsid FROM SummerClass WHERE "+self.search_subcommand_generator(["cid","name","teacher","type"],keywords)

            cursor.execute(command)

            resulttuple=cursor.fetchall()

            print('resulttuple:',resulttuple)

        connection.close()

        result=[]
        for i in resulttuple:
            tempdict={"name":i[0],"cid":i[1],"teacher":i[2],"credit":i[3],"type":i[4],"bsid":i[5]}
            result.append(tempdict)

        return {"dicts":result}

    def load_data(self,data):

        connection=sqlite3.connect("db.sqlite3")
        cursor=connection.cursor()

        datakeys=[]
        for i in data:
            datakeys.append(i['bsid'])

        cursor.execute("select bsid from SummerClass")
        dbkeytuples=cursor.fetchall()

        dbkeys=[]
        for ktp in dbkeytuples:
            dbkeys.append(ktp[0])

        deletecommand=''
        for k in datakeys:
            if k in dbkeys:
                deletecommand+="delete from SummerClass where bsid = "+str(k)+";"
        cursor.executescript(deletecommand)

        tupleclasses=[]
        for c in data:
            c=self.check_dict(c)
            tupleclasses.append((c['bsid'],c['name'],c['cid'],c['teacher'],c['teacher_job'],\
                                c['remark'],c['type'],c['credit'],c['hours'],c['max_member'],\
                                 c['min_member'],c['now_member'],json.dumps(c['time']),\
                                 json.dumps(c['asp'])))

        cursor.executemany('insert into SummerClass values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',tupleclasses)

        connection.commit()

        connection.close()

        return True


    #
    # for i in loaddata():
    #     print (type(i["asp"]))
    #     print(len(i))
#
def test():
#     subcommand = " "
#
#     counter1 = 0
#     for column in columns:
#
#         subsubcommand = "("
#         counter2 = 0
#         for keyword in keywords:
#             i = column + " LIKE" + " %" + keyword + "%"
#             if counter2:
#                 subsubcommand = subsubcommand + " OR " + i
#             else:
#                 subsubcommand += i
#
#             counter2 += 1
#
#         if counter1:
#             subcommand = subcommand + " )AND" + subsubcommand
#         else:
#             subcommand += subsubcommand
#
#         counter1 += 1
#
#     subcommand += " )"
#
#     return subcommand
#
# print(test(["a","c"],["b"]))

    dbtool=MainDB()

    dbtool.load_data(loaddata())

    print("data loaded!")

    print(dbtool.search("吴诗玉"))



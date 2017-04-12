#! /usr/bin/env python3

import json
def loaddata():
    with open('/home/hiro/LuckyParis/database/course.json') as f:
        data = json.load(f)
        return data

# for i in loaddata():
#     if i['bsid']==383397:
#         print(i)




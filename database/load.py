#! /usr/bin/env python3

import json,os
def loaddata():
    with open(os.path.dirname(__file__)+'/../database/course.json') as f:
        data = json.load(f)
        return data

# for i in loaddata():
#     if i['bsid']==383397:
#         print(i)




import numpy as np
import json
from collections import OrderedDict
import copy

# compress
import gzip
import base64

class dataInput:

    def __init__(self):
        self.isCompress = False

    def setJSONString(self, fstr):
        js = json.loads(fstr, object_pairs_hook=dict)

        ## 節点
        self.node = OrderedDict(js['node'])
        # 型をfloat に 統一する
        for ID in self.node:
            n = self.node[ID]
            for key in ['x', 'y', 'z']:
                if key in n:
                    n[key] = float(n[key]) if n[key] != None else 0.0
                else:
                    n[key] = 0.0


        ## 解析結果
        self.dict_fsec = []
        if 'result' in js:
            self.dict_fsec = js['result']


        ## 荷重
        self.load = []
        if 'load' in js:
            self.load = js['load']


        return None

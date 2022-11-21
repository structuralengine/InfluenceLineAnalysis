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

        ## 境界線
        self.line = []
        list1 = []
        list2 = []
        line = js['line']
        for id in self.load:
            L_id = self.load[id]
            L1_id = L_id[0]['L1']
            L2_id = L_id[0]['L2']
            L1 = line[int(L1_id)-1]
            L2 = line[int(L2_id)-1]
            L1_position = L1['position']
            L2_position = L2['position']
            for i in range(len(L1_position)):
                L1_x = L1_position[i]['x']
                L1_y = L1_position[i]['y']
                L2_x = L2_position[i]['x']
                L2_y = L2_position[i]['y']
                list1.append([L1_x, L1_y])
                list2.append([L2_x, L2_y])
            self.line.append([list1, list2])

        return None

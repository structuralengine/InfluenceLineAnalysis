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

    def setCompressJSON(self, data):
        self.isCompress = True
        js = self.decompress(data)
        self.setJSONString(js)

    def setJSONString(self, fstr):
        js = json.loads(fstr, object_pairs_hook=dict)
        self.setJSON(js)

    def setJSON(self, js: dict):

        self.production = js['production'] if 'production' in js else True
        self.uid = js['uid'] if 'uid' in js else None
        self.username = js['username'] if 'username' in js else ''
        self.password = js['password'] if 'password' in js else ''

        # ケースによって変わらないパラメータを取得

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


        ## 部材
        self.member = []
        if 'member' in js:
            self.member = js['member']
            # 型をstring に 統一する, 部材長さを計算しておく
            for ID in self.member:
                m = self.member[ID]
                m['ni'] = str(m['ni'])
                m['nj'] = str(m['nj'])
                m['L'] =  round(self.GetLength(m) * 1000) #部材長さを計算しておく
                # 節点に関する整合性をチェック
                for n in [m['ni'], m['nj'] ]:
                    # 存在しない節点を含むシェルはエラー
                    if not n in self.node:
                        return 'have a shell that contains nodes that do not exist.'


        ## 解析結果
        self.dict_fsec = []
        if 'result' in js:
            self.dict_fsec = js['result']
            # 型をstring に 統一する




        return None

    # 部材の長さを計算する
    def GetLength(self, target: dict):
        IDi   = target['ni']
        IDj   = target['nj']
        pi = self.node[IDi]
        pj = self.node[IDj]
        return self.GetDistance(pi, pj)

    # 2点間の距離を計算する
    def GetDistance(self, pi: dict, pj: dict):
        xx = pj['x']-pi['x']
        yy = pj['y']-pi['y']
        zz = pj['z']-pi['z']
        return np.sqrt(xx**2+yy**2+zz**2)

    def compress(self, js: str):
        # gzip圧縮する
        l = gzip.compress(js.encode())
        # Base64エンコードする
        byteBase64 = base64.b64encode(l)
        # string に変換
        return byteBase64.decode()

    def decompress(self, byteBase64):
        # base64型 を もとに戻す
        b = base64.b64decode(byteBase64)
        # str型に変換し、カンマでばらして int 配列に変換する
        l = eval(b) #[int(n) for n in b.decode().split(',')]
        # gzipを解凍する
        return gzip.decompress(bytes(l))



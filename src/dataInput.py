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

    def readTestData(self, fnameR='test.json'):
        f = open(fnameR, encoding="utf-8")
        fstr = f.read()  # ファイル終端まで全て読んだデータを返す
        f.close()
        self.setJSONString(fstr)

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
            n['x'] = float(n['x'])
            n['y'] = float(n['y'])
            n['z'] = float(n['z'])


        ## 部材
        self.member = []
        if 'member' in js:
            self.member = js['member']
            # 型をstring に 統一する, 部材長さを計算しておく
            for ID in self.member:
                m = self.member[ID]
                m['ni'] = str(m['ni'])
                m['nj'] = str(m['nj'])
                m['e'] = str(m['e'])
                m['xi'] = 1
                m['yi'] = 1
                m['zi'] = 1
                m['xj'] = 1
                m['yj'] = 1
                m['zj'] = 1
                m['cg'] = m['cg'] if 'cg' in m else 0
                m['L'] =  round(self.GetLength(m) * 1000) #部材長さを計算しておく
                # 節点に関する整合性をチェック
                for n in [m['ni'], m['nj'] ]:
                    # 存在しない節点を含むシェルはエラー
                    if not n in self.node:
                        return 'have a shell that contains nodes that do not exist.'



        ## 荷重
        self.load = []
        if 'load' in js:
            self.load = js['load']

            ### 型を 統一する
            for load in self.load.values():
                load['fix_node']   = str(load['fix_node'])   if 'fix_node'   in load else '1'
                load['fix_member'] = str(load['fix_member']) if 'fix_member' in load else '1'
                load['element']    = str(load['element'])    if 'element'    in load else '1'
                load['joint']      = str(load['joint'])      if 'joint'      in load else '1'

                if 'load_node' in load:
                    load_node =load['load_node']
                    # 型をstring に 統一する
                    for ln in load_node:
                        ln['n'] = str(ln['n'])
                        # 荷重
                        ln['tx'] = float(ln['tx']) if 'tx' in ln else 0  # load in x-direction
                        ln['ty'] = float(ln['ty']) if 'ty' in ln else 0  # load in y-direction
                        ln['tz'] = float(ln['tz']) if 'tz' in ln else 0  # load in z-direction
                        ln['rx'] = float(ln['rx']) if 'rx' in ln else 0  # moment around x-axis
                        ln['ry'] = float(ln['ry']) if 'ry' in ln else 0  # moment around y-axis
                        ln['rz'] = float(ln['rz']) if 'rz' in ln else 0  # moment around z-axis
                        # 強制変位
                        ln['dx'] = float(ln['dx']) if 'dx' in ln else 0  # deload in x-direction
                        ln['dy'] = float(ln['dy']) if 'dy' in ln else 0  # load in y-direction
                        ln['dz'] = float(ln['dz']) if 'dz' in ln else 0  # load in z-direction
                        ln['ax'] = float(ln['ax']) if 'ax' in ln else 0  # moment around x-axis
                        ln['ay'] = float(ln['ay']) if 'ay' in ln else 0  # moment around y-axis
                        ln['az'] = float(ln['az']) if 'az' in ln else 0  # moment around z-axis

                    # 存在しない節点の荷重は削除
                    for ln in load_node[:]:
                        if not ln['n'] in self.node:
                            load_node.remove(ln)
                else:
                    load['load_node'] = []

                if 'load_member' in load:
                    load_member = load['load_member']
                    # 型を統一する
                    for lm in load_member:
                        lm['m'] = str(lm['m'])
                        lm['mark'] = int(lm['mark'])
                        lm['L1'] = round(lm['L1']*1000) if 'L1' in lm else 0 # 1000倍して int型で管理
                        lm['L2'] = round(lm['L2']*1000) if 'L2' in lm else 0 # 1000倍して int型で管理
                        lm['P1'] = float(lm['P1']) if 'P1' in lm else 0
                        lm['P2'] = float(lm['P2']) if 'P2' in lm else 0

                    # 存在しない要素の荷重は削除
                    for lm in load_member[:]:
                        if not lm['m'] in self.member:
                            load_member.remove(lm)
                else:
                    load['load_member'] = []


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



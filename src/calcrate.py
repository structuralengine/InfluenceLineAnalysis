# ======================
# 3D Frame Analysis
# ======================
import numpy as np
from collections import OrderedDict

from scipy.sparse.linalg import spsolve
from scipy.sparse import csr_matrix

from dataInput import dataInput


class FrameCalc:

    def __init__(self, _inp: dataInput):
        self.inp = _inp

    # 全ての荷重ケースの解析を開始する
    def calcrate(self) -> str:

        # calcration
        for id in self.inp.load:
            pass

        return ""



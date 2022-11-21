# ======================
# 3D Frame Analysis
# ======================
import numpy as np
from scipy.spatial import Delaunay
from sympy.geometry import Point, Polygon
import matplotlib.pyplot as plt
from matplotlib import path
from collections import OrderedDict

from scipy.sparse.linalg import spsolve
from scipy.sparse import csr_matrix

from dataInput import dataInput


class FrameCalc:
    def __init__(self, _inp: dataInput):
        self.inp = _inp

    def HeronFormula(self, a, b, c):
        # スモールsの値を算出
        s = (a + b + c) / 2.0
        # 三角形の面積を算出
        S = np.sqrt(s * (s - a) * (s - b) * (s - c))

        # 面積を戻り値として返す
        return S

    def get_Length(self, pointA, pointB):
        x1 = pointA[0]
        y1 = pointA[1]
        x2 = pointB[0]
        y2 = pointB[1]

        L = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        return L

    def _calc_cross_point(self, pointA, pointB, pointC, pointD, coordinates):
        cross_point = (0,0,0)

        if pointA[0] > pointB[0]:
            x1 = pointA[0]
            x2 = pointB[0]
        else:
            x1 = pointB[0]
            x2 = pointA[0]

        if pointA[1] > pointB[1]:
            y1 = pointA[1]
            y2 = pointB[1]
        else:
            y1 = pointB[1]
            y2 = pointA[1]

        bunbo = (pointB[0] - pointA[0]) * (pointD[1] - pointC[1]) - (pointB[1] - pointA[1]) * (pointD[0] - pointC[0])

        # 直線が平行な場合
        if (bunbo == 0):
            return False, cross_point

        vectorAC = ((pointC[0] - pointA[0]), (pointC[1] - pointA[1]))
        r = ((pointD[1] - pointC[1]) * vectorAC[0] - (pointD[0] - pointC[0]) * vectorAC[1]) / bunbo
        s = ((pointB[1] - pointA[1]) * vectorAC[0] - (pointB[0] - pointA[0]) * vectorAC[1]) / bunbo

        # rを使った計算の場合
        distance = ((pointB[0] - pointA[0]) * r, (pointB[1] - pointA[1]) * r)
        cross_point = (int(pointA[0] + distance[0]), int(pointA[1] + distance[1]))

        # sを使った計算の場合
        # distance = ((pointD[0] - pointC[0]) * s, (pointD[1] - pointC[1]) * s)
        # cross_point = (int(pointC[0] + distance[0]), int(pointC[1] + distance[1]))

        # TINの構成線上に交点があるかを判定
        if x1 <= cross_point[0] <= x2 and y1 <= cross_point[1] <= y2:
            judge = True

            # 交点のZ座標を算出
            for i in range(len(coordinates)):
                coordinate = coordinates[i]
                point = coordinate.key
                if point[0] == pointA[0] and point[1] == pointA[1]:
                    zA = coordinate.value
                elif point[0] == pointB[0] and point[1] == pointB[1]:
                    zB = coordinate.value
            dx = x2 - x1
            dy = y2 - y1
            dz = np.abs(zB - zA)
            l = np.sqrt(dx**2 + dy**2)
            l2 = np.sqrt(cross_point[0]**2 + cross_point[1]**2)
            z = dz * l2 / l
            cross_point.append(z)

        else :
            judge = False

        return judge, cross_point

    # 全ての荷重ケースの解析を開始する
    def calcrate(self) -> str:

        # calcration
        # インプットデータを呼び出し
        for id in self.inp.load:
            pointlist = []
            P = self.inp.node
            for i in range(len(P)):
                point = P[str(i+1)]
                point_x = point["x"]
                point_y = point["y"]
                pointlist.append([point_x, point_y])
            P = np.array(pointlist)
            tri = Delaunay(P)
            com = tri.simplices
            line = self.inp.line
            myj = self.inp.dict_fsec
            point_z = []
            for value in myj.values():
                myj_v = value.values()
                point_z.append(myj_v)

        coordinates = []
        for i in range(len(point_z)):
            coordinate = pointlist[i]
            coordinate.extend(point_z[i])
            coordinates.append(coordinate)

        # 節点を繋いだ線分(外縁)の、起終点を線分ごとにまとめる
        line_points = []
        start_points = []
        end_points = []
        for i in range(len(line[0])):
            LineNo = line[0][i]
            start_points.append(LineNo[0])
            end_points.append(LineNo[-1])
            for j in range(len(LineNo)-1):
                startpoint = LineNo[j]
                endpoint = LineNo[j+1]
                line_points.append([startpoint, endpoint])
        # lineの起終点同士をつなぐ
        for i in range(len(start_points)-1):
            startpoint = start_points[i]
            endpoint = start_points[i-1]
            line_points.append([startpoint, endpoint])
            startpoint = end_points[i]
            endpoint = end_points[i-1]
            line_points.append([startpoint, endpoint])

        # 境界内に含まれたポイントのみを抽出
        point_in_range = []
        line_points_flatten = line[0][0]
        for i in range(len(line[0])-1):
            L0 = line[0][i + 1]
            L1 = L0[::-1]
            line_points_flatten.extend(L1)
        line_x = list()
        line_y = list()
        for i in range(len(line_points_flatten)):
            line_point = line_points_flatten[i]
            line_x.append(line_point[0])
            line_y.append(line_point[1])
        porygon_points = list()
        for i,X in enumerate(line_x):
            porygon_point = (X, line_y[i])
            porygon_points.append(porygon_point)
        # 境界をポリゴンとして、内外判定を実施
        polygon = Polygon(*porygon_points)
        for i in range(len(pointlist)):
            pickpoint_x = pointlist[i][0]
            pickpoint_y = pointlist[i][1]
            pickpoint = (pickpoint_x, pickpoint_y)
            judge = polygon.encloses_point(pickpoint)
            if judge == True:
                point_in_range.append(pickpoint)

        # 外縁とTINの交点を算出
        component_points = P[com] # TINの構成点（3点）
        edge_points = []
        for i in range(len(component_points)):
            cp = component_points[i]
            cp1 = cp[0]
            cp2 = cp[1]
            cp3 = cp[2]
            for j in range(len(line_points)):
                LP = line_points[j]
                LP1 = LP[0]
                LP2 = LP[1]
                crosspoint1 = self._calc_cross_point(cp1, cp2, LP1, LP2, coordinates)
                judge1 = crosspoint1[0]
                if judge1 == True:
                    edge_points.append(crosspoint1[1])
                crosspoint2 = self._calc_cross_point(cp2, cp3, LP1, LP2, coordinates)
                judge2 = crosspoint2[0]
                if judge2 == True:
                    edge_points.append(crosspoint2[1])
                crosspoint3 = self._calc_cross_point(cp3, cp1, LP1, LP2, coordinates)
                judge3 = crosspoint3[0]
                if judge3 == True:
                    edge_points.append(crosspoint3[1])

        #面積算出用のTINをポイントでまとめる
        point_on_range = []
        for i in range(len(edge_points)):
            EP = edge_points[i]
            coordinates.append(EP)
            point_on_range.append((EP[0], EP[1]))
        point_in_range.extend(point_on_range)
        # 境界内でTINを再作成
        Points_in_range = np.array(point_in_range)
        tri_in_range = Delaunay(Points_in_range)
        # TINの構成を3角形ごとに抽出
        Volumes = []
        Component_in_range = Points_in_range[tri_in_range.simplices]
        for i in range(len(Component_in_range)):
            tri_point = Component_in_range[i]
            tri_points = []
            for j in range(len(tri_point)):
                point_0 = tri_point[j]
                point_x = point_0[0]
                point_y = point_0[1]
                for k in range(len(coordinates)):
                    CP = coordinates[k]
                    if CP[0] == point_x and CP[1] == point_y:
                        point_z = CP[2]
                        break
                tri_points.append([point_x, point_y, point_z])
            P1 = tri_points[0]
            P2 = tri_points[1]
            P3 = tri_points[2]
            L1 = self.get_Length(P1, P2)
            L2 = self.get_Length(P2, P3)
            L3 = self.get_Length(P3, P1)
            S = self.HeronFormula(L1, L2, L3)
            V = S * (P1[2] + P2[2] + P3[2]) / 3.0
            Volumes.append(V)


        Volume = np.sum(Volumes)

        return Volume



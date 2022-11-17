import pytest
import os
import json

def test_001():

    from src.dataInput import dataInput
    from src.calcrate import FrameCalc


    # 入力データを読み込む
    folder_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    int_file_path = os.path.join(folder_path, 'example_files/min_test.json')
    f = open(int_file_path, encoding="utf-8")
    fstr = f.read()  # ファイル終端まで全て読んだデータを返す
    f.close()
    inp = dataInput()
    inp.setJSONString(fstr)

    # 計算する
    out_text = FrameCalc(inp).calcrate()

    # 結果を返送する
    out_file_path = os.path.join(folder_path, 'example_files/min_test.out.json')
    fout=open(out_file_path, 'w')
    print(out_text, file=fout)
    fout.close()
    exit()


if __name__ == "__main__": 
    import sys
    sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../"))
    import conftest

    test_001()
import pytest
import json

def test_001():

    # from src.calcrate import FrameCalc
    from src.dataInput import dataInput
    # from src.usage import usage


    # 入力データを読み込む
    f = open('./example_files/test.json', encoding="utf-8")
    fstr = f.read()  # ファイル終端まで全て読んだデータを返す
    f.close()
    inp = dataInput()
    inp.setJSONString(fstr)

    #calc = FrameCalc(inp)

    # ユーザーチェック
    # user = usage(inp.production)
    # error = user.checkUser(inp)
    # if error != None:
    #     test_out_json(json.dumps({'error': error['message']}))


    # 計算開始
    #error, result = calc.calcrate()
    # if error != None:
    #     test_out_json(json.dumps({'error': error}))

    # # 使用量を計算する
    # for key in result:
    #     re = result[key]
    #     user.deduct_points += re['size']

    # result['old_points'] = user.old_points
    # result['deduct_points'] = user.deduct_points
    # result['new_points'] = user.writeFirestore()


    # 結果を返送する
    # out_text = json.dumps(result)
    # fout=open('./example_files/test.out.json', 'w')
    # print(out_text, file=fout)
    # fout.close()
    # exit()


if __name__ == "__main__": 
    import sys 
    import os
    sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../"))
    import conftest

    test_001()
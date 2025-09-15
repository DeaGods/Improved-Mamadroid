# coding=utf-8
"""
主流程脚本：
1. 将APK文件通过androguard转换为GML调用图
2. 将GML文件转换为TXT格式调用关系
3. 对TXT文件进行抽象，生成class、family、package层次的文件
"""
import os
import abstractGraph
import apk2graph
import gml2txt
import time
import traceback
import gc

def main():
    # 路径配置
    apk_dir = r"G:\无用\google_resstringencryption_apk"
    gml_dir = os.path.join(os.getcwd(), "gml")
    txt_dir = os.path.join(os.getcwd(), "txt", "benign")
    num = 0  # 成功处理计数器

    # 创建输出目录
    os.makedirs(gml_dir, exist_ok=True)
    os.makedirs(txt_dir, exist_ok=True)

    # 步骤1：APK转GML
    if not os.path.exists(apk_dir):
        print(f"错误：APK目录不存在 - {apk_dir}")
        return

    for filename in os.listdir(apk_dir):
        apk_path = os.path.join(apk_dir, filename)
        # 仅处理APK文件
        if not os.path.isfile(apk_path) or not filename.endswith(".apk"):
            continue

        # 转换并保存GML
        gml_filename = f"{os.path.splitext(filename)[0]}.gml"
        gml_path = os.path.join(gml_dir, gml_filename)
        try:
            apk2graph.extractcg(apk_path, gml_path)
        except Exception:
            traceback.print_exc()

    # 步骤2：GML转TXT
    if not os.path.exists(gml_dir):
        print(f"错误：GML目录不存在 - {gml_dir}")
        return

    for gmlname in os.listdir(gml_dir):
        g = None
        edgelist = None
        gml_path = os.path.join(gml_dir, gmlname)
        # 仅处理GML文件
        if not os.path.isfile(gml_path) or not gmlname.endswith(".gml"):
            continue

        # 跳过已处理或空文件
        txt_filename = f"{os.path.splitext(gmlname)[0]}.txt"
        storepath = os.path.join(txt_dir, txt_filename)
        if os.path.exists(storepath) or os.path.getsize(gml_path) == 0:
            continue

        # 转换并保存TXT
        try:
            g, edgelist = gml2txt.gml2graph(gml_path)
            gml2txt.caller2callee(edgelist, g.vs, storepath)
        except Exception:
            traceback.print_exc()
        finally:
            # 释放内存
            if g is not None:
                del g
            if edgelist is not None:
                del edgelist
            gc.collect()

    # 步骤3：抽象图处理
    if not os.path.exists(txt_dir):
        print(f"错误：TXT目录不存在 - {txt_dir}")
        return

    logfile = os.path.join(os.getcwd(), "log.txt")
    with open(logfile, 'w') as log:
        for txtname in os.listdir(txt_dir):
            txtpath = os.path.join(txt_dir, txtname)
            if not os.path.isfile(txtpath) or not txtname.endswith(".txt"):
                continue

            try:
                abstractGraph._preprocess_graph(txtpath, os.getcwd())
                log.write(f"{txtname.rpartition('.')[0]}.apk is abstracted\n")
                num += 1
            except Exception:
                traceback.print_exc()
        log.write(f"{num} apks have done")

if __name__ == "__main__":
    time_start = time.time()
    main()
    print(f"总耗时: {time.time() - time_start} 秒")
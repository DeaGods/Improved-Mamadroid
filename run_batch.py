# coding=utf-8
'''
run_batch.py 脚本功能：
循环调用 mamadroid.py，显示其内部打印语句，跳过已处理文件
'''

import os
import subprocess
import time
import argparse

def get_processed_gmls(txt_dir):
    """获取已处理过的GML文件名（通过TXT文件反推）"""
    processed = set()
    if not os.path.exists(txt_dir):
        return processed
    
    for txt_file in os.listdir(txt_dir):
        if txt_file.endswith(".txt"):
            gml_name = os.path.splitext(txt_file)[0] + ".gml"
            processed.add(gml_name)
    return processed

def get_unprocessed_gmls(gml_dir, processed_gmls):
    """获取未处理的GML文件列表"""
    if not os.path.exists(gml_dir):
        return []
    
    all_gmls = [f for f in os.listdir(gml_dir) 
               if f.endswith(".gml") and os.path.isfile(os.path.join(gml_dir, f))]
    return [gml for gml in all_gmls if gml not in processed_gmls]

def run_gml2txt_batch(gml_dir, txt_dir, interval=30):
    """循环处理未转换为TXT的GML文件，显示mamadroid.py的打印输出"""
    while True:
        try:
            processed_gmls = get_processed_gmls(txt_dir)
            print(f"当前已处理GML数量: {len(processed_gmls)}")

            unprocessed_gmls = get_unprocessed_gmls(gml_dir, processed_gmls)
            unprocessed_count = len(unprocessed_gmls)

            if not unprocessed_gmls:
                print("所有GML文件已处理完毕，等待新文件...")
                time.sleep(interval)
                continue

            print(f"发现{unprocessed_count}个未处理GML，开始处理本轮...")

            # 关键修改：不捕获输出，让mamadroid.py的打印直接显示在控制台
            # 或使用 stdout=subprocess.STDOUT 将stderr合并到stdout显示
            result = subprocess.run(
                ["python", "mamadroid.py"],
                # 移除 capture_output=True，默认输出到控制台
                check=True  # 若mamadroid.py执行出错（返回非0状态码），会抛出异常
            )

            print(f"本轮处理完成，等待{interval}秒后检查新文件...")
            time.sleep(interval)

        except subprocess.CalledProcessError as e:
            print(f"mamadroid.py执行出错，返回码：{e.returncode}")
        except Exception as e:
            print(f"处理过程出错: {str(e)}")
            print("等待恢复后继续...")
            time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量处理GML转TXT，显示内部打印")
    parser.add_argument("--gml_dir", default=os.path.join(os.getcwd(), "gml"), 
                      help="GML文件存储目录")
    parser.add_argument("--txt_dir", default=os.path.join(os.getcwd(), "txt", "malware"), 
                      help="TXT文件存储目录")
    parser.add_argument("--interval", type=int, default=30, 
                      help="循环检查间隔时间(秒)")
    args = parser.parse_args()

    os.makedirs(args.gml_dir, exist_ok=True)
    os.makedirs(args.txt_dir, exist_ok=True)

    run_gml2txt_batch(args.gml_dir, args.txt_dir, args.interval)
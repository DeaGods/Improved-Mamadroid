#coding=utf-8
import numpy
import sys
import Markov as mk
import os
from time import time
import gc

# 初始化变量
PACKETS = []  # 存储状态列表
WHICHCLASS = "Packages"  # 处理类型标识
wf = "Y"  # 文件读取模式标识
appslist = None
dbs = None

# 读取状态列表文件，构建节点列表
with open(f"{WHICHCLASS}.txt", encoding='utf-8') as packseq:
    for line in packseq:
        PACKETS.append(line.replace('\n', ''))
allnodes = PACKETS.copy()
allnodes.extend(['self-defined', 'obfuscated'])  # 补充特殊节点

# 构建输出CSV表头（文件名 + 所有节点间的转移关系）
Header = ['filename']
for i in range(len(allnodes)):
    for j in range(len(allnodes)):
        Header.append(f"{allnodes[i]}To{allnodes[j]}")

# 初始化变量
Fintime = []  # 存储处理时间
dbcounter = 0
numApps = [f for f in os.listdir('package/') if os.path.isfile(os.path.join('package', f))]
leng = len(numApps)

# 检查输入文件是否存在
if leng == 0:
    sys.exit("错误：package文件夹中未找到任何文件！")

# 确保输出目录存在
os.makedirs(f'Features/{WHICHCLASS}', exist_ok=True)

# 写入结果到CSV
FLUSH_INTERVAL = 200  # 刷新缓冲区间隔
write_counter = 0      # 写入计数器
with open(f'Features/{WHICHCLASS}/result.csv', 'w', encoding='utf-8', newline='') as f:
    # 写入表头
    f.write(','.join(map(str, Header)) + '\n')
    f.flush()
    
    # 遍历处理每个文件
    for i in range(leng):
        current_file = numApps[i]
        specificapp = None
        
        # 读取文件内容
        try:
            if wf == 'Y':
                with open(f'package/{current_file}', encoding='utf-8') as callseq:
                    specificapp = [line.rstrip('\n') for line in callseq]
            else:
                specificapp = [line for line in dbs[dbcounter][i]]
        except Exception:
            continue  # 跳过读取失败的文件
        
        # 计算马尔可夫矩阵并写入结果
        try:
            start_time = time()
            # 生成马尔可夫转移矩阵
            mark_mat = mk.main(specificapp, allnodes, wf)
            # 构建结果行（文件名 + 矩阵数据）
            mark_row = [current_file] if wf == 'Y' else [appslist[dbcounter][i]]
            for row in mark_mat:
                mark_row.extend(map(str, row))
            
            # 写入行数据
            f.write(','.join(mark_row) + '\n')
            write_counter += 1
            
            # 定期刷新缓冲区
            if write_counter % FLUSH_INTERVAL == 0:
                f.flush()
            
            Fintime.append(time() - start_time)
        except Exception:
            continue  # 跳过处理失败的文件
        
        # 释放内存
        del specificapp, mark_mat, mark_row
        gc.collect()
    
    # 最终刷新缓冲区
    f.flush()

dbcounter += 1

# 输出处理统计信息
if Fintime:
    print("\n处理统计:")
    print(f"- 成功处理文件数: {len(Fintime)}")
    print(f"- 平均处理时间: {numpy.mean(Fintime):.4f} 秒/文件")
    print(f"- 总处理时间: {numpy.sum(Fintime):.4f} 秒")
else:
    print("\n警告：未成功处理任何文件！")
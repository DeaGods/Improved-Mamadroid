#coding=utf-8
"""将family文件夹中的文件转换为马尔可夫矩阵，结果保存到Features/Families"""
import numpy
import sys
import Markov as mk
import os
from time import time

# 初始化变量
PACKETS = []  # 存储家族列表
WHICHCLASS = "Families"  # 处理类型标识
wf = "Y"  # 文件读取模式标识
appslist = None
dbs = None

# 读取家族列表，构建节点列表
with open("Families.txt", encoding='utf-8') as packseq:
    for line in packseq:
        PACKETS.append(line.replace('\n', ''))
allnodes = PACKETS
allnodes.extend(['self-defined', 'obfuscated'])  # 补充特殊节点

# 构建输出CSV表头（文件名 + 所有节点间的转移关系）
Header = ['filename']
for i in range(len(allnodes)):
    for j in range(len(allnodes)):
        Header.append(f"{allnodes[i]}To{allnodes[j]}")

# 初始化变量
Fintime = []  # 存储处理时间
dbcounter = 0
numApps = os.listdir('family/')
DatabaseRes = [Header]  # 结果集（含表头）
leng = len(numApps)

# 处理每个文件
for i in range(leng):
    try:
        # 读取文件内容
        if wf == 'Y':
            with open(f'family/{numApps[i]}', encoding='utf-8') as callseq:
                specificapp = [line.replace('\n', '') for line in callseq]
        else:
            specificapp = [line for line in dbs[dbcounter][i]]

        # 计算马尔可夫矩阵
        start_time = time()
        mark_mat = mk.main(specificapp, allnodes, wf)

        # 构建结果行
        mark_row = [numApps[i]] if wf == 'Y' else [appslist[dbcounter][i]]
        for row in mark_mat:
            mark_row.extend(row)

        DatabaseRes.append(mark_row)
        Fintime.append(time() - start_time)
    except Exception:
        continue  # 跳过处理失败的文件

dbcounter += 1

# 保存结果到CSV
os.makedirs(f'Features/{WHICHCLASS}', exist_ok=True)
with open(f'Features/{WHICHCLASS}/result.csv', 'w', encoding='utf-8') as f:
    for line in DatabaseRes:
        f.write(str(line) + '\n')
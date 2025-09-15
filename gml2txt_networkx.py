#coding=utf-8
"""将GML格式的调用图转换为TXT格式的调用关系"""
import sys
import os
import networkx as nx
import parse
from collections import defaultdict
import gc


def caller2callee(edgelist, nodes, filename):
    """
    将边列表转换为调用关系并写入TXT文件
    :param edgelist: 边列表（节点ID对）
    :param nodes: 节点属性字典
    :param filename: 输出TXT文件路径
    """
    edgesname = defaultdict(list)
    # 提取节点标签并构建调用关系
    for k, v in edgelist:
        edgesname[parse.parse_label(nodes[k]["label"])].append(parse.parse_label(nodes[v]["label"]) + "\n")
    
    # 写入文件
    with open(filename, 'w', encoding='utf-8') as out:
        for node in edgesname:
            out.write(f"{node} ==> {edgesname[node]}\n")
    
    # 释放内存
    edgesname.clear()


def gml2graph(gmlpath):
    """
    读取GML文件并解析为图对象和边列表
    :param gmlpath: GML文件路径
    :return: 图对象、边列表
    """
    g = None
    try:
        g = nx.read_gml(gmlpath)
        return g, list(g.edges())  # 边列表为节点ID元组列表
    finally:
        # 确保资源释放
        if g is not None:
            del g
            gc.collect()


if __name__ == '__main__':
    gmlpath = "1.gml"
    g, edgelist = gml2graph(gmlpath)
    caller2callee(edgelist, g.nodes, "1.txt")
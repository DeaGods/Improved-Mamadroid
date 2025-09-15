#coding=utf-8
"""将API调用抽象为class、family、package三个层次"""
import os
from multiprocessing import Process

def _preprocess_graph(app, _dir):
    """预处理调用图TXT，提取caller和callee并生成临时文件"""
    app_basename = os.path.basename(app)
    temp_file = f"{app_basename}"  # 临时文件存储提取的调用关系

    # 提取caller和callee到临时文件
    with open(temp_file, 'w') as fp:
        with open(app) as fh:
            for lines in fh:
                lines = lines.strip()
                if not lines or " ==> " not in lines:
                    continue  # 跳过空行或格式错误行

                # 分割调用者和被调用者
                caller_part, callee_part = lines.split(" ==> ", 1)
                caller = caller_part.split(":")[0].replace("<", "").strip()
                if not caller:
                    continue

                # 解析被调用者列表
                callee = []
                if "," in callee_part:
                    for sub in callee_part.split("\\n',"):
                        cleaned = sub.split(":")[0].replace("['<", "").replace("'<", "").strip()
                        if cleaned:
                            callee.append(cleaned)
                else:
                    cleaned = callee_part.split(":")[0].replace("['<", "").replace("'<", "").strip()
                    if cleaned:
                        callee.append(cleaned)

                # 写入临时文件（caller + 多个callee，用制表符分隔）
                if callee:
                    fp.write(caller + "\t")
                    fp.write("\t".join(callee) + "\n")

    # 执行抽象处理并清理临时文件
    selfDefined(temp_file, _dir)
    os.remove(temp_file)

def selfDefined(f, _dir):
    """加载白名单并启动多进程执行抽象"""
    # 加载包、家族、类的白名单
    with open("Packages.txt") as fh:
        Package = [l.strip('\n').lstrip('.') if l.startswith('.') else l.strip('\n').strip() for l in fh]
    with open("Families.txt") as fh:
        Family = [l.strip('\n').strip() for l in fh]
    with open("classes.txt") as fh:
        Class = [l.strip('\n').strip() for l in fh]

    # 先抽象为class，再并行抽象为family和package
    class_file = abstractToClass(Class, f, _dir)
    Package.reverse()  # 包名匹配优先级调整

    # 多进程处理
    p_family = Process(target=abstractToMode, args=(Family, class_file, _dir))
    p_package = Process(target=abstractToMode, args=(Package, class_file, _dir))
    p_family.start()
    p_package.start()
    p_package.join()

def _repeat_function(lines, whitelist, fh, sep):
    """根据白名单匹配规则，将调用转换为抽象标识"""
    line = lines.strip()
    if line in whitelist:
        fh.write(line + sep)
        return

    # 特殊格式处理
    if "junit." in line:
        return
    if '$' in line:
        if line.replace('$', '.') in whitelist:
            fh.write(line.replace('$', '.') + sep)
            return
        elif line.split('$')[0] in whitelist:
            fh.write(line.split('$')[0] + sep)
            return

    # 混淆判断（短字符占比过高）
    items = line.split('.')
    short_count = sum(1 for item in items if len(item) < 3)
    if short_count > len(items) / 2:
        fh.write("obfuscated" + sep)
    else:
        fh.write("self-defined" + sep)

def abstractToClass(class_whitelist, app, _dir):
    """将调用关系抽象为class层次"""
    class_dir = os.path.join(_dir, "class")
    os.makedirs(class_dir, exist_ok=True)
    app_filename = os.path.basename(app)
    output_file = os.path.join(class_dir, app_filename)

    # 写入class抽象结果
    with open(output_file, 'w') as fh:
        with open(app) as fp:
            for line in fp:
                parts = [p for p in line.strip('\n').split('\t') if len(p) > 1]
                if not parts:
                    continue
                # 逐个处理调用组件并写入
                for i, part in enumerate(parts):
                    sep = "\t" if i < len(parts) - 1 else "\n"
                    _repeat_function(part, class_whitelist, fh, sep)
    return output_file

def abstractToMode(whitelist, app, _dir):
    """将class抽象结果进一步转换为family或package层次"""
    # 家族/包标识及路径配置
    dico = {"org.xml": 'xml', "com.google":'google', "javax": 'javax', "java": 'java', 
            "org.w3c.dom": 'dom', "org.json": 'json', "org.apache": 'apache', 
            "android": 'android', "dalvik": 'dalvik'}
    is_family = len(whitelist) <= 15  # 家族白名单较短

    # 输出路径
    if is_family:
        output_dir = os.path.join(_dir, "family")
    else:
        output_dir = os.path.join(_dir, "package")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, os.path.basename(app))

    # 写入抽象结果
    with open(output_file, 'w') as fh:
        with open(app) as fp:
            for line in fp:
                parts = line.strip('\n').split('\t')
                for part in parts:
                    if "obfuscated" in part or "self-defined" in part:
                        fh.write(part + '\t')
                        continue
                    # 匹配白名单并写入对应标识
                    for item in whitelist:
                        if part.startswith(item):
                            fh.write(dico[item] + '\t' if is_family else item + '\t')
                            break
                fh.write('\n')

if __name__ == "__main__":
    _preprocess_graph(app="./1.txt", _dir="./output")#更改为自己实际的地址和目录
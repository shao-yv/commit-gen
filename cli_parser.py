import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='生成规范的 Git 提交信息')
    parser.add_argument('-p', '--path', default='.', help='Git 仓库路径（默认为当前目录）')
    parser.add_argument('-s', '--stage', action='store_true', help='读取暂存区变更（git diff --cached）')
    return parser.parse_args()
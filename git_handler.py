import git

def get_diff(repo_path=".", staged=False):
    """
    获取指定仓库的 diff
    :param repo_path: Git 仓库路径
    :param staged: 是否读取暂存区（True: git diff --cached, False: git diff）
    :return: diff 文本，失败返回 None
    """
    try:
        repo = git.Repo(repo_path)
        if staged:
            diff = repo.git.diff('--cached')
        else:
            diff = repo.git.diff()
        return diff
    except Exception as e:
        print(f"读取 Git 仓库失败：{e}")
        return None
def build_prompt(diff, extra_info=None):
    """
    构建发送给 LLM 的提示词
    :param diff: git diff 文本
    :param extra_info: 额外的信息字典（如克隆检测结果），可选
    :return: 完整提示词字符串
    """
    base_prompt = f"根据以下代码变更，生成规范的 Git 提交信息：\n\n{diff}"
    if extra_info and extra_info.get('clone_info'):
        base_prompt += f"\n\n额外信息：{extra_info['clone_info']}"
    return base_prompt
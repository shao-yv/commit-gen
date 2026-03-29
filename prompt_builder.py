def build_prompt(diff, extra_info=None):
    base_prompt = f"根据以下代码变更，生成规范的 Git 提交信息：\n\n{diff}"
    if extra_info and extra_info.get('examples'):
        base_prompt += f"\n\n参考以下历史提交示例（注意格式和风格）：\n{extra_info['examples']}"
    return base_prompt
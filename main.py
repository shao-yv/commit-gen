import sys
import git_handler
import preprocessor
import prompt_builder
import llm_client
import cli_parser

def main():
    args = cli_parser.parse_args()
    diff = git_handler.get_diff(repo_path=args.path, staged=args.stage)
    if not diff:
        print("没有未提交的变更，或无法读取变更。")
        sys.exit(0)

    print("正在分析代码变更...")
    extra = preprocessor.analyze(diff)
    prompt = prompt_builder.build_prompt(diff, extra)
    msg = llm_client.generate(prompt)
    if msg:
        print("\n生成的提交信息：")
        print(msg)
        if "AI 服务暂时不可用" in msg:
            print("（注意：由于 AI 服务暂时不可用，以上为降级方案生成的通用提交信息。）")
    else:
        print("生成失败。")

if __name__ == "__main__":
    main()
# 智能 Git 提交信息生成器

基于大语言模型的命令行工具，自动读取 Git 仓库变更，生成符合 [Conventional Commits](https://www.conventionalcommits.org/) 规范的提交信息。

## ✨ 功能特性

- 🔍 自动读取 Git 工作区或暂存区变更（`git diff` / `git diff --cached`）
- 🤖 调用大模型 API（支持硅基流动平台）生成提交信息
- 🛠 命令行参数支持：
  - `-p / --path`：指定 Git 仓库路径
  - `-s / --stage`：读取暂存区变更（默认工作区）
- 🛡 健壮的错误处理与重试机制（默认重试3次）
- 🧩 降级方案：API 不可用时返回通用提交信息，保证流程不中断
- 🔐 环境变量安全存储 API Key

## 📦 安装与使用

### 环境要求
- Python 3.8+
- Git

### 安装依赖
```bash
pip install GitPython openai python-dotenv
```

### 配置 API Key
1.注册 硅基流动 账号，获取 API Key。

2.在项目根目录创建 .env 文件，内容如下：
```text
SILICONFLOW_API_KEY=sk-你的真实Key
```
3.确保 .env 已加入 .gitignore，避免泄露。

### 基本用法
```bash
# 查看帮助
python commit_gen.py -h

# 分析当前目录 Git 仓库的工作区变更
python commit_gen.py

# 分析指定仓库的暂存区变更
python commit_gen.py -p /path/to/repo -s
```

## 📝 命令行参数
| 参数    | 简写 | 说明                          |
| ------- | ---- | ----------------------------- |
| --path  | -p   | Git 仓库路径（默认为当前目录）|
| --stage | -s   | 读取暂存区变更（git diff --cached） |
| --help  | -h   | 显示帮助信息                  |
## 🧪 示例
假设你在 E:\项目计划 中修改了 example.py 并暂存：

```bash
git add example.py
python commit_gen.py -s
```
输出类似：

```
正在分析代码变更...

生成的提交信息：
feat(example): 更新示例文件内容
```
若 API 服务异常，则输出降级信息：
```
chore: 更新代码（AI 服务暂时不可用，请手动补充说明）
```

## 🛠 技术栈
- Python 3.13

- GitPython（Git 交互）

- OpenAI SDK（API 调用，兼容硅基流动）

- python-dotenv（环境变量管理）

- argparse（命令行参数解析）

## 📁 项目结构
```
.
├── commit_gen.py          # 主程序
├── .env                   # API Key（不提交）
├── .gitignore             # 忽略敏感文件
├── 项目计划.md            # 项目规划
├── DEVLOG.md              # 开发日志
└── README.md              # 项目说明
```
## 📄 项目成果
- 软件著作权：申请中（待提交）

- 学术论文：撰写中

- 考研复试：展示软件工程实践与科研潜力

## 📮 反馈与联系
如有问题或建议，欢迎提交 Issue 或联系作者：
GitHub: shao-yv

## 📜 许可证
本项目采用 MIT 许可证。

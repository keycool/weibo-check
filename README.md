# 微博热搜分析

基于微博、抖音、微信热搜的产品创意分析工具，使用AI对热点话题进行评分和创意生成。

## 在线预览

报告实时发布在 GitHub Pages：https://keycool.github.io/weibo-check/

![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?style=flat-square)
![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-green?style=flat-square)

## 功能特点

- **多平台支持**: 微博、抖音、微信热搜数据获取
- **AI智能分析**: 使用 Claude/智谱AI 对热搜话题进行多维度评分
- **产品创意生成**: 为每个话题生成创新的产品概念
- **可视化报告**: 生成精美的交互式 HTML 分析报告
- **自动化部署**: GitHub Actions 每日自动更新
- **索引页面**: GitHub Pages 展示各平台最新报告

## 快速开始

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/keycool/weibo-check.git
cd weibo-check

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API 密钥
cp config/config.example.yaml config/config.yaml
# 编辑 config.yaml 或设置环境变量
export TIANAPI_KEY=your_api_key
export ANTHROPIC_API_KEY=your_anthropic_key

# 4. 运行分析
python -m src.fetch_weibo
python -m src.analyze_with_claude

# 5. 生成索引页面
python src/generate_index.py
```

### GitHub Actions (自动)

1. Fork 本仓库
2. 在 Settings → Secrets and variables → Actions 中添加:
   - `TIANAPI_KEY`: 天API密钥
   - `ANTHROPIC_API_KEY`: Claude/智谱AI密钥
3. 启用 GitHub Pages (Settings → Pages → gh-pages branch)
4. 在 Actions 中手动触发 workflow 或等待定时任务

## 目录结构

```
weibo-check/
├── .github/
│   └── workflows/
│       └── weibo-analysis.yml    # GitHub Actions 工作流
├── .claude/
│   └── commands/
│       └── weibo-trends-analyzer.md
├── config/
│   ├── config.yaml
│   └── config.example.yaml
├── data/                          # 数据和报告目录
│   ├── *_raw_*.json              # 原始API数据
│   ├── *_analysis_*.json         # 分析结果
│   ├── *_analysis_*.html         # HTML报告
│   └── index.html                # 索引页面
├── docs/
│   ├── README.md
│   ├── INSTALLATION.md
│   └── CONFIGURATION.md
├── src/
│   ├── __init__.py
│   ├── fetch_weibo.py            # 数据获取
│   ├── analyze_with_claude.py    # AI分析
│   ├── analyze_trends.py         # 多平台分析
│   ├── config_loader.py          # 配置管理
│   ├── path_utils.py             # 路径工具
│   └── generate_index.py         # 索引生成
├── requirements.txt
├── SKILL.md                      # 项目模式文档
└── README.md
```

## 工作流程

```
1. 数据获取 → data/{source}_raw_{timestamp}.json
2. AI分析   → data/{source}_analysis_{timestamp}.json
3. HTML报告 → data/{source}_analysis_{timestamp}.html
4. 索引生成 → data/index.html
5. 部署     → GitHub Pages
```

## 评分标准

每话题满分100分：

- **有趣度 (80分)**: 新颖性、情感共鸣、传播潜力、娱乐价值
- **有用度 (20分)**: 实用价值、市场潜力

## 配置

| 环境变量 | 说明 | 必需 |
|---------|------|------|
| `TIANAPI_KEY` | 天API密钥 | 是 |
| `ANTHROPIC_API_KEY` | Claude/智谱AI密钥 | 是 |
| `MODEL_ID` | AI模型 (默认: glm-4) | 否 |

详细配置说明见 [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

## 技术栈

- **Python 3.11+**: 主要开发语言
- **Anthropic SDK**: Claude AI 集成
- **Requests**: HTTP 请求
- **PyYAML**: 配置管理
- **GitHub Actions**: 自动化工作流
- **GitHub Pages**: 静态页面托管

## 许可证

MIT License

## 作者

- GitHub: [@keycool](https://github.com/keycool)

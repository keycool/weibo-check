# 微博热搜分析Skill

基于微博热搜话题的产品创意分析工具，使用AI对热点话题进行评分和创意生成。

## 功能特点

- 📊 **自动数据获取**: 从天API获取最新微博热搜数据
- 🤖 **AI智能分析**: 使用Claude对热搜话题进行多维度评分
- 💡 **产品创意生成**: 为每个话题生成创新的产品概念
- 📈 **可视化报告**: 生成交互式HTML分析报告
- ⚙️ **灵活配置**: 支持配置文件和环境变量
- 🌐 **跨平台**: 支持Windows、macOS、Linux

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 方式1: 环境变量（推荐）
export TIANAPI_KEY=your_api_key_here

# 方式2: 配置文件
# 编辑 config/config.yaml，设置 api.tianapi.key
```

### 3. 运行分析

在Claude Code中执行：

```
/weibo-trends-analyzer
```

或手动执行：

```bash
# 获取热搜数据
python -m src.fetch_weibo

# 然后使用Claude分析数据并生成报告
```

## 目录结构

```
微博热搜分析的Skills/
├── .claude/
│   └── commands/
│       └── weibo-trends-analyzer.md   # 技能命令定义
├── config/
│   ├── config.yaml                    # 配置文件
│   └── config.example.yaml            # 配置模板
├── src/
│   ├── __init__.py
│   ├── fetch_weibo.py                 # 数据获取脚本
│   ├── config_loader.py               # 配置加载器
│   └── path_utils.py                  # 路径管理工具
├── docs/
│   ├── README.md                      # 本文档
│   ├── INSTALLATION.md                # 安装指南
│   └── CONFIGURATION.md               # 配置说明
├── data/                              # 数据存储目录
├── requirements.txt                   # Python依赖
└── version.txt                        # 版本号
```

## 工作流程

1. **数据获取**: `fetch_weibo.py` 从天API获取微博热搜
2. **配置加载**: 从 `config.yaml` 加载分析参数
3. **AI分析**: Claude对每个话题进行评分和创意生成
4. **报告生成**: 生成交互式HTML报告

## 评分标准

每话题满分100分：

- **有趣度 (80分)**: 新颖性、情感共鸣、传播潜力、娱乐价值
- **有用度 (20分)**: 实用价值、市场潜力

## 配置

主要配置文件: `config/config.yaml`

```yaml
analysis:
  topic_count: 20          # 分析话题数量

api:
  tianapi:
    key: ""                # API密钥（推荐使用环境变量）
```

详细配置说明请参考 [CONFIGURATION.md](CONFIGURATION.md)

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `TIANAPI_KEY` | 天API密钥 |
| `WEIBO_SKILL_TOPIC_COUNT` | 分析话题数量 |
| `WEIBO_SKILL_DATA_DIR` | 数据目录 |
| `WEIBO_SKILL_LOG_LEVEL` | 日志级别 |

## 版本

当前版本: 1.0.0

## 许可证

MIT License

## 支持

如有问题或建议，请查看 [CONFIGURATION.md](CONFIGURATION.md) 中的故障排除部分。

# 配置说明

本文档详细说明微博热搜分析Skill的配置选项。

## 配置文件位置

主配置文件: `config/config.yaml`

配置模板: `config/config.example.yaml`

## 配置优先级

```
命令行参数 > 环境变量 > config.yaml > 代码默认值
```

## 配置项详解

### API配置 (api)

```yaml
api:
  tianapi:
    base_url: "https://apis.tianapi.com/weibohot/index"
    timeout: 30          # 请求超时时间（秒）
    max_retries: 3       # 最大重试次数
    key: ""              # API密钥（推荐使用环境变量TIANAPI_KEY）
```

**环境变量覆盖**:
- `TIANAPI_KEY`: 覆盖 `api.tianapi.key`

### 分析配置 (analysis)

```yaml
analysis:
  topic_count: 20                    # 分析话题数量
  enable_web_search: true            # 是否启用WebSearch
  search_delay: 2                    # WebSearch请求间隔（秒）
  scoring:
    interesting: 80                  # 有趣度总分
    useful: 20                       # 有用度总分
    interesting_detail:
      novelty: 20                    # 新颖性
      resonance: 20                  # 情感共鸣
      viral: 20                      # 传播潜力
      entertainment: 20              # 娱乐价值
    useful_detail:
      practical: 10                  # 实用价值
      market: 10                     # 市场潜力
```

**环境变量覆盖**:
- `WEIBO_SKILL_TOPIC_COUNT`: 覆盖 `topic_count`

### 路径配置 (paths)

```yaml
paths:
  data_dir: "data"                                           # 数据目录
  raw_filename_format: "weibo_raw_{timestamp}.json"          # 原始数据文件名格式
  report_filename_format: "weibo_analysis_{timestamp}.html"  # 报告文件名格式
  timestamp_format: "%Y%m%d_%H%M%S"                          # 时间戳格式
```

**环境变量覆盖**:
- `WEIBO_SKILL_DATA_DIR`: 覆盖 `data_dir`

**说明**:
- 所有路径都相对于项目根目录
- `{timestamp}` 会被自动替换为实际时间戳
- 时间戳格式遵循Python strftime规范

### 输出配置 (output)

```yaml
output:
  json_indent: 2                           # JSON缩进空格数
  encoding: "utf-8"                        # 文件编码
  save_intermediate: true                  # 是否保存中间结果
  intermediate_filename: "weibo_analysis_{timestamp}.json"
```

### 日志配置 (logging)

```yaml
logging:
  level: "INFO"                           # 日志级别
  file: "logs/skill.log"                  # 日志文件路径
  console: true                           # 是否输出到控制台
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**环境变量覆盖**:
- `WEIBO_SKILL_LOG_LEVEL`: 覆盖 `level`

**日志级别**: DEBUG, INFO, WARNING, ERROR

### HTML报告配置 (html)

```yaml
html:
  title: "微博热搜产品创意分析"            # 报告标题
  theme: "dark"                           # 主题: dark, light, auto
  enable_animation: true                  # 启用动画
  enable_search: true                     # 启用搜索
  enable_filter: true                     # 启用筛选
```

### 评分等级配置 (grades)

```yaml
grades:
  excellent: 80                           # 优秀分数线
  good: 60                                # 良好分数线
  average: 0                              # 普通分数线（以下）
```

## 命令行参数

```bash
python -m src.fetch_weibo [选项]
```

可用选项：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config PATH` | 指定配置文件 | config/config.yaml |
| `--api-key KEY` | 指定API密钥 | 从配置/环境变量读取 |
| `--output PATH` | 指定输出目录 | 从配置读取 |

## 配置示例

### 示例1: 基本配置

```yaml
# config/config.yaml
api:
  tianapi:
    key: ""  # 使用环境变量 TIANAPI_KEY

analysis:
  topic_count: 20
```

### 示例2: 自定义评分

```yaml
analysis:
  topic_count: 30
  scoring:
    interesting: 70
    useful: 30
    interesting_detail:
      novelty: 25
      resonance: 20
      viral: 15
      entertainment: 10
```

### 示例3: 自定义输出路径

```yaml
paths:
  data_dir: "output/data"
  raw_filename_format: "hot_{timestamp}.json"
```

## 环境变量设置

### Linux/macOS

```bash
# 临时设置
export TIANAPI_KEY=your_key
export WEIBO_SKILL_TOPIC_COUNT=30

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export TIANAPI_KEY=your_key' >> ~/.bashrc
source ~/.bashrc
```

### Windows (CMD)

```cmd
# 临时设置
set TIANAPI_KEY=your_key

# 永久设置
setx TIANAPI_KEY "your_key"
```

### Windows (PowerShell)

```powershell
# 临时设置
$env:TIANAPI_KEY="your_key"

# 永久设置
[System.Environment]::SetEnvironmentVariable('TIANAPI_KEY', 'your_key', 'User')
```

## 配置验证

验证配置是否正确：

```bash
# 使用配置文件运行
python -m src.fetch_weibo --config config/config.yaml

# 检查环境变量
echo $TIANAPI_KEY  # Linux/macOS
echo %TIANAPI_KEY%  # Windows CMD
echo $env:TIANAPI_KEY  # Windows PowerShell
```

## 常见问题

### Q: 如何修改分析话题数量？

**A**: 有三种方式：
1. 编辑 `config.yaml`: `analysis.topic_count: 30`
2. 环境变量: `export WEIBO_SKILL_TOPIC_COUNT=30`
3. 暂不支持（数量在AI分析阶段使用）

### Q: API密钥在哪里设置？

**A**: 推荐使用环境变量：
```bash
export TIANAPI_KEY=your_key
```

或在配置文件中设置（不推荐）：
```yaml
api:
  tianapi:
    key: "your_key"
```

### Q: 如何更改输出目录？

**A**: 设置环境变量：
```bash
export WEIBO_SKILL_DATA_DIR=/custom/path
```

或编辑配置文件：
```yaml
paths:
  data_dir: "/custom/path"
```

### Q: 配置文件不生效？

**A**: 检查以下几点：
1. 文件路径是否正确
2. YAML语法是否正确（注意缩进）
3. 环境变量是否覆盖了配置
4. 运行 `python -m src.fetch_weibo --config config/config.yaml` 指定配置文件

## 更多信息

- [README.md](README.md) - 项目概述
- [INSTALLATION.md](INSTALLATION.md) - 安装指南

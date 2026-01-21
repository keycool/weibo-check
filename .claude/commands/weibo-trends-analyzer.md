# 微博热搜产品创意分析

执行完整的微博热搜分析流程，生成产品创意和HTML报告。

## 配置说明

该技能使用 `config/config.yaml` 进行配置管理。支持以下配置方式：
- **配置文件**: `config/config.yaml`（主要配置）
- **环境变量**: `TIANAPI_KEY`（API密钥）、`WEIBO_SKILL_*`（其他配置）

首次使用前请确保：
1. 安装依赖: `pip install -r requirements.txt`
2. 设置API密钥: `export TIANAPI_KEY=your_key_here`
   或在 `config/config.yaml` 中设置 `api.tianapi.key`

## 执行步骤

### 1. 获取最新热搜数据

执行Python脚本获取微博热搜（使用配置文件中的设置）：

```bash
# 方式1: 使用默认配置
python -m src.fetch_weibo

# 方式2: 指定配置文件
python -m src.fetch_weibo --config config/config.yaml

# 方式3: 命令行指定API密钥（覆盖配置）
python -m src.fetch_weibo --api-key YOUR_API_KEY

# 方式4: 指定输出目录（覆盖配置）
python -m src.fetch_weibo --output /custom/path
```

### 2. 读取配置

从 `config/config.yaml` 加载配置，包括：
- 分析话题数量 (`analysis.topic_count`)
- 评分权重 (`analysis.scoring`)
- 输出路径 (`paths.data_dir`)

### 3. 读取JSON数据

从data目录读取最新生成的JSON文件（文件名格式：`weibo_raw_YYYYMMDD_HHMMSS.json`）

### 4. 分析热搜话题

根据配置中的 `analysis.topic_count` 分析指定数量的热搜话题。

#### 评分标准（总分100分）

**有趣度（80分）**：
- 新颖性（20分）：话题的独特性和意外性
- 情感共鸣（20分）：公众参与度和情感投入
- 传播潜力（20分）：话题的可分享性
- 娱乐价值（20分）：趣味性和吸引力

**有用度（20分）**：
- 实用价值（10分）：是否解决实际问题
- 市场潜力（10分）：商业化和变现机会

#### 产品创意生成

为每个话题生成：
- **产品名称**：有创意、易记、与话题相关
- **核心功能**：3-5个关键功能点
- **目标用户**：用户画像、痛点、行为特征
- **价值主张**：用户采用理由和差异化优势

### 5. 生成HTML报告

创建包含以下内容的交互式HTML报告：

- 📊 汇总统计（总数、优秀、良好、普通）
- 🔍 实时搜索话题功能
- 🎯 按评分段筛选（优秀80+、良好60-80、普通<60）
- 📄 导出/打印功能
- 📱 响应式设计

报告样式根据配置中的 `grades` 设置：
- **优秀（80+分）**：绿色边框，突出显示
- **良好（60-80分）**：蓝色边框，标准显示
- **普通（<60分）**：灰色边框，淡化显示

### 6. 保存报告

将HTML报告保存到配置中指定的路径：
```
{paths.data_dir}/weibo_analysis_YYYYMMDD_HHMMSS.html
```
默认: `data/weibo_analysis_YYYYMMDD_HHMMSS.html`

### 7. 显示结果摘要

向用户展示：
- ✅ 分析完成的话题数量
- ✅ 各评分段的数量分布（优秀/良好/普通）
- ✅ Top 5 优秀话题列表
- ✅ HTML报告的保存路径

## 进度显示

在分析过程中显示进度：
- "正在分析第 X/{topic_count} 个话题：{标题}"
- "正在生成产品创意..."
- "正在生成HTML报告..."

## 配置优先级

```
命令行参数 > 环境变量 > config.yaml > 代码默认值
```

## 环境变量

- `TIANAPI_KEY`: 天API密钥（推荐使用此方式）
- `WEIBO_SKILL_TOPIC_COUNT`: 分析话题数量
- `WEIBO_SKILL_DATA_DIR`: 数据目录
- `WEIBO_SKILL_LOG_LEVEL`: 日志级别

## 注意事项

1. 分析话题数量由配置文件 `analysis.topic_count` 决定，默认20个
2. 评分要客观公正，有理有据
3. 产品创意要有创新性和可行性
4. HTML报告要美观、易读、交互友好
5. 所有文本使用UTF-8编码

## 故障排除

**问题**: API密钥错误
**解决**: 设置环境变量 `export TIANAPI_KEY=your_key` 或在配置文件中设置

**问题**: 模块未找到
**解决**: 确保从项目根目录运行，或使用 `python -m src.fetch_weibo`

**问题**: 配置文件不存在
**解决**: 复制 `config/config.example.yaml` 为 `config/config.yaml`

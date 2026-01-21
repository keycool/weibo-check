# 安装指南

本文档介绍如何安装和设置微博热搜分析Skill。

## 环境要求

- Python 3.7+
- pip (Python包管理器)
- 天API账号和API密钥

## 安装步骤

### 1. 克隆或下载项目

```bash
# 假设项目已存在于本地
cd "E:\vibe coding\CC\微博热搜分析的Skills"
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

依赖包括：
- `requests`: HTTP请求库
- `pyyaml`: YAML配置文件解析

### 3. 获取天API密钥

1. 访问 [天API官网](https://www.tianapi.com/)
2. 注册账号
3. 创建应用，选择"微博热搜"接口
4. 复制API密钥

### 4. 配置API密钥

**方式1: 环境变量（推荐）**

```bash
# Linux/macOS
export TIANAPI_KEY=your_api_key_here

# Windows (CMD)
set TIANAPI_KEY=your_api_key_here

# Windows (PowerShell)
$env:TIANAPI_KEY="your_api_key_here"
```

**方式2: 配置文件**

1. 复制配置模板：
```bash
cp config/config.example.yaml config/config.yaml
```

2. 编辑 `config/config.yaml`:
```yaml
api:
  tianapi:
    key: "your_api_key_here"
```

### 5. 验证安装

```bash
# 测试数据获取
python -m src.fetch_weibo
```

成功执行后，会在 `data/` 目录生成 `weibo_raw_YYYYMMDD_HHMMSS.json` 文件。

## 在Claude Code中使用

### 方式1: 使用Skill命令

在Claude Code对话中输入：
```
/weibo-trends-analyzer
```

### 方式2: 手动执行

1. 获取数据：
```bash
python -m src.fetch_weibo
```

2. 在Claude Code中分析数据并生成报告

## 故障排除

### 问题1: ModuleNotFoundError: No module named 'src'

**原因**: Python路径设置问题

**解决**:
```bash
# 使用 -m 参数从项目根目录运行
python -m src.fetch_weibo
```

### 问题2: API密钥错误

**原因**: API密钥未设置或无效

**解决**:
1. 检查环境变量: `echo $TIANAPI_KEY`
2. 检查配置文件: `config/config.yaml`
3. 验证API密钥是否有效

### 问题3: 网络连接超时

**原因**: 网络问题或API服务不可用

**解决**:
1. 检查网络连接
2. 增加超时时间: 编辑 `config.yaml` 中的 `api.tianapi.timeout`
3. 确认天API服务状态

### 问题4: 权限错误

**原因**: data目录权限问题

**解决**:
```bash
# Linux/macOS
chmod 755 data

# Windows: 以管理员身份运行
```

## 卸载

```bash
# 仅删除Python包
pip uninstall -y requests pyyaml

# 完全删除项目目录
rm -rf "微博热搜分析的Skills"
```

## 更新

```bash
# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements.txt --upgrade
```

## 下一步

安装完成后，请查看 [CONFIGURATION.md](CONFIGURATION.md) 了解详细配置选项。

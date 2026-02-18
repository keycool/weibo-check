---
name: hotsearch-analyzer-patterns
description: Multi-platform hot search analysis patterns with robust error handling
version: 2.1.0
source: local-git-analysis
analyzed_commits: 6
repository: 微博热搜分析的Skills
last_updated: 2026-02-18
---

# Hot Search Analyzer Patterns

This skill documents the coding patterns, architecture, and workflows extracted from the multi-platform hot search analysis project. The project analyzes trending topics from Weibo (微博), Douyin (抖音), and WeChat (微信) to generate product ideas and insights.

## Commit Conventions

This project uses **Chinese conventional commits** with the `feat:` prefix:

- `feat:` - New features (新功能)
  - Example: `feat: 增加抖音和微信热搜支持，重构为多平台通用结构`
  - Example: `feat: 添加 GitHub Actions 自动化微博热搜分析`

### Commit Message Style
- Messages are written in Chinese (中文)
- Use descriptive, detailed commit messages that explain the change
- Focus on what was added/changed and why

## Code Architecture

```
微博热搜分析的Skills/
├── .github/
│   └── workflows/
│       └── weibo-analysis.yml  # GitHub Actions 自动化工作流
├── .claude/
│   ├── commands/           # Claude Code skill definitions
│   │   └── weibo-trends-analyzer.md
│   └── settings.local.json
├── config/
│   ├── config.yaml         # Main configuration file
│   └── config.example.yaml # Configuration template
├── data/                   # Generated data and reports
│   ├── *_raw_*.json       # Raw API responses
│   ├── *_analysis_*.json  # Analysis results
│   ├── *_analysis_*.html  # HTML reports
│   └── debug_json_*.txt   # Debug files for JSON parsing errors
├── docs/                   # Documentation
│   ├── CONFIGURATION.md
│   ├── INSTALLATION.md
│   └── README.md
├── src/                    # Source code
│   ├── __init__.py
│   ├── fetch_hotsearch.py   # Multi-platform data fetcher
│   ├── fetch_weibo.py       # Legacy Weibo-specific fetcher
│   ├── analyze_trends.py    # Claude-powered analysis
│   ├── analyze_with_claude.py # Alternative Claude analyzer
│   ├── config_loader.py     # Configuration management
│   ├── path_utils.py        # Cross-platform path handling
│   ├── generate_index.py    # GitHub Pages index generator
│   └── cleanup_temp.py      # Temporary file cleanup
├── requirements.txt
├── SKILL.md               # This file - extracted patterns
└── version.txt
```

### Module Organization

1. **Data Fetching Layer** (`fetch_hotsearch.py`)
   - Generic `HotSearchFetcher` class supporting multiple platforms
   - Platform-agnostic API integration
   - Retry logic with exponential backoff
   - JSON data normalization

2. **Analysis Layer** (`analyze_trends.py`)
   - `TrendAnalyzer` class using Claude/Anthropic SDK
   - Multi-dimensional scoring system
   - Product idea generation
   - HTML report generation

3. **Configuration Layer** (`config_loader.py`)
   - YAML-based configuration with environment variable overrides
   - Priority: CLI args > env vars > config.yaml > defaults
   - Deep merge for nested configurations

4. **Utilities Layer** (`path_utils.py`)
   - Cross-platform path management
   - Automatic project root detection
   - Directory creation helpers

## Key Design Patterns

### 1. Multi-Platform Support Pattern

The codebase was refactored to support multiple platforms (Weibo, Douyin, WeChat) using a unified structure:

```python
# Platform-agnostic fetcher
fetcher = HotSearchFetcher(source="weibo")  # or "douyin", "wechat"
fetcher.run()

# Platform-agnostic analyzer
analyzer = TrendAnalyzer(source="weibo")
analyzer.run()
```

**Key principles:**
- Single class handles all platforms via `source` parameter
- Configuration-driven API endpoints
- Normalized data format across platforms
- Consistent file naming: `{source}_raw_{timestamp}.json`

### 2. Configuration Management Pattern

Three-tier configuration system:

```python
# Priority order:
# 1. Command-line arguments (highest)
# 2. Environment variables (TIANAPI_KEY, WEIBO_SKILL_*)
# 3. YAML config file (config/config.yaml)
# 4. Code defaults (lowest)

config_loader = ConfigLoader(config_path)
config = config_loader.load()
```

**Best practices:**
- Never hardcode API keys in code
- Use `TIANAPI_KEY` environment variable for secrets
- Provide `config.example.yaml` as template
- Support both absolute and relative paths

### 3. Path Management Pattern

Cross-platform path handling with automatic root detection:

```python
path_manager = PathManager()
data_dir = path_manager.ensure_data_dir()  # Creates if not exists
config_file = path_manager.get_config_file()
```

**Key features:**
- Detects project root by finding `.claude` directory
- Provides typed Path objects (pathlib)
- Auto-creates directories when needed
- Consistent path resolution across Windows/Unix

### 4. API Integration Pattern

Robust API calls with retry logic:

```python
for attempt in range(self.max_retries):
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if not self._validate_response(data):
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return None

        return data
    except Exception as e:
        if attempt < self.max_retries - 1:
            time.sleep(2 ** attempt)
```

**Pattern elements:**
- Configurable retry count and timeout
- Exponential backoff (2^attempt seconds)
- Response validation before processing
- Graceful error handling

### 5. Data Processing Pipeline

Standard workflow for all platforms:

```
1. Fetch raw data → {source}_raw_{timestamp}.json
2. Analyze with Claude → {source}_analysis_{timestamp}.json
3. Generate HTML report → {source}_analysis_{timestamp}.html
4. Create index file → index_{source}.html
```

### 6. Claude SDK Integration Pattern

Using Anthropic SDK for AI-powered analysis:

```python
client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

message = client.messages.create(
    model=os.getenv("MODEL_ID", "glm-4.6"),  # Supports custom models
    max_tokens=16000,
    messages=[{"role": "user", "content": prompt}]
)

response_text = message.content[0].text
```

**Key practices:**
- Support model override via `MODEL_ID` env var
- Parse JSON responses with fallback cleanup
- Handle markdown code blocks in responses
- Regex-based JSON extraction as last resort

### 7. Enhanced JSON Error Handling Pattern

Robust JSON parsing with multiple fallback strategies:

```python
try:
    return json.loads(response_text)
except json.JSONDecodeError as e:
    print(f"⚠️ JSON 解析失败: {e}")
    print(f"错误位置: line {e.lineno} column {e.colno}")

    # Strategy 1: Extract JSON array first
    match = re.search(r'\[[\s\S]*\]', response_text)
    if match:
        extracted = match.group()
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            # Strategy 2: Fix extracted JSON
            fixed = self._fix_json(extracted)
            return json.loads(fixed)

    # Strategy 3: Fix original text
    fixed_text = self._fix_json(response_text)
    return json.loads(fixed_text)
```

**JSON Fix Rules:**
- Remove BOM and invisible characters
- Fix missing commas between objects: `}{` → `},{`
- Fix missing commas between arrays: `][` → `],[`
- Fix missing commas after values: `85"key"` → `85,"key"`
- Fix missing commas after booleans: `true{` → `true,{`
- Remove trailing commas: `[1,2,]` → `[1,2]`
- Remove leading commas: `{,"key"` → `{"key"`

**Debug File Generation:**
When JSON parsing fails, automatically save debug information:
```
data/debug_json_YYYYMMDD_HHMMSS.txt
├── === 原始响应 ===
├── === 提取的 JSON ===
└── === 修复后的 JSON ===
```

## Workflows

### GitHub Actions Automation Workflow

The project includes automated analysis via GitHub Actions:

**Workflow File**: `.github/workflows/weibo-analysis.yml`

**Triggers:**
- Scheduled: Daily at 6:00 AM and 6:00 PM Beijing time
- Manual: Via workflow_dispatch

**Steps:**
1. Checkout repository
2. Setup Python 3.11 with pip cache
3. Install dependencies from requirements.txt
4. Fetch hot search data: `python -m src.fetch_weibo`
5. Analyze with Claude: `python -m src.analyze_with_claude`
6. Upload artifacts (HTML reports, retention: 30 days)
7. Deploy to GitHub Pages (gh-pages branch)

**Required Secrets:**
```yaml
TIANAPI_KEY          # 天API密钥
ANTHROPIC_API_KEY    # Claude/智谱 API密钥
ANTHROPIC_BASE_URL   # API基础URL（可选）
```

**Configuration in GitHub:**
1. Go to repository Settings → Secrets and variables → Actions
2. Add the required secrets
3. Enable GitHub Pages from gh-pages branch
4. Workflow runs automatically or manually trigger

### GitHub Pages Index Generation

The project includes an automatic index page generator for GitHub Pages:

**Generator File**: `src/generate_index.py`

**Functionality:**
- Scans `data/` directory for all HTML reports
- Groups reports by platform (weibo, douyin, wechat)
- Displays only the **latest report** per platform
- Generates `data/index.html` for GitHub Pages

**How it works:**
1. Finds all `*_analysis_*.html` files in data directory
2. Parses filename to extract platform and timestamp
3. Sorts by timestamp (newest first)
4. For each platform, keeps only the most recent report
5. Generates responsive HTML with platform sections

**Usage:**
```bash
# Run locally
python src/generate_index.py

# Output: data/index.html
```

**Key Features:**
- Each platform shows only the latest report (configurable via `reports[:n]` slice)
- Responsive grid layout
- Platform icons and section headers
- File size display
- Automatic timestamp parsing from filenames

**File Naming Convention:**
```
{platform}_analysis_{YYYYMMDD_HHMMSS}.html
Example: weibo_analysis_20260116_195949.html
```

### Temporary File Cleanup Module

The project includes an automatic cleanup module for temporary files:

**Cleanup File**: `src/cleanup_temp.py`

**Functionality:**
- Automatically cleans up `tmpclaude-*` temporary files in project root
- Keeps the latest N files (default: 3)
- Removes old files based on modification time

**How it works:**
1. Scans project root for files matching `tmpclaude-*` pattern
2. Sorts files by modification time (newest first)
3. Deletes files beyond the keep limit
4. Reports deleted file count

**Usage:**
```bash
# Run as standalone
python -m src.cleanup_temp

# Run with custom keep count
python -m src.cleanup_temp 5  # Keep 5 files
```

**Integration:**
- Added as a step in GitHub Actions workflow after index generation
- Independent module, can be called from any Python code

**Key Features:**
- Configurable keep count via parameter
- Cross-platform path handling
- Detailed logging of cleanup operations
- Safe: only deletes files, never directories

### Adding Support for a New Platform

When adding a new hot search platform (e.g., Xiaohongshu):

1. **Update configuration** (`config/config.yaml`):
   ```yaml
   api:
     tianapi:
       sources:
         xiaohongshu: "https://apis.tianapi.com/xiaohongshu/index"
   ```

2. **Update source mapping** (`analyze_trends.py`):
   ```python
   self.source_map = {
       "weibo": "微博",
       "douyin": "抖音",
       "wechat": "微信",
       "xiaohongshu": "小红书"  # Add new platform
   }
   ```

3. **Update CLI choices** (both files):
   ```python
   parser.add_argument("--source", choices=["weibo", "douyin", "wechat", "xiaohongshu"])
   ```

4. **Test the workflow**:
   ```bash
   python -m src.fetch_hotsearch --source xiaohongshu
   python -m src.analyze_trends --source xiaohongshu
   ```

### Running Analysis Workflow

Complete workflow for analyzing hot search trends:

```bash
# Method 1: Using legacy Weibo-specific module
python -m src.fetch_weibo
python -m src.analyze_with_claude

# Method 2: Using multi-platform module
python -m src.fetch_hotsearch --source weibo
python -m src.analyze_trends --source weibo

# Method 3: Analyze other platforms
python -m src.fetch_hotsearch --source douyin
python -m src.analyze_trends --source douyin

python -m src.fetch_hotsearch --source wechat
python -m src.analyze_trends --source wechat

# View reports
# Open data/*_analysis_YYYYMMDD_HHMMSS.html in browser
```

**Output Files:**
- `data/{source}_raw_{timestamp}.json` - Raw API data
- `data/{source}_analysis_{timestamp}.json` - Analysis results
- `data/{source}_analysis_{timestamp}.html` - HTML report
- `data/debug_json_{timestamp}.txt` - Debug info (if errors occur)

### Configuration Setup Workflow

First-time setup:

```bash
# 1. Copy example config
cp config/config.example.yaml config/config.yaml

# 2. Set API key (recommended method)
export TIANAPI_KEY=your_api_key_here

# 3. (Optional) Set Anthropic API key for Claude
export ANTHROPIC_API_KEY=your_anthropic_key

# 4. (Optional) Customize model
export MODEL_ID=glm-4.6  # or claude-3-5-sonnet-20241022

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run
python -m src.fetch_hotsearch --source weibo
```

## Testing Patterns

### Manual Testing Approach

The project uses manual testing with real API calls:

1. **Data Fetching Tests**:
   - Verify API connectivity
   - Check JSON file creation in `data/` directory
   - Validate data structure and field mapping

2. **Analysis Tests**:
   - Verify Claude API integration
   - Check scoring calculations
   - Validate HTML report generation

3. **Configuration Tests**:
   - Test environment variable overrides
   - Verify YAML config loading
   - Check default fallbacks

### Error Handling Patterns

```python
# Pattern 1: Graceful degradation
if not self.check_api_key():
    print("错误: API密钥未设置！")
    return 1

# Pattern 2: Retry with backoff
for attempt in range(self.max_retries):
    try:
        # ... operation ...
    except Exception as e:
        if attempt < self.max_retries - 1:
            time.sleep(2 ** attempt)
        else:
            print(f"失败: {e}")
            return 1

# Pattern 3: JSON parsing fallback
try:
    return json.loads(response_text)
except json.JSONDecodeError:
    fixed_text = self._fix_json(response_text)
    return json.loads(fixed_text)
```

## File Naming Conventions

### Python Files
- Use snake_case: `fetch_hotsearch.py`, `analyze_trends.py`
- Module names describe functionality clearly
- Utility modules end with `_utils`: `path_utils.py`
- Configuration modules end with `_loader`: `config_loader.py`

### Data Files
- Raw data: `{source}_raw_{timestamp}.json`
- Analysis results: `{source}_analysis_{timestamp}.json`
- HTML reports: `{source}_analysis_{timestamp}.html`
- Index files: `index_{source}.html`
- Timestamp format: `YYYYMMDD_HHMMSS`

### Configuration Files
- Main config: `config.yaml`
- Example/template: `config.example.yaml`
- Never commit `config.yaml` with secrets

## Documentation Patterns

### Docstring Style

Use Chinese docstrings with clear structure:

```python
def fetch_hot_search(self) -> Optional[Dict[str, Any]]:
    """从请求源获取数据"""
    # Implementation...

class HotSearchFetcher:
    """通用热搜数据获取器"""

    def __init__(self, source: str = "weibo"):
        """
        初始化获取器

        Args:
            source: 热搜来源 (weibo, douyin, wechat)
        """
```

### README Structure

Documentation follows this hierarchy:

```
docs/
├── README.md           # Overview and quick start
├── INSTALLATION.md     # Setup instructions
└── CONFIGURATION.md    # Configuration reference
```

### Skill Documentation

Claude Code skills use detailed markdown with:
- Step-by-step execution instructions
- Configuration examples
- Troubleshooting section
- Environment variable reference

## Code Style Guidelines

### Import Organization

```python
# 1. Standard library imports
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# 2. Third-party imports
import requests
import anthropic

# 3. Local imports (with path setup)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_loader import ConfigLoader
from src.path_utils import PathManager
```

### Class Structure

```python
class ClassName:
    """类文档字符串"""

    # 1. Class constants
    CONSTANT_NAME = "value"

    def __init__(self, param: str):
        """初始化方法"""
        # 2. Instance attributes
        self.param = param
        self.config = self._load_config()

    # 3. Public methods
    def public_method(self) -> ReturnType:
        """公共方法"""
        pass

    # 4. Private methods (prefixed with _)
    def _private_method(self) -> ReturnType:
        """私有方法"""
        pass
```

### Error Messages

Use Chinese error messages with helpful context:

```python
print("错误: API密钥未设置！")
print(f"尝试 {attempt + 1} 失败: {e}")
print("⚠️ JSON 解析失败: {e}")
```

Use emoji for visual clarity:
- 🚀 Starting process
- 📊 Data/statistics
- ✅ Success
- ❌ Error
- 📂 File operations
- 🤖 AI/API operations
- 💡 Ideas/insights
- 🎉 Completion

## Environment Variables

### Required Variables

```bash
# API Keys
TIANAPI_KEY=your_tianapi_key          # Required for data fetching
ANTHROPIC_API_KEY=your_anthropic_key  # Required for analysis

# Optional Overrides
MODEL_ID=glm-4.6                      # AI model selection
WEIBO_SKILL_TOPIC_COUNT=20            # Number of topics to analyze
WEIBO_SKILL_DATA_DIR=data             # Data directory path
WEIBO_SKILL_LOG_LEVEL=INFO            # Logging level
```

### Configuration Priority

```
Command-line args > Environment variables > config.yaml > Code defaults
```

## Common Pitfalls and Solutions

### Issue: Module Not Found

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Always run from project root using `-m` flag:
```bash
# ✅ Correct
python -m src.fetch_hotsearch

# ❌ Wrong
python src/fetch_hotsearch.py
```

### Issue: API Key Not Set

**Problem**: "错误: API密钥未设置！"

**Solution**: Set environment variable:
```bash
export TIANAPI_KEY=your_key_here
```

### Issue: Config File Not Found

**Problem**: Configuration file doesn't exist

**Solution**: Copy example config:
```bash
cp config/config.example.yaml config/config.yaml
```

### Issue: JSON Parsing Errors

**Problem**: `Expecting ',' delimiter: line X column Y`

**Root Cause**: Claude/智谱 API 返回的 JSON 格式不完全标准

**Solution**: 代码已包含自动修复机制：
1. 自动清理 markdown 代码块标记
2. 提取 JSON 数组内容
3. 应用 7 种 JSON 修复规则
4. 保存调试文件到 `data/debug_json_*.txt`

**手动排查步骤**:
```bash
# 1. 查看最新的调试文件
ls -lt data/debug_json_*.txt | head -1

# 2. 检查原始响应
cat data/debug_json_YYYYMMDD_HHMMSS.txt

# 3. 如果问题持续，尝试更换模型
export MODEL_ID=claude-3-5-sonnet-20241022
python -m src.analyze_with_claude

# 4. 或调整 max_tokens
# 编辑 src/analyze_with_claude.py 中的 max_tokens 参数
```

**预防措施**:
- 在 prompt 中明确要求返回纯 JSON
- 使用更稳定的模型（如 Claude Sonnet）
- 减少分析的话题数量（修改 config.yaml 中的 topic_count）

### Issue: GitHub Actions 失败

**Problem**: Workflow 运行失败，出现各种错误

**常见原因和解决方案**:

1. **Secrets 未配置**
   ```
   错误: API密钥未设置！
   解决: Settings → Secrets → 添加 TIANAPI_KEY 和 ANTHROPIC_API_KEY
   ```

2. **JSON 解析错误**
   ```
   错误: Expecting ',' delimiter
   解决: 代码已包含自动修复，查看 Actions artifacts 中的 debug_json_*.txt
   ```

3. **模块导入错误**
   ```
   错误: ModuleNotFoundError
   解决: 检查 workflow 中是否使用 python -m src.module_name 格式
   ```

4. **依赖安装失败**
   ```
   错误: pip install 失败
   解决: 检查 requirements.txt 格式，确保版本号正确
   ```

**调试步骤**:
1. 查看 Actions 日志的详细输出
2. 下载 artifacts 查看生成的文件
3. 本地复现：使用相同的环境变量运行命令
4. 检查 GitHub Pages 部署权限

## Integration with Claude Code

### Skill Definition

Skills are defined in `.claude/commands/*.md` with:

1. **Metadata section**: Configuration and prerequisites
2. **Execution steps**: Numbered workflow
3. **Configuration guide**: Environment variables and files
4. **Troubleshooting**: Common issues and solutions

### Skill Invocation

```bash
# From Claude Code CLI
/weibo-trends-analyzer

# Or programmatically
python -m src.fetch_hotsearch --source weibo && \
python -m src.analyze_trends --source weibo
```

## Future Enhancement Patterns

When extending this project:

1. **Add new platforms**: Follow "Adding Support for a New Platform" workflow
2. **Customize scoring**: Modify `analysis.scoring` in config.yaml
3. **Change report style**: Edit HTML template in `generate_html_report()`
4. **Add new analysis dimensions**: Extend prompt in `analyze_topics()`
5. **Integrate new AI models**: Set `MODEL_ID` environment variable

## Summary

This project demonstrates:
- ✅ Multi-platform architecture with single codebase
- ✅ Configuration-driven design with multiple override levels
- ✅ Robust API integration with retry logic
- ✅ Cross-platform path management
- ✅ Claude SDK integration for AI-powered analysis
- ✅ Chinese-language development practices
- ✅ Clean separation of concerns (fetch → analyze → report)

**Key Takeaway**: When building similar analysis tools, prioritize configurability, platform abstraction, and robust error handling from the start.

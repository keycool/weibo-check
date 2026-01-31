#!/usr/bin/env python3
"""
使用 Claude Agent SDK 分析热搜话题 (支持多源：微博、抖音、微信)
生成评分和产品创意报告
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

import anthropic

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_loader import ConfigLoader
from src.path_utils import PathManager


class TrendAnalyzer:
    """热搜话题分析器（使用 Claude SDK）"""

    def __init__(self, source: str = "weibo"):
        self.source = source
        # 初始化 Anthropic 客户端
        self.client = anthropic.Anthropic()
        self.path_manager = PathManager()
        self.config_loader = ConfigLoader(self.path_manager.get_config_file())
        self.config = self.config_loader.load()

        # 使用智谱兼容的模型 ID
        self.model_id = os.getenv("MODEL_ID", "glm-4.6")
        
        # 来源映射
        self.source_map = {
            "weibo": "微博",
            "douyin": "抖音",
            "wechat": "微信"
        }
        self.source_name = self.source_map.get(source, source)

    def get_latest_data_file(self) -> Path:
        """获取最新的热搜数据文件"""
        data_dir = self.path_manager.get_data_dir()
        # 根据 source 查找对应的 raw 文件
        pattern = f"{self.source}_raw_*.json"
        files = sorted(data_dir.glob(pattern), reverse=True)
        if not files:
            raise FileNotFoundError(f"未找到 {self.source} 的热搜数据文件，请先运行 fetch_hotsearch.py --source {self.source}")
        return files[0]

    def analyze_topics(self, data_file: Path) -> list:
        """调用 Claude/智谱 API 分析话题"""
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        topic_count = self.config['analysis']['topic_count']
        topics = data['topics'][:topic_count]

        print(f"📊 准备分析 {len(topics)} 个 {self.source_name} 话题...")

        prompt = f"""你是一个专业的产品创意分析师。请分析以下{self.source_name}热搜话题。

## 评分标准（总分100分）

**有趣度（80分）**：
- 新颖性（20分）：话题的独特性和意外性
- 情感共鸣（20分）：公众参与度和情感投入
- 传播潜力（20分）：话题的可分享性
- 娱乐价值（20分）：趣味性和吸引力

**有用度（20分）**：
- 实用价值（10分）：是否解决实际问题
- 市场潜力（10分）：商业化和变现机会

## 话题数据
{json.dumps(topics, ensure_ascii=False, indent=2)}

## 输出要求
为每个话题生成 JSON 格式的分析结果，包含：
- rank: 排名（数字）
- title: 话题标题（字符串）
- scores: 各维度评分对象，包含 novelty, resonance, viral, entertainment, practical, market
- total_score: 总分（数字）
- grade: 等级，"优秀"(>=80分)/"良好"(>=60分)/"普通"(<60分)
- product_idea: 产品创意对象，包含：
  - name: 产品名称
  - features: 核心功能（字符串描述）
  - target_users: 目标用户（字符串描述）
  - value_proposition: 价值主张（字符串描述）

请只返回 JSON 数组，不要添加任何其他文字说明或 markdown 标记。"""

        print(f"🤖 正在调用 {self.model_id} 进行分析...")

        message = self.client.messages.create(
            model=self.model_id,
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}]
        )

        # 解析响应
        response_text = message.content[0].text
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 解析失败: {e}")
            print(f"错误位置: line {e.lineno} column {e.colno}")
            print(f"原始响应前500字符: {response_text[:500]}...")

            # 尝试提取 JSON 数组（先提取再修复）
            import re
            match = re.search(r'\[[\s\S]*\]', response_text)
            if match:
                extracted = match.group()
                print(f"✓ 提取到 JSON 数组，长度: {len(extracted)}")

                # 尝试直接解析提取的内容
                try:
                    return json.loads(extracted)
                except json.JSONDecodeError as e2:
                    print(f"⚠️ 提取的 JSON 仍有错误: {e2}")
                    print(f"错误位置: line {e2.lineno} column {e2.colno}")

                    # 尝试修复提取的 JSON
                    fixed_extracted = self._fix_json(extracted)
                    try:
                        result = json.loads(fixed_extracted)
                        print(f"✓ JSON 修复成功")
                        return result
                    except json.JSONDecodeError as e3:
                        print(f"⚠️ 修复后仍有错误: {e3}")
                        # 保存问题 JSON 用于调试
                        debug_file = self.path_manager.get_data_dir() / f"debug_json_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write("=== 原始响应 ===\n")
                            f.write(response_text)
                            f.write("\n\n=== 提取的 JSON ===\n")
                            f.write(extracted)
                            f.write("\n\n=== 修复后的 JSON ===\n")
                            f.write(fixed_extracted)
                        print(f"⚠️ 调试信息已保存到: {debug_file.name}")
                        raise e3

            # 如果无法提取 JSON 数组，尝试修复原始文本
            print(f"⚠️ 无法提取 JSON 数组，尝试修复原始文本")
            fixed_text = self._fix_json(response_text)
            try:
                return json.loads(fixed_text)
            except json.JSONDecodeError as e4:
                # 保存问题 JSON 用于调试
                debug_file = self.path_manager.get_data_dir() / f"debug_json_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write("=== 原始响应 ===\n")
                    f.write(response_text)
                    f.write("\n\n=== 修复后的文本 ===\n")
                    f.write(fixed_text)
                print(f"⚠️ 调试信息已保存到: {debug_file.name}")
                raise e4

    def _fix_json(self, text: str) -> str:
        """尝试修复常见的 JSON 格式错误"""
        import re

        # 移除可能的 BOM 和其他不可见字符
        text = text.strip().lstrip('\ufeff')

        # 修复 }{  -> },{  (对象之间缺少逗号)
        text = re.sub(r'\}\s*\{', '},{', text)

        # 修复 ][ -> ],[ (数组之间缺少逗号)
        text = re.sub(r'\]\s*\[', '],[', text)

        # 修复对象后面直接跟字符串键 (如: }"key" -> },"key")
        text = re.sub(r'\}\s*"(?=[a-zA-Z_\u4e00-\u9fff])', '},"', text)

        # 修复数组后面直接跟字符串 (如: ]"key" -> ],"key")
        text = re.sub(r'\]\s*"(?=[a-zA-Z_\u4e00-\u9fff])', '],"', text)

        # 修复 "value""key" -> "value","key" (字符串之间缺少逗号)
        text = re.sub(r'"\s*"(?=[a-zA-Z_\u4e00-\u9fff])', '","', text)

        # 修复 "value"  "key" 或 "value"\n"key" (带空格/换行的情况)
        text = re.sub(r'"\s+\"', '","', text)

        # 修复数字后面直接跟字符串 (如: 85"key" -> 85,"key")
        text = re.sub(r'(\d)\s*"(?=[a-zA-Z_\u4e00-\u9fff])', r'\1,"', text)

        # 修复数字后面直接跟对象 (如: 85{ -> 85,{)
        text = re.sub(r'(\d)\s*\{', r'\1,{', text)

        # 修复 true/false/null 后面直接跟引号
        text = re.sub(r'(true|false|null)\s*"', r'\1,"', text)

        # 修复 true/false/null 后面直接跟对象
        text = re.sub(r'(true|false|null)\s*\{', r'\1,{', text)

        # 移除尾随逗号 (如: [1,2,3,] -> [1,2,3])
        text = re.sub(r',\s*\]', ']', text)
        text = re.sub(r',\s*\}', '}', text)

        # 修复多余的逗号 (如: {,, -> {, 或 ,,, -> ,)
        text = re.sub(r',\s*,+', ',', text)

        # 修复开头的逗号 (如: {,"key" -> {"key")
        text = re.sub(r'\{\s*,', '{', text)
        text = re.sub(r'\[\s*,', '[', text)

        return text

    def generate_html_report(self, analysis: list, timestamp: str) -> Path:
        """生成 HTML 报告"""
        grades = self.config['grades']
        excellent = sum(1 for a in analysis if a.get('total_score', 0) >= grades['excellent'])
        good = sum(1 for a in analysis if grades['good'] <= a.get('total_score', 0) < grades['excellent'])
        average = len(analysis) - excellent - good

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.source_name}热搜产品创意分析 - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
            color: #00d4ff;
            font-size: 2em;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.1);
            padding: 20px 30px;
            border-radius: 10px;
            text-align: center;
            min-width: 120px;
        }}
        .stat-card h3 {{ font-size: 2em; margin-top: 5px; }}
        .stat-card.excellent h3 {{ color: #00ff88; }}
        .stat-card.good h3 {{ color: #00d4ff; }}
        .stat-card.average h3 {{ color: #888; }}
        .topic-card {{
            background: rgba(255,255,255,0.05);
            margin: 20px 0;
            border-radius: 15px;
            padding: 25px;
            border-left: 4px solid #666;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .topic-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .topic-card.excellent {{ border-left-color: #00ff88; }}
        .topic-card.good {{ border-left-color: #00d4ff; }}
        .topic-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .topic-title {{
            font-size: 1.3em;
            font-weight: bold;
            flex: 1;
        }}
        .topic-score {{
            font-size: 1.5em;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            background: rgba(0,0,0,0.3);
        }}
        .topic-card.excellent .topic-score {{ color: #00ff88; }}
        .topic-card.good .topic-score {{ color: #00d4ff; }}
        .topic-grade {{
            font-size: 0.9em;
            padding: 3px 10px;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
        }}
        .scores-detail {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
            font-size: 0.85em;
            color: #aaa;
        }}
        .scores-detail span {{
            background: rgba(255,255,255,0.05);
            padding: 3px 8px;
            border-radius: 5px;
        }}
        .product-idea {{
            margin-top: 15px;
            padding: 15px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }}
        .product-idea h4 {{
            color: #ffd700;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        .product-idea p {{
            margin: 8px 0;
            line-height: 1.6;
            color: #ccc;
        }}
        .product-idea strong {{
            color: #fff;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        @media (max-width: 600px) {{
            .topic-header {{ flex-direction: column; align-items: flex-start; }}
            .stat-card {{ min-width: 100px; padding: 15px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 {self.source_name}热搜产品创意分析</h1>
        <div class="stats">
            <div class="stat-card">
                <p>总话题</p>
                <h3>{len(analysis)}</h3>
            </div>
            <div class="stat-card excellent">
                <p>优秀 (80+)</p>
                <h3>{excellent}</h3>
            </div>
            <div class="stat-card good">
                <p>良好 (60-80)</p>
                <h3>{good}</h3>
            </div>
            <div class="stat-card average">
                <p>普通 (&lt;60)</p>
                <h3>{average}</h3>
            </div>
        </div>
"""

        for item in analysis:
            total_score = item.get('total_score', 0)
            grade_class = 'excellent' if total_score >= 80 else ('good' if total_score >= 60 else '')
            grade_text = item.get('grade', '普通')
            idea = item.get('product_idea', {})
            scores = item.get('scores', {})

            score_items = []
            if scores:
                score_mapping = {'novelty': '新颖性', 'resonance': '情感共鸣', 'viral': '传播潜力', 'entertainment': '娱乐价值', 'practical': '实用价值', 'market': '市场潜力'}
                for key, label in score_mapping.items():
                    if key in scores:
                        score_items.append(f"<span>{label}: {scores[key]}</span>")

            scores_html = ''.join(score_items)
            html_content += f"""
        <div class="topic-card {grade_class}">
            <div class="topic-header">
                <span class="topic-title">#{item.get('rank', '?')} {item.get('title', '未知话题')}</span>
                <span class="topic-grade">{grade_text}</span>
                <span class="topic-score">{total_score}分</span>
            </div>
            <div class="scores-detail">{scores_html}</div>
            <div class="product-idea">
                <h4>💡 {idea.get('name', '产品创意')}</h4>
                <p><strong>核心功能：</strong>{idea.get('features', 'N/A')}</p>
                <p><strong>目标用户：</strong>{idea.get('target_users', 'N/A')}</p>
                <p><strong>价值主张：</strong>{idea.get('value_proposition', 'N/A')}</p>
            </div>
        </div>
"""

        html_content += f"""
        <p class="timestamp">
            生成时间：{timestamp}<br>
            来源：{self.source_name}热搜 | Powered by Claude Agent SDK + 智谱 GLM
        </p>
    </div>
</body>
</html>"""

        self.path_manager.ensure_data_dir()
        ts_clean = timestamp.replace('-', '').replace(':', '').replace(' ', '_')
        report_filename = self.config['paths']['report_filename_format'].format(source=self.source, timestamp=ts_clean)
        report_path = self.path_manager.get_data_dir() / report_filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 保存 index.html 用于快速查看 (可选，会覆盖之前来源的 index)
        index_path = self.path_manager.get_data_dir() / f'index_{self.source}.html'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return report_path

    def run(self) -> int:
        print(f"🚀 开始{self.source_name}热搜分析...")
        try:
            data_file = self.get_latest_data_file()
            print(f"📂 数据文件: {data_file.name}")
            analysis = self.analyze_topics(data_file)
            print(f"✅ 分析完成，共 {len(analysis)} 个话题")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_path = self.generate_html_report(analysis, timestamp)
            print(f"📄 HTML 报告: {report_path.name}")

            ts_clean = timestamp.replace('-', '').replace(':', '').replace(' ', '_')
            json_filename = self.config['output']['intermediate_filename'].format(source=self.source, timestamp=ts_clean)
            json_path = self.path_manager.get_data_dir() / json_filename
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"📋 JSON 结果: {json_path.name}")

            print("\n🎉 全部完成!")
            return 0
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return 1


def main():
    parser = argparse.ArgumentParser(description="分析各大平台热搜话题")
    parser.add_argument("--source", default="weibo", choices=["weibo", "douyin", "wechat"], help="来源平台")
    args = parser.parse_args()
    
    analyzer = TrendAnalyzer(source=args.source)
    return analyzer.run()


if __name__ == "__main__":
    sys.exit(main())

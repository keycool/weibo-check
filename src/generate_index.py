#!/usr/bin/env python3
"""
生成 GitHub Pages 索引页面
列出所有平台的分析报告
"""
import sys
from pathlib import Path
from datetime import datetime


def generate_index_html():
    """生成索引页面"""
    # 直接使用相对路径，不依赖 PathManager
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"

    # 确保 data 目录存在
    if not data_dir.exists():
        print(f"Error: data directory not found at {data_dir}")
        return None

    # 获取所有 HTML 报告文件
    html_files = sorted(data_dir.glob("*_analysis_*.html"), reverse=True)

    # 按平台分组
    reports_by_platform = {
        "weibo": [],
        "douyin": [],
        "wechat": []
    }

    platform_names = {
        "weibo": "微博",
        "douyin": "抖音",
        "wechat": "微信"
    }

    for html_file in html_files:
        filename = html_file.name
        # 解析文件名获取平台和时间戳
        for platform in reports_by_platform.keys():
            if filename.startswith(f"{platform}_analysis_"):
                timestamp_str = filename.replace(f"{platform}_analysis_", "").replace(".html", "")
                try:
                    # 尝试解析时间戳
                    if len(timestamp_str) == 15:  # YYYYMMDD_HHMMSS
                        dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        display_time = timestamp_str
                except:
                    display_time = timestamp_str

                reports_by_platform[platform].append({
                    "filename": filename,
                    "timestamp": timestamp_str,
                    "display_time": display_time,
                    "size": html_file.stat().st_size
                })
                break

    # 生成 HTML
    html_content = generate_html_content(reports_by_platform, platform_names)

    # 保存到 data/index.html
    index_path = data_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Index page generated: {index_path}")
    return index_path


def generate_html_content(reports_by_platform, platform_names):
    """生成 HTML 内容"""
    # 统计信息：有报告的平台数
    platforms_with_reports = sum(1 for reports in reports_by_platform.values() if reports)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>多平台热搜分析报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .subtitle {{
            text-align: center;
            color: rgba(255,255,255,0.9);
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.95);
            padding: 20px 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            font-size: 2em;
            color: #667eea;
            margin-top: 5px;
        }}
        .stat-card p {{
            color: #666;
            font-size: 0.9em;
        }}
        .platform-section {{
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .platform-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .platform-icon {{
            font-size: 2em;
            margin-right: 15px;
        }}
        .platform-title {{
            font-size: 1.5em;
            color: #333;
            flex: 1;
        }}
        .platform-count {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}
        .report-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .report-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-color: #667eea;
        }}
        .report-time {{
            font-size: 1.1em;
            color: #333;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        .report-meta {{
            display: flex;
            justify-content: space-between;
            color: #999;
            font-size: 0.85em;
        }}
        .no-reports {{
            text-align: center;
            color: #999;
            padding: 30px;
            font-style: italic;
        }}
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }}
        @media (max-width: 768px) {{
            h1 {{
                font-size: 2em;
            }}
            .reports-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 多平台热搜分析报告</h1>
        <p class="subtitle">实时追踪微博、抖音、微信热搜趋势，AI 驱动的产品创意分析</p>

        <div class="stats">
            <div class="stat-card">
                <p>有报告的平台</p>
                <h3>{platforms_with_reports}</h3>
            </div>
            <div class="stat-card">
                <p>支持平台</p>
                <h3>3</h3>
            </div>
        </div>
"""

    # 为每个平台生成报告列表
    platform_icons = {
        "weibo": "🔥",
        "douyin": "🎵",
        "wechat": "💬"
    }

    for platform, reports in reports_by_platform.items():
        platform_name = platform_names.get(platform, platform)
        icon = platform_icons.get(platform, "📱")

        html += f"""
        <div class="platform-section">
            <div class="platform-header">
                <span class="platform-icon">{icon}</span>
                <h2 class="platform-title">{platform_name}热搜</h2>
                <span class="platform-count">{'最新报告' if reports else '暂无报告'}</span>
            </div>
"""

        if reports:
            html += '            <div class="reports-grid">\n'
            for report in reports[:1]:  # 只显示最新 1 份
                size_kb = report['size'] / 1024
                html += f"""                <div class="report-card" onclick="window.location.href='{report['filename']}'">
                    <div class="report-time">{report['display_time']}</div>
                    <div class="report-meta">
                        <span>📄 {size_kb:.1f} KB</span>
                        <span>👉 查看报告</span>
                    </div>
                </div>
"""
            html += '            </div>\n'
        else:
            html += '            <div class="no-reports">暂无报告</div>\n'

        html += '        </div>\n'

    html += """
        <div class="footer">
            <p>🤖 由 Claude Code 自动生成 | 数据来源：天 API</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                每日自动更新 |
                <a href="https://github.com/keycool/weibo-check" style="color: white; text-decoration: none;">
                    GitHub 仓库
                </a>
            </p>
        </div>
    </div>
</body>
</html>
"""

    return html


if __name__ == "__main__":
    generate_index_html()

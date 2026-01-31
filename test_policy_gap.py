# -*- coding: utf-8 -*-
"""
測試 policy_gap_analysis skill
"""
import os
import sys

# 設定 Python 路徑
sys.path.insert(0, r"c:\Users\user\OneDrive\桌面\All平台")

from app.skills.policy_gap_analysis.run import execute

# 測試文件路徑
base_path = r"c:\Users\user\OneDrive\桌面\All平台\文件測試"

policy_path = os.path.join(base_path, "採購驗收管理辦法.docx")
interview_paths = [
    os.path.join(base_path, "[永瑞] 採購驗收管理辦法訪談 (1).docx"),
    os.path.join(base_path, "[永瑞] 採購驗收管理辦法訪談 (2).docx"),
    os.path.join(base_path, "[永瑞] 採購驗收管理辦法訪談 (3).docx"),
]

print("=" * 60)
print("測試 Policy Gap Analysis Skill")
print("=" * 60)
print(f"管理辦法: {policy_path}")
print(f"訪談紀錄: {len(interview_paths)} 份")
print("=" * 60)
print("\n正在分析中，請稍候...\n")

result = execute({
    "policy_file_path": policy_path,
    "interview_file_paths": interview_paths
})

if result.get("status") == "success":
    report = result.get("report", "")
    print("✅ 分析成功！\n")
    print("=" * 60)
    print("差異分析報告")
    print("=" * 60)
    print(report)
    
    # 儲存報告
    report_path = os.path.join(base_path, "差異分析報告.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n\n報告已儲存至: {report_path}")
else:
    print("❌ 分析失敗:")
    print(result.get("message", "未知錯誤"))

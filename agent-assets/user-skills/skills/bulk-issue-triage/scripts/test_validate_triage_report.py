import tempfile
import unittest
from pathlib import Path

from validate_triage_report import validate_report


VALID_REPORT = """# 批量问题初查与问题分包

## 输入覆盖

- [x] ISSUE-001
- [x] ISSUE-002

## PKG-01 权限恢复

- **包含问题**: ISSUE-001, ISSUE-002
- **领域**: Android 权限 / 相机会话
- **修复复杂度**: M
- **初查置信度**: 中

### 问题表现

重新安装后预览保持黑屏，系统权限弹窗未出现。

### 初步分析

权限恢复入口可能只覆盖首次安装路径。

### 证据与未知

已观察真机截图；尚未核对生命周期日志。

### 后续细化重点

核查权限状态机、拒绝后恢复路径与自动化测试入口。

## 推荐使用方法

在新 agent 窗口输入：

`/agent-orchestration-planner 针对如下外部 agent 已经初步分析的问题集合，进行核查确认，设计细化修复方案，制作好任务包。`
"""


class ValidateTriageReportTest(unittest.TestCase):
    def write_report(self, content: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        with handle:
            handle.write(content)
        return Path(handle.name)

    def test_accepts_complete_report(self) -> None:
        issues = validate_report(
            self.write_report(VALID_REPORT),
            expected_issue_ids={"ISSUE-001", "ISSUE-002"},
        )
        self.assertEqual([], issues)

    def test_rejects_missing_manifestation_and_unassigned_issue(self) -> None:
        content = VALID_REPORT.replace("### 问题表现", "### 用户影响")
        content = content.replace("ISSUE-001, ISSUE-002", "ISSUE-001")
        issues = validate_report(
            self.write_report(content),
            expected_issue_ids={"ISSUE-001", "ISSUE-002"},
        )
        self.assertTrue(any("问题表现" in issue for issue in issues))
        self.assertTrue(any("未分配" in issue for issue in issues))

    def test_rejects_duplicate_issue_ownership(self) -> None:
        duplicate = VALID_REPORT.replace(
            "## 推荐使用方法",
            """## PKG-02 重复归属

- **包含问题**: ISSUE-001
- **领域**: UI
- **修复复杂度**: S
- **初查置信度**: 低

### 问题表现

重复描述。

### 初步分析

重复分析。

### 证据与未知

未知。

### 后续细化重点

确认归属。

## 推荐使用方法""",
        )
        issues = validate_report(
            self.write_report(duplicate),
            expected_issue_ids={"ISSUE-001", "ISSUE-002"},
        )
        self.assertTrue(any("重复归属" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from validate_package_issue_report import validate_report


VALID_REPORT = """# 问题初查与打包

## 决策摘要

- 输入问题数：2
- 问题包数：1
- 待补证据：1
- 修复价值分布：fix-now 1
- 路由分布：handoff 1
- 推荐顺序：先补生命周期日志，再交给单个实现 agent

## 输入覆盖

- [x] CAMERA-BLACK-SCREEN
- [x] QA-17

## Evidence Ledger

- EV-001 | screenshot | qa/black-screen.png | observed | 重新安装后预览区域为黑色
- EV-002 | code | app/permissions/CameraPermission.kt | inferred | 权限恢复入口可能只覆盖首次安装路径

## PKG-01 权限恢复

- **包含问题**: CAMERA-BLACK-SCREEN, QA-17
- **领域**: Android 权限 / 相机会话
- **修复复杂度**: M
- **初查置信度**: 中
- **当前判断**: 高可能
- **修复价值**: fix-now
- **next_route**: handoff
- **证据引用**: EV-001, EV-002
- **依赖**: none
- **明确排除**: 相机驱动兼容性重写

### 问题表现

重新安装后预览保持黑屏，系统权限弹窗未出现。

### 用户影响

核心拍摄路径不可用。

### 初步分析

权限恢复入口可能只覆盖首次安装路径。

### 证据与未知

- 观察事实：EV-001
- 当前代码或测试证据：EV-002
- 反证或替代解释：设备相机服务异常仍未排除
- 待补证据：生命周期日志

### 修复价值核查

- 用户影响：核心拍摄路径不可用，EV-001
- 规范或产品目标冲突：重新安装后仍应恢复到可拍摄状态，EV-002
- 证据强度：截图已观察，代码证据为推断
- 修复风险与机会成本：权限恢复路径边界中等，值得继续
- 当前结论：fix-now

### 分包依据与依赖闭包

两个问题共享权限恢复状态、修改边界和验证矩阵，必须共同修改并共同验证，因此吸收到同一问题包。

### 范围与依赖

- 可能所有权：权限状态机与相机会话恢复
- 前置依赖：none
- 关联包：none
- 明确排除：相机驱动兼容性重写

### 后续细化重点

核查权限状态机、拒绝后恢复路径与自动化测试入口。
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
            expected_issue_ids={"CAMERA-BLACK-SCREEN", "QA-17"},
        )
        self.assertEqual([], issues)

    def test_rejects_missing_decision_summary_and_unassigned_issue(self) -> None:
        content = VALID_REPORT.replace("## 决策摘要", "## 普通摘要")
        content = content.replace("CAMERA-BLACK-SCREEN, QA-17", "CAMERA-BLACK-SCREEN")
        issues = validate_report(
            self.write_report(content),
            expected_issue_ids={"CAMERA-BLACK-SCREEN", "QA-17"},
        )
        self.assertTrue(any("决策摘要" in issue for issue in issues))
        self.assertTrue(any("未分配" in issue for issue in issues))

    def test_rejects_missing_manifestation_and_evidence_reference(self) -> None:
        content = VALID_REPORT.replace("### 问题表现", "### 用户影响")
        content = content.replace("- **证据引用**: EV-001, EV-002", "- **证据引用**: EV-999")
        issues = validate_report(
            self.write_report(content),
            expected_issue_ids={"CAMERA-BLACK-SCREEN", "QA-17"},
        )
        self.assertTrue(any("问题表现" in issue for issue in issues))
        self.assertTrue(any("EV-999" in issue for issue in issues))

    def test_rejects_duplicate_issue_ownership(self) -> None:
        duplicate = VALID_REPORT.replace(
            "### 后续细化重点\n\n核查权限状态机、拒绝后恢复路径与自动化测试入口。",
            """### 后续细化重点

核查权限状态机、拒绝后恢复路径与自动化测试入口。

## PKG-02 重复归属

- **包含问题**: CAMERA-BLACK-SCREEN
- **领域**: UI
- **修复复杂度**: S
- **初查置信度**: 低
- **当前判断**: 待核查
- **修复价值**: defer
- **next_route**: deferred
- **证据引用**: EV-001
- **依赖**: none
- **明确排除**: none

### 问题表现

重复描述。

### 用户影响

重复影响。

### 初步分析

重复分析。

### 证据与未知

未知。

### 修复价值核查

当前证据不足，先延期。

### 分包依据与依赖闭包

错误地重复归属。

### 范围与依赖

none。

### 后续细化重点

确认归属。""",
        )
        issues = validate_report(
            self.write_report(duplicate),
            expected_issue_ids={"CAMERA-BLACK-SCREEN", "QA-17"},
        )
        self.assertTrue(any("重复归属" in issue for issue in issues))

    def test_rejects_unknown_route_and_missing_dependency_closure(self) -> None:
        content = VALID_REPORT.replace(
            "- **next_route**: handoff",
            "- **next_route**: auto-fix",
        ).replace(
            "### 分包依据与依赖闭包",
            "### 普通分包说明",
        )
        issues = validate_report(self.write_report(content))
        self.assertTrue(any("next_route" in issue for issue in issues))
        self.assertTrue(any("依赖闭包" in issue for issue in issues))

    def test_orchestration_requires_explicit_reason(self) -> None:
        content = VALID_REPORT.replace(
            "- **next_route**: handoff",
            "- **next_route**: orchestration",
        )
        issues = validate_report(self.write_report(content))
        self.assertTrue(any("编排理由" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()

def report_status_from_runner_status(runner_status: str) -> str:
    if runner_status == "PASS":
        return "complete"
    if runner_status == "FAIL":
        return "failed"
    if runner_status == "NEEDS_HUMAN":
        return "waiting_on_user"
    return "in_progress"


def slack_checkbox_from_report_status(report_status: str) -> str:
    if report_status == "complete":
        return "[x]"
    return "[ ]"

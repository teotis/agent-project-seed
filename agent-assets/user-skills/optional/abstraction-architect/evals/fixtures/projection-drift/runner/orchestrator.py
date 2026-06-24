from dataclasses import dataclass


RUNNER_STATUSES = {
    "PENDING",
    "IN_PROGRESS",
    "PASS",
    "FAIL",
    "NEEDS_HUMAN",
}


@dataclass
class PackageRun:
    package_id: str
    worker: str
    status: str


def ready_to_finalize(packages: list[PackageRun]) -> bool:
    return all(package.status == "PASS" for package in packages)


def next_event(package: PackageRun) -> str:
    if package.worker == "manual" and package.status == "PASS":
        return "approval_requested"
    if package.status == "FAIL":
        return "retry_requested"
    return "status_snapshot"

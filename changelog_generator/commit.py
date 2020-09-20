import re
from typing import List, Optional

re_header_pattern = re.compile(
    "^(?P<type>[^\(]+)\((?P<scope>[^\)]+)\): (?P<subject>.+)$"
)
re_jira_pattern = re.compile("^([A-Z]{2,4}-[0-9]{1,6} ?)+$")
re_broke_pattern = re.compile("^BROKEN:$")
re_revert_header_pattern = re.compile("^[R|r]evert:? (?P<summary>.*)$")
re_revert_commit_pattern = re.compile("^This reverts commit ([a-f0-9]+)")
re_temp_header_pattern = re.compile("^(fixup!|squash!).*$")


class Commit:
    sha1: str
    short: str
    summary: str
    message: str

    revert: Optional["Commit"] = None
    type: Optional[str] = None
    scope: Optional[str] = None
    subject: Optional[str] = None

    def __init__(self, hexsha: str, summary: str, message: str) -> None:
        self.sha1 = hexsha
        self.short = hexsha[:8]
        self.message = message
        self.summary = summary

        res = re_header_pattern.match(self.summary)
        if res:
            self.type = res.group("type")
            self.scope = res.group("scope")
            self.subject = res.group("subject")

        res = re_revert_header_pattern.match(summary)
        if res:
            # TODO: properly fetch the reverted commit */
            self.revert = Commit(
                hexsha="", summary=res.group("summary"), message=res.group("summary")
            )

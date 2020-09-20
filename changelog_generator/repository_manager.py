import re
from typing import List, Optional

from git import Repo

tag_version_re = re.compile(
    "^(?P<major>\d+)-(?P<minor>\d+)-((?P<bug>\d+)|rc(?P<rc>\d+)){0,1}$"
)


def isTagVersion(tag: str) -> bool:
    return not not tag_version_re.match(tag)


def getTagValue(tag: str) -> int:
    res = tag_version_re.match(tag)
    assert res
    return -1 * (
        1000000 * int(res.group("major"))
        + 10000 * int(res.group("minor"))
        + 100 * int(res.group("bug") or "0")
        + int(res.group("rc") or "100")
    )


class RepositoryManager:
    def __init__(self, uri: str) -> None:
        self.repository = Repo(uri)
        self.tag_names: List[str] = []
        assert not self.repository.bare

    def getTags(self) -> List[str]:
        if not self.tag_names:
            tags: List[str] = self.repository.git.tag("--merged").split("\n")
            self.tag_names = list(sorted(filter(isTagVersion, tags), key=getTagValue))
        return self.tag_names

    def getCurrentTag(self) -> Optional[str]:
        tags = self.getTags()

        if not len(tags):
            return None

        tag = self.repository.tags[tags[0]]
        if tag.commit == self.repository.head.commit:
            return tag
        return None

    def getPreviousTag(self) -> Optional[str]:
        tags = self.getTags()
        if not len(tags):
            return None

        tag = self.repository.tags[tags[0]]
        if tag.commit != self.repository.head.commit:
            return tags[0]

        if len(tags) < 2:
            return None

        return tags[1]
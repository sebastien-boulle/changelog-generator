import re
from typing import Iterable, List, Optional

from git import Repo

from changelog_generator.commit import Commit

tag_version_re = re.compile(
    "^(?P<major>\d+)-(?P<minor>\d+)-((?P<bug>\d+)|rc(?P<rc>\d+)){0,1}$"
)

remote_re = re.compile(
    "^(https://github\.com/|git@github\.com:)(?P<organization>[^/]+)/(?P<repository>[^.]+)(\.git)?$"
)


def isTagVersion(tag: str) -> bool:
    res = tag_version_re.match(tag)
    return not not res and not res.group("rc")


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
    repository: Repo
    organization: str = ""
    name: str = ""

    def __init__(self, uri: str) -> None:
        self.repository = Repo(uri)
        self.tag_names: List[str] = []
        assert not self.repository.bare

        res = remote_re.match(self.repository.remotes["origin"].url)
        if res:
            self.organization = res.group("organization")
            self.name = res.group("repository")

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

    def getCommitsSinceLastTag(self) -> Iterable[Commit]:
        previousTag = self.getPreviousTag()
        currentTag = self.getCurrentTag() or "HEAD"

        if previousTag:
            revision = "%s..%s" % (previousTag, currentTag)
        else:
            revision = currentTag

        return map(
            lambda commit: Commit(
                hexsha=commit.hexsha, summary=commit.summary, message=commit.message
            ),
            self.repository.iter_commits(revision, no_merges=True),
        )

    def getOrganization(self) -> str:
        return self.organization

    def getName(self) -> str:
        return self.name

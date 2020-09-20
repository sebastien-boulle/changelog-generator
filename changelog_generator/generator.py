from typing import List

from jinja2 import Template

from changelog_generator.commit import Commit

template = Template(
    """# [{{currentTag}}](https://github.com/{{organization}}/{{repository}}/compare/{{previousTag}}...{{currentTag}})

{% for typeNode in commitTrees %}
## {{typeNode.type}}

{% for commit in typeNode.commits -%}
* **{{commit.scope}}**: {{commit.subject}} ([{{commit.short}}](https://github.com/{{organization}}/{{repository}}/commit/{{commit.sha1}}))
{%- if commit.jiras|length -%}
, references:
{%- for jira in commit.jiras %} [{{jira}}](https://{{organization}}.atlassian.net/browse/{{jira}}) {%- endfor %}
{%- endif %}
{% endfor -%}
{% endfor -%}"""
)


class CommitTree:
    type: str
    commits: List["Commit"]


def renderChangelog(
    organization: str,
    repository: str,
    previousTag: str,
    currentTag: str,
    commitTrees: List["CommitTree"],
) -> str:
    return template.render(
        organization=organization,
        repository=repository,
        previousTag=previousTag,
        currentTag=currentTag,
        commitTrees=commitTrees,
    )

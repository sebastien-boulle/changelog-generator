from changelog_generator.repository_manager import RepositoryManager


def main() -> None:
    repository = RepositoryManager("./")
    print(
        "Generate changelog between %s and %s"
        % (repository.getPreviousTag(), repository.getCurrentTag())
    )


if __name__ == "__main__":
    main()

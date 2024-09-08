"""Simple entrypoint demo"""


def main() -> None:
    print("I'm alive")


# Needed for poetry scripts defined in pyproject.toml
def entrypoint() -> None:
    main()


if __name__ == "__main__":
    entrypoint()

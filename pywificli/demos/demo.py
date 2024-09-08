"""Simple entrypoint demo"""

from pywificli.domain.model import Model


def main() -> None:
    model = Model("model", 1)
    print(f"I'm alive: {model}")


# Needed for poetry scripts defined in pyproject.toml
def entrypoint() -> None:
    main()


if __name__ == "__main__":
    entrypoint()

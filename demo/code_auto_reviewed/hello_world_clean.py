"""Greet module."""


def greet(name: str) -> str:
    """Return a greeting string."""
    return f"Hello, {name}!"


def main() -> None:
    print(greet("World"))


if __name__ == "__main__":
    main()
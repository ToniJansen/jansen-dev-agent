"""Greet module."""


def greet(name: str) -> None:
    print(f"Hello, {name}!")


def main() -> None:
    greet("World")


if __name__ == "__main__":
    main()
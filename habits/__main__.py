"""CLI entrypoint module for `python -m habits`."""

import sys

from habits import cli


def main() -> int:
    """Entrypoint for habit CLI execution."""
    return cli.main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())

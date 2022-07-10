#!/usr/bin/env python
import logging

try:
    from ... import config
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "config.py not found. Please follow the instructions in the README about how to set up the config.py file"
    )
from . import WcdImportBot


def main() -> None:
    logging.basicConfig(level=config.loglevel)
    WcdImportBot().run()


if __name__ == "__main__":
    main()

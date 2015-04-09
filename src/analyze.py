VERSION_STRING = "Nukecon 0.1"

import logging
import argparse
from analyze import commands

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description=
            "TODO Some description should be invented TODO")
    parser.add_argument('command',
                        metavar="COMMAND",
                        choices=['update', 'download', 'analyze'],
                        help="update, summary, download or analyze")

    parser.add_argument('component',
                        metavar="COMPONENT")

    parser.add_argument("--resolution-max",
                        metavar="RESOLUTION",
                        type=float,
                        help="Maximal resolution of structures")

    args = parser.parse_args()

    component = args.component.lower()
    if args.command == "update":
        commands.run_summary(component)
    elif args.command == "download":
        commands.run_download(component, args.resolution_max)
    elif args.command == "analyze":
        commands.run_analysis(component)
    else:
        logging.error("Command not implemented yet")


if __name__ == "__main__":
    main()

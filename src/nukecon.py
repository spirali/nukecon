import logging
import argparse
import commands
import query

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description=
            "TODO Some description should be invented TODO")
    parser.add_argument('command',
                        metavar="COMMAND",
                        choices=['update', 'summary', 'download', 'analyze'],
                        help="update, summary, download or analyze")

    parser.add_argument('component',
                        metavar="COMPONENT")

    parser.add_argument("--resolution-max",
                        metavar="RESOLUTION",
                        type=float,
                        help="Maximal resolution of structures")

    args = parser.parse_args()

    q = query.Query(args)

    if args.command == "update":
        commands.run_update(q)
    elif args.command == "summary":
        commands.run_summary(q)
    elif args.command == "download":
        commands.run_download(q)
    elif args.command == "analyze":
        commands.run_analysis(q)
    else:
        logging.error("Command not implemented yet")


if __name__ == "__main__":
    main()
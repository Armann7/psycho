import argparse
import asyncio
import logging
from pathlib import Path

from src.psycho_guide import PsychoGuide


async def main(scrape: bool = False, file_csv: Path = None):
    guide = PsychoGuide()
    if scrape:
        await guide.scrape()
    elif file_csv:
        with open(file_csv, 'w', encoding='utf8') as file_stream:
            guide.write_csv(file_stream)
    else:
        stats = guide.get_statistics()
        print(stats)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--scrape',
        type=bool,
        default=False,
        required=False,
        action=argparse.BooleanOptionalAction,
        help="Scrape data",
        )
    parser.add_argument(
        '--export_csv',
        type=Path,
        required=False,
        help="Export data as csv to given file",
        )
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        args = _parse_args()
    except ValueError:
        exit(1)
    asyncio.run(main(args.scrape, args.export_csv))

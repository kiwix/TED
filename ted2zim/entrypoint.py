#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import logging
import argparse

from .constants import NAME, SCRAPER, logger
from .scraper import Ted2Zim


def main():
    parser = argparse.ArgumentParser(
        prog=NAME, description="Scraper to create ZIM files from TED videos",
    )

    parser.add_argument(
        "--categories", help="List of topics to scrape", required=True, nargs="+",
    )

    parser.add_argument(
        "--max-pages",
        help="Number of pages to scrape in each topic. Pass 'max' if you want to scrape all",
        required=True,
        dest="max_pages",
    )

    parser.add_argument(
        "--name",
        help="ZIM name. Used as identifier and filename (date will be appended)",
        required=True,
    )

    parser.add_argument(
        "--format",
        help="Format to download/transcode video to. webm is smaller",
        choices=["mp4", "webm"],
        default="webm",
        dest="video_format",
    )

    parser.add_argument(
        "--low-quality",
        help="Re-encode video using stronger compression",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--output",
        help="Output folder for ZIM file or build folder",
        default="/output",
        dest="output_dir",
    )

    parser.add_argument(
        "--no-zim",
        help="Don't produce a ZIM file, create HTML folder only.",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--zim-file",
        help="ZIM file name (based on --name if not provided)",
        dest="fname",
    )

    parser.add_argument(
        "--language", help="ISO-639-3 (3 chars) language code of content", default="eng"
    )

    parser.add_argument(
        "--locale",
        help="Locale name to use for translations (if avail) and time representations. Defaults to --language or English.",
        dest="locale_name",
    )

    parser.add_argument(
        "--title",
        help="Custom title for your project and ZIM. Default to Channel name (of first video if playlists)",
    )

    parser.add_argument(
        "--description",
        help="Custom description for your project and ZIM. Default to Channel name (of first video if playlists)",
    )

    parser.add_argument(
        "--creator",
        help="Name of content creator. Defaults to Channel name or “Youtue Channels”",
    )

    parser.add_argument(
        "--publisher", help="Custom publisher name (ZIM metadata)", default="Kiwix"
    )

    parser.add_argument(
        "--tags",
        help="List of comma-separated Tags for the ZIM file. _videos:yes added automatically",
        default="youtube",
    )

    parser.add_argument(
        "--keep",
        help="Don't erase build folder on start (for debug/devel)",
        default=False,
        action="store_true",
        dest="keep_build_dir",
    )

    parser.add_argument(
        "--skip-download",
        help="Skip the download step (videos, thumbnails, subtitles)",
        default=False,
        action="store_true",
        dest="skip_download",
    )

    parser.add_argument(
        "--debug", help="Enable verbose output", action="store_true", default=False
    )

    args = parser.parse_args()
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    try:
        scraper = Ted2Zim(**dict(args._get_kwargs()))
        scraper.run()
    except Exception as exc:
        logger.error(f"FAILED. An error occurred: {exc}")
        if args.debug:
            logger.exception(exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

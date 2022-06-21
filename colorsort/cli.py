#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

import config as conf
import visualization as vis
from heuristics import HeuristicName
from image import Image
from util import ImageOrientation

ANALYZE_PARSER = "analyze"
SORT_PARSER = "sort"


def parse_args() -> argparse.Namespace:
    """Parse commandline arguments.

    Generates two subparsers:
    - analyze: Given an image (or a directory thereof), determine the image's dominant colors. Graphics saved to
    disk at the supplied location.
    - sort: Given a directory, perform color analysis on all images therein, then save copies named by sorted order.

    Returns:
        argparse.Namespace: The arguments parsed from the commandline interface.
    """
    main_parser = argparse.ArgumentParser(description="CoLoRsOrT!")
    subparsers = main_parser.add_subparsers(dest="command")

    # common args
    subparser_parent = argparse.ArgumentParser(add_help=False)
    subparser_parent.add_argument("input", type=Path, help="Input directory of .jpg files (or a single .jpg file).")
    subparser_parent.add_argument(
        "--n",
        type=int,
        default=conf.DEFAULT_N_CLUSTERS,
        help="Number of clusters to use for determining dominant colors.",
    )
    subparser_parent.add_argument(
        "--auto_n_heuristic",
        type=HeuristicName,
        default=HeuristicName.AUTO_N_BINNED_WITH_THRESHOLD,
        help="The heuristic used to set `n` for the clustering algorithm.",
    )
    subparser_parent.add_argument(
        "--no_enhance", action="store_true", help="Enhance the colors that are computed for this image."
    )
    subparser_parent.add_argument(
        "--orientation",
        type=str,
        default=ImageOrientation.HORIZONTAL,
        help="The stacking orientation of any output graphics.",
    )
    subparser_parent.add_argument("--visualize", action="store_true", help="Visualize graphics before saving them.")
    subparser_parent.add_argument(
        "--output_dir",
        type=Path,
        default=Path(conf.DEFAULT_OUTPUT_DIR),
        help="Output directory for sorted .jpg files.",
    )
    subparser_parent.add_argument(
        "--chips",
        action="store_true",
        help="Save chips for each image.",
    )

    # analyze subparser
    analyze_subparser = subparsers.add_parser(ANALYZE_PARSER, parents=[subparser_parent], help="Analyze images.")
    analyze_subparser.add_argument(
        "--include_color_reduced",
        action="store_true",
        help="Store the original image reduced to its dominant colors.",
    )

    sort_subparser = subparsers.add_parser(
        SORT_PARSER, parents=[subparser_parent], help="Sort images by color (also performs analysis)."
    )
    sort_subparser.add_argument(
        "--spectrum",
        action="store_true",
        help="Save spectrum image for the current collection of images.",
    )
    sort_subparser.add_argument("--anchor", type=str, help="Name of the first file in the sorted output sequence.")
    sort_subparser.add_argument("--reverse", action="store_true", help="Reverse the color sort order.")

    return main_parser.parse_args()


def main():
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    jpgs = [args.input] if args.input.is_file() else list(args.input.rglob("*.jpg"))

    print(f"Analyzing {len(jpgs)} images...")
    all_image_reps = []
    for jpg_path in tqdm(jpgs, ascii=True):
        all_image_reps.append(
            Image(
                image_path=jpg_path,
                resize_long_axis=conf.DEFAULT_RESIZE_LONG_AXIS,
                n_clusters=args.n,
                auto_n_heuristic=args.auto_n_heuristic,
                enhance=args.no_enhance,
            )
        )

    if args.command == SORT_PARSER:
        print("Sorting...")
        all_image_reps, _, _ = Image.colorsort(all_image_reps, args.anchor)

        print("Saving sorted images...")
        dest_dir = Path(f"{args.output_dir}/sorted/{timestamp}")
        for i, image_rep in enumerate(all_image_reps):
            sorted_image_dest = dest_dir / image_rep.generate_filename(i, "sorted")
            vis.save(image_rep, sorted_image_dest)

        if args.spectrum:
            print("Saving spectrum...")
            filename = f"{timestamp}_spectrum_n={args.n}_enhance={args.enhance}.jpg"
            spectrum_dest = Path(f"{args.output_dir}/spectrums/{filename}")
            vis.save_spectrum_visualization(all_image_reps, spectrum_dest)

        print("Done!")

    if args.chips:
        print("Saving chips...")
        dest_dir = Path(f"{args.output_dir}/chips/{timestamp}")
        for i, image_rep in enumerate(all_image_reps):
            chips_dest = dest_dir / image_rep.generate_filename(i, "chips")
            vis.save_chips_visualization(image_rep, chips_dest, orientation=ImageOrientation.AUTO)


if __name__ == "__main__":
    main()

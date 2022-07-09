#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

import colorsort.config as config
import colorsort.util as util
import colorsort.visualization as visualization
from colorsort.analyzed_image import AnalyzedImage
from colorsort.heuristics import NHeuristic

ANALYZE_PARSER = "analyze"
SORT_PARSER = "sort"


def parse_args() -> argparse.Namespace:
    """Parse commandline arguments.

    Generates two subparsers:
    - analyze: Given an image (or a directory thereof), determine the image's dominant colors. Graphics are saved
        to disk at the supplied location.
    - sort: Given a directory, perform color analysis on all images therein, sort them by their dominant hue,
        then save copies prefixed with sorted order.

    Returns:
        argparse.Namespace: The arguments parsed from the commandline interface.
    """
    main_parser = argparse.ArgumentParser(description="ColorSort")
    subparsers = main_parser.add_subparsers(dest="command")

    # common args
    subparser_parent = argparse.ArgumentParser(add_help=False)
    subparser_parent.add_argument("input", type=Path, help="Input directory of .jpg files (or a single .jpg file).")
    subparser_parent.add_argument(
        "--algorithm",
        type=util.DominantColorAlgorithm,
        default=util.DominantColorAlgorithm.KMEANS,
        help="The algorithm to use for determining the dominant color of images (k-means clustering by default).",
    )
    subparser_parent.add_argument(
        "--n_colors",
        type=int,
        default=config.DEFAULT_N_COLORS,
        help="Number of dominant colors to compute.",
    )
    subparser_parent.add_argument(
        "--auto_n_heuristic",
        type=NHeuristic,
        default=NHeuristic.AUTO_N_BINNED_WITH_THRESHOLD,
        help="The heuristic used to set `n` for the clustering algorithm.",
    )
    subparser_parent.add_argument(
        "--orientation",
        type=str,
        default=util.ImageOrientation.AUTO,
        help="The stacking orientation of any output graphics.",
    )
    subparser_parent.add_argument(
        "--output_dir",
        type=Path,
        default=Path(config.DEFAULT_OUTPUT_DIR),
        help="Output directory for sorted .jpg files.",
    )
    subparser_parent.add_argument(
        "--save_dominant_color_visualization",
        action="store_true",
        help="Save dominant color visualization for each image.",
    )
    subparser_parent.add_argument(
        "--include_remapped_image",
        action="store_true",
        help="Include remapped image in chips visualization. Ignored if not using KMEANS algorithm.",
    )
    subparser_parent.add_argument(
        "--display",
        action="store_true",
        help="Display generated graphics.",
    )

    # analyze subparser
    _ = subparsers.add_parser(ANALYZE_PARSER, parents=[subparser_parent], help="Analyze images.")

    # sort subparser
    sort_subparser = subparsers.add_parser(
        SORT_PARSER, parents=[subparser_parent], help="Sort images by color (also performs analysis)."
    )
    sort_subparser.add_argument(
        "--spectrum",
        action="store_true",
        help="Save spectrum image for the current collection of images.",
    )
    sort_subparser.add_argument(
        "--include_all_colors",
        action="store_true",
        help="Include all detected dominant colors in the spectrum graphic.",
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
            AnalyzedImage(
                image_path=jpg_path,
                resize_long_axis=config.DEFAULT_RESIZE_LONG_AXIS,
                dominant_color_algorithm=args.algorithm,
                n_colors=args.n_colors,
                auto_n_heuristic=args.auto_n_heuristic,
            )
        )

    if args.command == SORT_PARSER:
        print("Sorting...")
        all_image_reps, _, _ = AnalyzedImage.colorsort(all_image_reps, args.anchor)

        print("Saving sorted images...")
        dest_dir = Path(f"{args.output_dir}/sorted/{timestamp}")
        for i, image_rep in enumerate(all_image_reps):
            sorted_image_dest = dest_dir / image_rep.generate_filename(i, "sorted")
            visualization.save(image_rep, sorted_image_dest)

        if args.spectrum:
            print("Saving spectrum...")
            filename = f"{timestamp}_spectrum_n={args.n_colors}.jpg"
            spectrum_dest = Path(f"{args.output_dir}/spectrums/{filename}")
            print(args.include_all_colors)
            visualization.save_spectrum_visualization(
                all_image_reps, args.include_all_colors, spectrum_dest, args.display
            )

    if args.save_dominant_color_visualization:
        print("Saving chips...")
        dest_dir = Path(f"{args.output_dir}/chips/{timestamp}")
        for i, image_rep in enumerate(all_image_reps):
            chips_dest = dest_dir / image_rep.generate_filename(i, "chips")
            visualization.save_dominant_color_visualization(
                image_rep,
                chips_dest,
                visualization_orientation=args.orientation,
                include_remapped_image=args.include_remapped_image,
                display=args.display,
            )

    print("\nDominant colors:")
    for i, image in enumerate(all_image_reps):
        print(f"{i+1}. {image.get_pretty_string()}")


if __name__ == "__main__":
    main()

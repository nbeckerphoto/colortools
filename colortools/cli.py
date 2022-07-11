#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

from tqdm import tqdm
from colortools import __version__

import colortools.config as config
import colortools.util as util
import colortools.visualization as visualization
from colortools.analyzed_image import AnalyzedImage
from colortools.heuristics import NColorsHeuristic
from colortools.sort import colorsort

logging.basicConfig(format="%(levelname)s: %(message)s")


def parse_args() -> argparse.Namespace:
    """Parse commandline arguments.

    Returns:
        argparse.Namespace: The arguments parsed from the commandline interface.
    """
    parser = argparse.ArgumentParser(description="ColorTools")
    parser.add_argument("input", type=Path, help="Input directory of .jpg files (or a single .jpg file).")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--algorithm",
        "-a",
        type=util.DominantColorAlgorithm,
        default=config.DEFAULT_DOMINANT_COLOR_ALGORITHM,
        help="The algorithm to use for determining the dominant color of images (k-means clustering by default).",
    )
    parser.add_argument(
        "--n_colors",
        "-n",
        type=int,
        default=config.DEFAULT_N_COLORS,
        help="Number of dominant colors to compute.",
    )
    parser.add_argument(
        "--n_colors_heuristic",
        type=NColorsHeuristic,
        default=config.DEFAULT_N_COLORS_HEURISTIC,
        help="The heuristic used to set `n` for the clustering algorithm.",
    )
    parser.add_argument(
        "--exclude_bw",
        action="store_true",
        help="Exclude black and white images from generated graphics.",
    )
    parser.add_argument(
        "--skip_sort", action="store_true", help="Skip sorting for the current set of analyzed images."
    )
    parser.add_argument("--sort_reverse", action="store_true", help="Reverse the image sort order.")
    parser.add_argument(
        "--sort_anchor",
        type=str,
        help="Anchor image with which to begin sorted sequence.",
    )
    parser.add_argument("--save_sorted", action="store_true", help="Save sorted sequence of images.")
    parser.add_argument(
        "--display",
        action="store_true",
        help="Display generated graphics in addition to saving them.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print a summary of the supplied arguments.")
    parser.add_argument(
        "--output_dir",
        "-o",
        type=Path,
        default=Path(config.DEFAULT_OUTPUT_DIR),
        help="Output directory for sorted .jpg files.",
    )
    parser.add_argument(
        "--dominant_colors",
        action="store_true",
        help="Save dominant color visualization for each image.",
    )
    parser.add_argument(
        "--dominant_colors_remapped",
        action="store_true",
        help="Include remapped image in dominant color visualization. Ignored if not using KMEANS algorithm.",
    )
    parser.add_argument(
        "--spectrum",
        action="store_true",
        help="Save spectrum image for the current collection of images.",
    )
    parser.add_argument(
        "--spectrum_all_colors",
        action="store_true",
        help="Include all detected dominant colors in the spectrum graphic.",
    )
    parser.add_argument("--collage", action="store_true", help="Save a collage of the analyzed images.")
    parser.add_argument(
        "--summary", action="store_true", help="Print a summary of the analyzed images to the console."
    )
    return parser.parse_args()


def check_args(args: argparse.Namespace) -> argparse.Namespace:
    """Check arguments for conflicts, issuing warnings and fixing arguments as needed.

    Args:
        args (argparse.Namespace): The arguments to check.

    Returns:
        argparse.Namespace: The checked arguments.
    """
    if args.skip_sort and args.save_sorted:
        logging.warning("Unable to save sorted images because skip_sort=True; ignoring save_sorted")
        args.save_sorted = False
    if not args.algorithm == util.DominantColorAlgorithm.KMEANS and args.dominant_colors_remapped:
        logging.warning("Unable to remap image using HUE_DIST algorithm; ignoring --dominant_colors_remapped")
        args.dominant_colors_remapped = False
    if not (args.save_sorted or args.dominant_colors or args.spectrum or args.collage):
        logging.warning("No output graphics are set to be generated! See usage (--help) for more details.")
    return args


def print_verbose_output(args: argparse.Namespace):
    """Print a verbose output for the provided arguments.

    Args:
        args (argparse.Namespace): The arguments for which to print verbose summary.
    """
    print()
    print("Analyze settings:")
    print(f"- input={args.input}")
    print(f"- algorithm={args.algorithm}")
    print(f"- n_colors={args.n_colors}")
    print(f"- n_colors_heuristic={args.n_colors_heuristic}")
    print()

    print("Action summary:")
    print(f"- Black and white images will {'not ' if args.exclude_bw else ''}be included")
    if not args.skip_sort:
        print(f"- Images will be sorted in {'reverse' if args.sort_reverse else 'standard'} order")
        if args.save_sorted:
            sorted_dir = f"{args.output_dir}/{config.DEFAULT_SORTED_DIR}"
            print(f"- Sorted images will be saved to {sorted_dir}")
        if args.sort_anchor:
            print(f"- Sort anchor image is {args.sort_anchor}")
    else:
        print("- Images will not be sorted")

    if args.dominant_colors:
        dominant_colors_dir = f"{args.output_dir}/{config.DEFAULT_DOMINANT_COLOR_DIR}"
        print(
            "- Saving dominant colors graphic "
            f"{'with remapped images ' if args.dominant_colors_remapped else ''}"
            f"to {dominant_colors_dir}"
        )

    if args.spectrum:
        spectrum_dir = f"{args.output_dir}/{config.DEFAULT_SPECTRUM_DIR}"
        print(
            "- Saving spectrum graphic "
            f"{'with all spectrum colors' if args.spectrum_all_colors else 'with dominant colors only'} "
            f"to {spectrum_dir}"
        )

    if args.collage:
        collage_dir = f"{args.output_dir}/{config.DEFAULT_COLLAGE_DIR}"
        print(f"- Saving collage graphic to {collage_dir}")

    if args.summary:
        print("- Summary will be printed at the end of processing")

    print()


def main():
    args = check_args(parse_args())
    timstamp_str = util.get_timestamp_string()
    jpg_paths = util.collect_jpg_paths(args.input)

    if args.verbose:
        print_verbose_output()

    print(f"Analyzing {len(jpg_paths)} images...")
    analyzed_images = []
    for jpg_path in tqdm(jpg_paths, ascii=True):
        analyzed_images.append(
            AnalyzedImage(
                image_path=jpg_path,
                resize_long_axis=config.DEFAULT_RESIZE_LONG_AXIS,
                dominant_color_algorithm=args.algorithm,
                n_colors=args.n_colors,
                auto_n_heuristic=args.n_colors_heuristic,
            )
        )

    if not args.skip_sort:
        analyzed_images, color_sorted, _ = colorsort(analyzed_images, args.sort_anchor)
        if args.exclude_bw:
            analyzed_images = color_sorted
        print("Sorting complete")

        if args.save_sorted:
            dest_dir = Path(f"{args.output_dir}/{config.DEFAULT_SORTED_DIR}/{timstamp_str}")
            for i, analyzed_image in enumerate(analyzed_images):
                sorted_image_dest = dest_dir / analyzed_image.generate_filename(i, "sorted")
                visualization.save(analyzed_image, sorted_image_dest)
            print(f"Saved sorted images to {dest_dir}")

    if args.dominant_colors or args.dominant_colors_remapped:
        dest_dir = Path(f"{args.output_dir}/{config.DEFAULT_DOMINANT_COLOR_DIR}/{timstamp_str}")
        for i, analyzed_image in enumerate(analyzed_images):
            dominant_colors_dest = dest_dir / analyzed_image.generate_filename(i, "dc")
            visualization.save_dominant_color_visualization(
                analyzed_image,
                config.DEFAULT_DOMINANT_COLOR_CHIP_SIZE,
                dominant_colors_dest,
                include_remapped_image=args.dominant_colors_remapped,
                display=args.display,
            )
        print(f"Saved dominant color graphics to {dest_dir}")

    if args.spectrum:
        filename = f"{timstamp_str}_spectrum.jpg"
        spectrum_dest = Path(f"{args.output_dir}/{config.DEFAULT_SPECTRUM_DIR}/{filename}")
        visualization.save_spectrum_visualization(
            analyzed_images, args.spectrum_all_colors, spectrum_dest, args.display
        )
        print(f"Saved spectrum graphic to {spectrum_dest}")

    if args.collage:
        filename = f"{timstamp_str}_collage_n.jpg"
        collage_dest = Path(f"{args.output_dir}/{config.DEFAULT_COLLAGE_DIR}/{filename}")
        visualization.save_image_collage(analyzed_images, collage_dest, args.display)
        print(f"Saved collage graphic to {collage_dest}")

    if args.summary:
        print("\nAnalyzed image summary:")
        for i, image in enumerate(analyzed_images):
            print(f"{i+1}. {image.get_pretty_string()}")


if __name__ == "__main__":
    main()

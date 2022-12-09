#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path
from typing import List

from tqdm import tqdm

import colortools.config as config
import colortools.sort as sort
import colortools.util as util
import colortools.visualization as visualization
from colortools import __version__
from colortools.analyzed_image import AnalyzedImage
from colortools.heuristics import NColorsHeuristic

logging.basicConfig(format="%(levelname)s: %(message)s")

# TODO tests


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse commandline arguments.

    Arguments:
        args (List[str]): The list of arguments for this run of ColorTools.

    Returns:
        argparse.Namespace: The arguments parsed from the commandline interface.
    """
    parser = argparse.ArgumentParser(description="Analyze and sort images by their dominant colors.")
    parser.add_argument("input", type=Path, help="input directory of .jpg files (or a single .jpg file)")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--algorithm",
        type=util.DominantColorAlgorithm,
        choices=[dca.value for dca in util.DominantColorAlgorithm],
        default=config.DEFAULT_DOMINANT_COLOR_ALGORITHM,
        help="algorithm to use for determining the dominant color of images (default kmeans)",
    )
    parser.add_argument(
        "--n_colors",
        "--n-colors",
        type=int,
        default=config.DEFAULT_N_COLORS,
        help="number of dominant colors to compute",
    )
    parser.add_argument(
        "--n_colors_heuristic",
        "--n-colors-heuristic",
        type=NColorsHeuristic,
        choices=[nch.value for nch in NColorsHeuristic],
        default=config.DEFAULT_N_COLORS_HEURISTIC,
        help="heuristic used to set `n` for the clustering algorithm",
    )
    parser.add_argument(
        "--skip_analysis_crop",
        "--skip-analysis-crop",
        action="store_true",
        help="Analyze images in their entirety, without any edge cropping.",
    )
    parser.add_argument(
        "--exclude_bw",
        "--exclude-bw",
        action="store_true",
        help="exclude black and white images from generated graphics",
    )
    parser.add_argument(
        "--exclude_color",
        "--exclude-color",
        action="store_true",
        help="exclude color images from generated graphics",
    )
    parser.add_argument(
        "--sort", type=sort.SortMethod, choices=[sm.value for sm in sort.SortMethod], default=None, help="sort images"
    )
    parser.add_argument("--sort_reverse", "--sort-reverse", action="store_true", help="reverse the image sort order")
    parser.add_argument(
        "--sort_anchor",
        type=str,
        help="anchor image with which to begin sorted sequence",
    )
    parser.add_argument("--save_sorted", "--save-sorted", action="store_true", help="save sorted sequence of images")
    parser.add_argument(
        "--display",
        action="store_true",
        help="display generated graphics in addition to saving them",
    )
    parser.add_argument("--verbose", action="store_true", help="print a summary of the supplied arguments")
    parser.add_argument(
        "--output_dir",
        "--output-dir",
        type=Path,
        default=Path(config.DEFAULT_OUTPUT_DIR),
        help="Output directory for sorted .jpg files.",
    )
    parser.add_argument(
        "--dominant_colors",
        "--dominant-colors",
        action="store_true",
        help="save dominant color visualization for each image",
    )
    parser.add_argument(
        "--dominant_colors_remapped",
        "--dominant-colors-remapped",
        action="store_true",
        help="include remapped image in dominant color visualization; ignored if not using kmeans algorithm",
    )
    parser.add_argument(
        "--spectrum",
        action="store_true",
        help="save spectrum image for the current collection of images",
    )
    parser.add_argument(
        "--spectrum_all_colors",
        "--spectrum-all-colors",
        action="store_true",
        help="include all detected dominant colors in the spectrum graphic",
    )
    parser.add_argument("--collage", action="store_true", help="save a collage of the analyzed images")
    parser.add_argument("--summary", action="store_true", help="print a summary of the analyzed images to the console")
    return parser.parse_args(args)


def check_args(args: argparse.Namespace) -> argparse.Namespace:
    """Check arguments for conflicts, issuing warnings and fixing arguments as needed.

    Args:
        args (argparse.Namespace): The arguments to check.

    Returns:
        argparse.Namespace: The checked arguments.
    """
    if args.save_sorted and not args.sort:
        logging.warning(f"--save_sorted enabled with no sort method; defaulting to {config.DEFAULT_SORT_METHOD}")
        args.sort = config.DEFAULT_SORT_METHOD
    if not args.sort:
        logging.warning("No sort method provided! Use --help to see valid values if you wish to sort your output.")
    if not args.algorithm == util.DominantColorAlgorithm.KMEANS and args.dominant_colors_remapped:
        logging.warning("Unable to remap image using hue_dist algorithm; ignoring --dominant_colors_remapped")
        args.dominant_colors_remapped = False
    if args.exclude_bw and args.exclude_color:
        logging.error("Cannot set both --exclude_bw and --exclude_color")
        return None
    if args.spectrum_all_colors:
        args.spectrum = True
    if not (
        args.summary
        or args.sort
        or args.save_sorted
        or args.dominant_colors
        or args.dominant_colors_remapped
        or args.spectrum
        or args.collage
    ):
        logging.error(
            "No output action selected; please select "
            "--summary, --sort, --save_sorted, --dominant_colors, --dominant_colors_remapped, or --spectrum"
        )
        return None
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
    print(f"- skip_analysis_crop={args.skip_analysis_crop}")
    print()

    print("Action summary:")
    print(f"- Black and white images will {'not ' if args.exclude_bw else ''}be included")
    print(f"- Color images images will {'not ' if args.exclude_color else ''}be included")
    if args.sort:
        print(
            f"- Images will be sorted by {args.sort.value} in {'reverse' if args.sort_reverse else 'standard'} order"
        )
        if args.save_sorted:
            sorted_dir = Path(args.output_dir, config.DEFAULT_SORTED_DIR)
            print(f"- Sorted images will be saved to {sorted_dir}")
        if args.sort_anchor:
            print(f"- Sort anchor image is {args.sort_anchor}")
    else:
        print("- Images will not be sorted")

    if args.dominant_colors or args.dominant_colors_remapped:
        dominant_colors_dir = Path(args.output_dir, config.DEFAULT_DOMINANT_COLOR_DIR)
        print(
            "- Saving dominant colors graphic "
            f"{'with remapped images ' if args.dominant_colors_remapped else ''}"
            f"to {dominant_colors_dir}"
        )

    if args.spectrum:
        spectrum_dir = Path(args.output_dir, config.DEFAULT_SPECTRUM_DIR)
        print(
            "- Saving spectrum graphic "
            f"{'with all spectrum colors' if args.spectrum_all_colors else 'with dominant colors only'} "
            f"to {spectrum_dir}"
        )

    if args.collage:
        collage_dir = Path(args.output_dir, config.DEFAULT_COLLAGE_DIR)
        print(f"- Saving collage graphic to {collage_dir}")

    if args.summary:
        print("- Summary will be printed at the end of processing")

    print()


def run():
    args = check_args(parse_args(sys.argv[1:]))
    if args:
        timstamp_str = util.get_timestamp_string()
        jpg_paths = util.collect_jpg_paths(args.input)

        if args.verbose:
            print_verbose_output(args)

        n_jpg_paths = len(jpg_paths)
        if n_jpg_paths == 0:
            print(f"No images found in {args.input}")
        else:
            print(f"Analyzing {n_jpg_paths} images...")
            analyzed_images = []
            edge_crop = 0 if args.skip_analysis_crop else config.DEFAULT_EDGE_CROP
            for jpg_path in tqdm(jpg_paths, ascii=True):
                analyzed_images.append(
                    AnalyzedImage(
                        image_path=jpg_path,
                        resize_long_axis=config.DEFAULT_RESIZE_LONG_AXIS,
                        edge_crop=edge_crop,
                        dominant_color_algorithm=args.algorithm,
                        n_colors=args.n_colors,
                        auto_n_heuristic=args.n_colors_heuristic,
                    )
                )

            if args.exclude_bw:
                analyzed_images, _ = sort.separate_color_and_bw(analyzed_images)
            if args.exclude_color:
                _, analyzed_image = sort.separate_color_and_bw(analyzed_images)

            if args.sort:
                sort_function = sort.get_sort_function(args.sort)
                analyzed_images = sort_function(analyzed_images, args.sort_reverse, args.sort_anchor)
                n_sorted = len(analyzed_images)

                if args.save_sorted:
                    dest_dir = Path(args.output_dir, config.DEFAULT_SORTED_DIR, timstamp_str)
                    for i, analyzed_image in enumerate(analyzed_images):
                        sorted_image_dest = Path(dest_dir, analyzed_image.generate_filename(i, "sorted"))
                        visualization.save(analyzed_image, sorted_image_dest)
                    print(f"Saved {n_sorted} sorted images to {dest_dir}")
                else:
                    print(f"Sorted {n_sorted} images:")
                    for i, image in enumerate(analyzed_images):
                        print(f"{i+1:4.0f}. {image.image_path}")

            if args.dominant_colors or args.dominant_colors_remapped:
                dest_dir = Path(args.output_dir, config.DEFAULT_DOMINANT_COLOR_DIR, timstamp_str)
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
                spectrum_dest = Path(args.output_dir, config.DEFAULT_SPECTRUM_DIR, filename)
                visualization.save_spectrum_visualization(
                    analyzed_images,
                    args.spectrum_all_colors,
                    config.DEFAULT_SPECTRUM_HEIGHT,
                    spectrum_dest,
                    args.display,
                )
                print(f"Saved spectrum graphic to {spectrum_dest}")

            if args.collage:
                filename = f"{timstamp_str}_collage.jpg"
                collage_dest = Path(args.output_dir, config.DEFAULT_COLLAGE_DIR, filename)
                visualization.save_image_collage(
                    analyzed_images, config.DEFAULT_COLLAGE_WIDTH, collage_dest, args.display
                )
                print(f"Saved collage graphic to {collage_dest}")

            if args.summary:
                print("\nAnalyzed image summary:")
                for i, image in enumerate(analyzed_images):
                    print(f"{i+1}. {image.get_pretty_string()}")

#!/usr/bin/env python3
import argparse
from pathlib import Path

from tqdm import tqdm

import colorsort.config as config
import colorsort.util as util
import colorsort.visualization as visualization
from colorsort.analyzed_image import AnalyzedImage
from colorsort.heuristics import NColorsHeuristic
from colorsort.sort import colorsort


def parse_args() -> argparse.Namespace:
    """Parse commandline arguments.

    Returns:
        argparse.Namespace: The arguments parsed from the commandline interface.
    """
    parser = argparse.ArgumentParser(description="ColorSort")
    parser.add_argument("input", type=Path, help="Input directory of .jpg files (or a single .jpg file).")
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
        "--skip_sort", action="store_true", help="Skip sorting for the current set of analyzed images."
    )
    parser.add_argument("--save_sorted", action="store_true", help="Save sorted sequence of images.")
    parser.add_argument(
        "--sort_anchor",
        type=str,
        help="Anchor image with which to begin sorted sequence.",
    )
    parser.add_argument("--sort_reverse", action="store_true", help="Reverse the image sort order.")
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
    parser.add_argument(
        "--exclude_bw",
        action="store_true",
        help="Exclude black and white images from generated graphics.",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Display generated graphics in addition to saving them.",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    timstamp_str = util.get_timestamp_string()
    jpg_paths = util.collect_jpg_paths(args.input)

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
        print("Sorting...")
        analyzed_images, color_sorted, _ = colorsort(analyzed_images, args.sort_anchor)
        if args.exclude_bw:
            analyzed_images = color_sorted

        if args.save_sorted:
            print("Saving sorted images...")
            dest_dir = Path(f"{args.output_dir}/{config.DEFAULT_SORTED_DIR}/{timstamp_str}")
            for i, analyzed_image in enumerate(analyzed_images):
                sorted_image_dest = dest_dir / analyzed_image.generate_filename(i, "sorted")
                visualization.save(analyzed_image, sorted_image_dest)

    if args.skip_sort and args.save_sorted:
        print("Ignoring option '--save_sorted' (--skip_sort=True)")

    if args.dominant_colors or args.dominant_colors_remapped:
        print("Saving dominant colors visualization...")
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

    if args.spectrum:
        print("Saving spectrum...")
        filename = f"{timstamp_str}_spectrum.jpg"
        spectrum_dest = Path(f"{args.output_dir}/{config.DEFAULT_SPECTRUM_DIR}/{filename}")
        visualization.save_spectrum_visualization(
            analyzed_images, args.spectrum_all_colors, spectrum_dest, args.display
        )

    if args.collage:
        print("Saving collage...")
        filename = f"{timstamp_str}_collage_n.jpg"
        spectrum_dest = Path(f"{args.output_dir}/{config.DEFAULT_COLLAGE_DIR}/{filename}")
        visualization.save_image_collage(analyzed_images, spectrum_dest, args.display)

    if args.summary:
        print("\nAnalyzed colors:")
        for i, image in enumerate(analyzed_images):
            print(f"{i+1}. {image.get_pretty_string()}")


if __name__ == "__main__":
    main()

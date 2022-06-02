import argparse
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

import colorsort.config as conf
import colorsort.visualization as vis
from colorsort.cs_image_representation import CsImageRepresentation


def parse_args():
    parser = argparse.ArgumentParser(description="CoLoRsOrT!")
    parser.add_argument("input_dir", type=Path, help="Input directory of .jpg files.")
    parser.add_argument(
        "--output_dir",
        default=Path(conf.DEFAULT_OUTPUT_DIR),
        type=Path,
        help="Output directory for sorted .jpg files.",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=conf.DEFAULT_N_CLUSTERS,
        help="Number of clusters to use for determining dominant colors.",
    )
    parser.add_argument(
        "--chips",
        action="store_true",
        help="Save chips for each image.",
    )
    parser.add_argument(
        "--spectrum",
        action="store_true",
        help="Save spectrum image for the current collection of images.",
    )
    parser.add_argument("--co", dest="color_only", action="store_true")
    parser.add_argument("--resolve", action="store_true")
    parser.add_argument("--enhance", action="store_true")
    parser.add_argument("--anchor", type=str, help="Name of the anchor file.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print(args)
    print(f"timestamp={timestamp}")

    # collect images and process images
    print("Finding images...")
    jpgs = list(args.input_dir.rglob("*.jpg"))
    all_image_reps = []

    print(f"Building representations for {len(jpgs)} images...")
    for jpg_path in tqdm(jpgs, ascii=True):
        all_image_reps.append(
            CsImageRepresentation(
                image_path=jpg_path,
                resize_long_axis=conf.DEFAULT_RESIZE_LONG_AXIS,
                n_clusters=args.n,
                resolve=args.resolve,
                enhance=args.enhance,
            )
        )

    print("Sorting...")
    combined, color, bw = CsImageRepresentation.colorsort(all_image_reps, args.anchor)

    print("Saving sorted images...")
    dest_dir = Path(f"{args.output_dir}/sorted/{timestamp}")
    for i, image_rep in enumerate(combined):
        sorted_image_dest = dest_dir / image_rep.get_filename(i, "sorted")
        vis.save(image_rep, sorted_image_dest)

    if args.chips:
        print("Saving chips...")
        dest_dir = Path(f"{args.output_dir}/chips/{timestamp}")
        for i, image_rep in enumerate(combined):
            # if not image_rep.is_bw:
            chips_dest = dest_dir / image_rep.get_filename(i, "chips")
            vis.save_chips_visualization(image_rep, chips_dest)

    if args.spectrum:
        print("Saving spectrum...")
        filename = f"{timestamp}_spectrum_n={args.n}_resolve={args.resolve}_enhance={args.enhance}.jpg"
        spectrum_dest = Path(f"{args.output_dir}/spectrums/{filename}")
        vis.save_spectrum_visualization(combined, spectrum_dest)

    print("Done!")

# ColorTools

A commandline tool for sorting images by their dominant color.

## Installation
Installation is simple using `pip`: 

```
$ pip install colortools
```

## Usage
```
$ colortools --help
usage: colortools [-h] [--version] [--algorithm ALGORITHM] [--n_colors N_COLORS] [--n_colors_heuristic N_COLORS_HEURISTIC] [--exclude_bw] [--skip_sort] [--sort_reverse]
                  [--sort_anchor SORT_ANCHOR] [--save_sorted] [--display] [--verbose] [--output_dir OUTPUT_DIR] [--dominant_colors] [--dominant_colors_remapped] [--spectrum]
                  [--spectrum_all_colors] [--collage] [--summary]
                  input

ColorTools

positional arguments:
  input                 Input directory of .jpg files (or a single .jpg file).

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --algorithm ALGORITHM, -a ALGORITHM
                        The algorithm to use for determining the dominant color of images (k-means clustering by default).
  --n_colors N_COLORS, -n N_COLORS
                        Number of dominant colors to compute.
  --n_colors_heuristic N_COLORS_HEURISTIC
                        The heuristic used to set `n` for the clustering algorithm.
  --exclude_bw          Exclude black and white images from generated graphics.
  --skip_sort           Skip sorting for the current set of analyzed images.
  --sort_reverse        Reverse the image sort order.
  --sort_anchor SORT_ANCHOR
                        Anchor image with which to begin sorted sequence.
  --save_sorted         Save sorted sequence of images.
  --display             Display generated graphics in addition to saving them.
  --verbose             Print a summary of the supplied arguments.
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        Output directory for sorted .jpg files.
  --dominant_colors     Save dominant color visualization for each image.
  --dominant_colors_remapped
                        Include remapped image in dominant color visualization. Ignored if not using KMEANS algorithm.
  --spectrum            Save spectrum image for the current collection of images.
  --spectrum_all_colors
                        Include all detected dominant colors in the spectrum graphic.
  --collage             Save a collage of the analyzed images.
  --summary             Print a summary of the analyzed images to the console.
```

### Tests and Coverage
... can be run with 

```
$ coverage run -m pytest tests && coverage html && open htmlcov/index.html 
```


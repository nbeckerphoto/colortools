# ColorSort

A commandline tool for sorting images by their dominant color. Updates coming soon! 

## Usage
```
$ python cli.py --help
usage: cli.py [-h] [--algorithm ALGORITHM] [--n_colors N_COLORS] [--n_colors_heuristic N_COLORS_HEURISTIC] [--skip_sort] [--save_sorted] [--sort_anchor SORT_ANCHOR]
              [--sort_reverse] [--output_dir OUTPUT_DIR] [--dominant_colors] [--dominant_colors_remapped] [--spectrum] [--spectrum_all_colors] [--collage] [--summary]
              [--exclude_bw] [--display]
              input

ColorSort

positional arguments:
  input                 Input directory of .jpg files (or a single .jpg file).

optional arguments:
  -h, --help            show this help message and exit
  --algorithm ALGORITHM, -a ALGORITHM
                        The algorithm to use for determining the dominant color of images (k-means clustering by default).
  --n_colors N_COLORS, -n N_COLORS
                        Number of dominant colors to compute.
  --n_colors_heuristic N_COLORS_HEURISTIC
                        The heuristic used to set `n` for the clustering algorithm.
  --skip_sort           Skip sorting for the current set of analyzed images.
  --save_sorted         Save sorted sequence of images.
  --sort_anchor SORT_ANCHOR
                        Anchor image with which to begin sorted sequence.
  --sort_reverse        Reverse the image sort order.
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
  --exclude_bw          Exclude black and white images from generated graphics.
  --display             Display generated graphics in addition to saving them.
```

### Tests and Coverage
... can be run with 

```
$ coverage run -m pytest tests && coverage html && open htmlcov/index.html 
```

### v1.0.0 TODO
- Installable via `pip`
- Better argument checking/setting in CLI.
- ~~Clean up CLI options.~~
- ~~\>=90% test coverage~~
- ~~Image collage generation~~
- ~~Ensure that spectrum generation works with \>1 color per bar.~~
- ~~Ensure exact decimals are stored for dominant colors, and only cast to ints when needed~~
- ~~Git hooks for black and flake8~~

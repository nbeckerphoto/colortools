# ColorSort

A commandline tool for sorting images by their dominant color. Updates coming soon! 

## Usage
There are two main routines: `analyze` and `sort`.

```sh
$ python cli.py --help
usage: cli.py [-h] {analyze,sort} ...

ColorSort

positional arguments:
  {analyze,sort}
    analyze       Analyze images.
    sort          Sort images by color (also performs analysis).

optional arguments:
  -h, --help      show this help message and exit
```

### `analyze`

`analyze`: Given an image (or a directory thereof), determine the image's dominant colors. Graphics are saved to disk at the supplied location.

```sh
$ python cli.py analyze --help
usage: cli.py analyze [-h] [--algorithm ALGORITHM] [--n_colors N_COLORS] [--auto_n_heuristic AUTO_N_HEURISTIC] [--orientation ORIENTATION] [--output_dir OUTPUT_DIR]
                      [--save_dominant_color_visualization] [--include_remapped_image] [--exclude_black_and_white] [--display]
                      input

positional arguments:
  input                 Input directory of .jpg files (or a single .jpg file).

optional arguments:
  -h, --help            show this help message and exit
  --algorithm ALGORITHM
                        The algorithm to use for determining the dominant color of images (k-means clustering by default).
  --n_colors N_COLORS   Number of dominant colors to compute.
  --auto_n_heuristic AUTO_N_HEURISTIC
                        The heuristic used to set `n` for the clustering algorithm.
  --orientation ORIENTATION
                        The stacking orientation of any output graphics.
  --output_dir OUTPUT_DIR
                        Output directory for sorted .jpg files.
  --save_dominant_color_visualization
                        Save dominant color visualization for each image.
  --include_remapped_image
                        Include remapped image in chips visualization. Ignored if not using KMEANS algorithm.
  --exclude_black_and_white
                        Exclude black and white images from generated graphics.
  --display             Display generated graphics.
```

### `sort`

`sort`: Given a directory, perform color analysis on all images therein, sort them by their dominant hue, then save copies prefixed with sorted order. 

```sh
$ python cli.py sort --help   
usage: cli.py sort [-h] [--algorithm ALGORITHM] [--n_colors N_COLORS] [--auto_n_heuristic AUTO_N_HEURISTIC] [--orientation ORIENTATION] [--output_dir OUTPUT_DIR]
                   [--save_dominant_color_visualization] [--include_remapped_image] [--exclude_black_and_white] [--display] [--anchor ANCHOR] [--reverse] [--spectrum]
                   [--include_all_colors] [--collage]
                   input

positional arguments:
  input                 Input directory of .jpg files (or a single .jpg file).

optional arguments:
  -h, --help            show this help message and exit
  --algorithm ALGORITHM
                        The algorithm to use for determining the dominant color of images (k-means clustering by default).
  --n_colors N_COLORS   Number of dominant colors to compute.
  --auto_n_heuristic AUTO_N_HEURISTIC
                        The heuristic used to set `n` for the clustering algorithm.
  --orientation ORIENTATION
                        The stacking orientation of any output graphics.
  --output_dir OUTPUT_DIR
                        Output directory for sorted .jpg files.
  --save_dominant_color_visualization
                        Save dominant color visualization for each image.
  --include_remapped_image
                        Include remapped image in chips visualization. Ignored if not using KMEANS algorithm.
  --exclude_black_and_white
                        Exclude black and white images from generated graphics.
  --display             Display generated graphics.
  --anchor ANCHOR       Name of the first file in the sorted output sequence.
  --reverse             Reverse the color sort order.
  --spectrum            Save spectrum image for the current collection of images.
  --include_all_colors  Include all detected dominant colors in the spectrum graphic.
  --collage             Save a collage of the sorted images.
```

### Tests and Coverage
... can be run with 

```
$ coverage run -m pytest tests && coverage html && open htmlcov/index.html 
```

### v1.0.0 TODO
- Installable via `pip`
- ~~\>=90% test coverage~~
- ~~Image collage generation~~
- ~~Ensure that spectrum generation works with \>1 color per bar.~~
- ~~Ensure exact decimals are stored for dominant colors, and only cast to ints when needed~~
- ~~Git hooks for black and flake8~~

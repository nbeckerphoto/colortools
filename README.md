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
                      [--generate_chips_graphic] [--include_remapped_image] [--display]
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
  --generate_chips_graphic
                        Save chips visualization for each image.
  --include_remapped_image
                        Include remapped image in chips visualization. Ignored if not using KMEANS algorithm.
  --display             Display generated graphics.
```

### `sort`

`sort`: Given a directory, perform color analysis on all images therein, sort them by their dominant hue, then save copies prefixed with sorted order. 

```sh
$ python cli.py sort --help   
usage: cli.py sort [-h] [--algorithm ALGORITHM] [--n_colors N_COLORS] [--auto_n_heuristic AUTO_N_HEURISTIC] [--orientation ORIENTATION] [--output_dir OUTPUT_DIR]
                   [--generate_chips_graphic] [--include_remapped_image] [--display] [--spectrum] [--anchor ANCHOR] [--reverse]
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
  --generate_chips_graphic
                        Save chips visualization for each image.
  --include_remapped_image
                        Include remapped image in chips visualization. Ignored if not using KMEANS algorithm.
  --display             Display generated graphics.
  --spectrum            Save spectrum image for the current collection of images.
  --anchor ANCHOR       Name of the first file in the sorted output sequence.
  --reverse             Reverse the color sort order.
```

### Tests and Coverage
... can be run with 

```
$ coverage run -m pytest tests && coverage html
$ open htmlcov/index.html
```

### v1.0.0 TODO
- Installable via `pip`
- \>=80% test coverage
- Image collage generation
- Ensure that spectrum generation works with \>1 color per bar. 

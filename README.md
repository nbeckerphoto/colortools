# ColorSort

A commandline tool for sorting images by their dominant color. 

There are two main routines: `analyze` and `sort`.

```
$ python colorsort/cli.py --help
usage: cli.py [-h] {analyze,sort} ...

CoLoRsOrT!

positional arguments:
  {analyze,sort}
    analyze       Analyze images.
    sort          Sort images by color (also performs analysis).

optional arguments:
  -h, --help      show this help message and exit
```

`analyze`: Given an image (or a directory thereof), determine the image's dominant colors. Graphics saved to disk at the supplied location.
```
$ python colorsort/cli.py analyze --help
usage: cli.py analyze [-h] [--n N] [--auto_n_heuristic AUTO_N_HEURISTIC] [--no_enhance] [--orientation ORIENTATION] [--visualize] [--output_dir OUTPUT_DIR] [--chips]
                      [--include_color_reduced]
                      input

positional arguments:
  input                 Input directory of .jpg files (or a single .jpg file).

optional arguments:
  -h, --help            show this help message and exit
  --n N                 Number of clusters to use for determining dominant colors.
  --auto_n_heuristic AUTO_N_HEURISTIC
                        The heuristic used to set `n` for the clustering algorithm.
  --no_enhance          Enhance the colors that are computed for this image.
  --orientation ORIENTATION
                        The stacking orientation of any output graphics.
  --visualize           Visualize graphics before saving them.
  --output_dir OUTPUT_DIR
                        Output directory for sorted .jpg files.
  --chips               Save chips for each image.
  --include_color_reduced
                        Store the original image reduced to its dominant colors.
```

`sort`: Given a directory, perform color analysis on all images therein, then save copies named by sorted order.
```
$ python colorsort/cli.py sort --help   
usage: cli.py sort [-h] [--n N] [--auto_n_heuristic AUTO_N_HEURISTIC] [--no_enhance] [--orientation ORIENTATION] [--visualize] [--output_dir OUTPUT_DIR] [--chips] [--spectrum]
                   [--anchor ANCHOR] [--reverse]
                   input

positional arguments:
  input                 Input directory of .jpg files (or a single .jpg file).

optional arguments:
  -h, --help            show this help message and exit
  --n N                 Number of clusters to use for determining dominant colors.
  --auto_n_heuristic AUTO_N_HEURISTIC
                        The heuristic used to set `n` for the clustering algorithm.
  --no_enhance          Enhance the colors that are computed for this image.
  --orientation ORIENTATION
                        The stacking orientation of any output graphics.
  --visualize           Visualize graphics before saving them.
  --output_dir OUTPUT_DIR
                        Output directory for sorted .jpg files.
  --chips               Save chips for each image.
  --spectrum            Save spectrum image for the current collection of images.
  --anchor ANCHOR       Name of the first file in the sorted output sequence.
  --reverse             Reverse the color sort order.
```

Updates coming soon! 
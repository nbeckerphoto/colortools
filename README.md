# ColorTools

A commandline tool for analyzing and sorting images by their dominant colors.

## Installation
Installation is simple using `pip`: 

```
$ pip install colortools
```

## Usage
For details on how to use `ColorTools`, including many examples, see the included [`ColorTools` Tutorial](docs/colortools-tutorial.md). 

```
$ colortools --help
usage: colortools [-h] [--version] [--algorithm {hue_dist,kmeans}] [--n_colors N_COLORS]
                  [--n_colors_heuristic {auto_n_hue,auto_n_hue_binned,auto_n_binned_with_threshold,auto_n_simple_threshold}] [--skip_analysis_crop] [--exclude_bw]
                  [--exclude_color] [--sort {hue,saturation,value}] [--sort_reverse] [--sort_anchor SORT_ANCHOR] [--save_sorted] [--display] [--verbose]
                  [--output_dir OUTPUT_DIR] [--dominant_colors] [--dominant_colors_remapped] [--spectrum] [--spectrum_all_colors] [--collage] [--summary]
                  input

Analyze and sort images by their dominant colors.

positional arguments:
  input                 input directory of .jpg files (or a single .jpg file)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --algorithm {hue_dist,kmeans}
                        algorithm to use for determining the dominant color of images (default kmeans)
  --n_colors N_COLORS, --n-colors N_COLORS
                        number of dominant colors to compute
  --n_colors_heuristic {auto_n_hue,auto_n_hue_binned,auto_n_binned_with_threshold,auto_n_simple_threshold}, --n-colors-heuristic {auto_n_hue,auto_n_hue_binned,auto_n_binned_with_threshold,auto_n_simple_threshold}
                        heuristic used to set `n` for the clustering algorithm
  --skip_analysis_crop, --skip-analysis-crop
                        Analyze images in their entirety, without any edge cropping.
  --exclude_bw, --exclude-bw
                        exclude black and white images from generated graphics
  --exclude_color, --exclude-color
                        exclude color images from generated graphics
  --sort {hue,saturation,value}
                        sort images
  --sort_reverse, --sort-reverse
                        reverse the image sort order
  --sort_anchor SORT_ANCHOR
                        anchor image with which to begin sorted sequence
  --save_sorted, --save-sorted
                        save sorted sequence of images
  --display             display generated graphics in addition to saving them
  --verbose             print a summary of the supplied arguments
  --output_dir OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory for sorted .jpg files.
  --dominant_colors, --dominant-colors
                        save dominant color visualization for each image
  --dominant_colors_remapped, --dominant-colors-remapped
                        include remapped image in dominant color visualization; ignored if not using kmeans algorithm
  --spectrum            save spectrum image for the current collection of images
  --spectrum_all_colors, --spectrum-all-colors
                        include all detected dominant colors in the spectrum graphic
  --collage             save a collage of the analyzed images
  --summary             print a summary of the analyzed images to the console
```

### Building from Source
To build from source: 

```
$ python -m build
```

Then, to install the local build file using `pip`: 

```
$ pip install dist/npt_colortools-VERSION-none-any.whl
```

### Tests and Coverage
To run tests with `coverage`, generate an HTML report, and open the report: 

```
$ coverage run -m pytest tests && coverage html && open htmlcov/index.html 
```

### Known Issues
- First run after installation is _slow_.

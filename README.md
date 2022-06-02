# ColorSort

A commandline tool for sorting images by their dominant color. 

Usage: 

```
$ python colorsort/colorsort_cli.py --help
usage: colorsort_cli.py [-h] [--output_dir OUTPUT_DIR] [--n N] [--chips] [--spectrum] [--co] [--resolve] [--enhance] [--anchor ANCHOR] input_dir

CoLoRsOrT!

positional arguments:
  input_dir             Input directory of .jpg files.

optional arguments:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR
                        Output directory for sorted .jpg files.
  --n N                 Number of clusters to use for determining dominant colors.
  --chips               Save chips for each image.
  --spectrum            Save spectrum image for the current collection of images.
  --co
  --resolve
  --enhance
  --anchor ANCHOR       Name of the anchor file.
```

Updates coming soon! 
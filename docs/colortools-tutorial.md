# ColorTools Tutorial

## What is ColorTools?

ColorTools is a commandline interface (CLI) application for analyzing and sorting images by their dominant colors. 

At its core is an image analysis module, which performs color analysis on the provided images using one of a couple different algorithms. Once the images are analyzed, the results can be used for sorting images along a number of different dimensions, as well as generating numerous types of summary graphics. 

## Illustrated Examples

### Example 1 
The simplest way to use ColorTools is to simply point it to a directory of images and generate a summary of the results. 

For each image, a list of dominant colors is provided in both RGB and HSV. Dominant colors are represented as lists of length 3 (for [R, G, B] or [H, S, V]). 


```
$ colortools input/tutorial --summary
```

Note: you will see the following warning when the `--sort` option is omitted. This is expected and is intended as a reminder that the results will not be sorted. 

```
WARNING: No sort method provided! Use --help to see valid values if you wish to sort your output.
```

Output:
```
Analyzed image summary:
1. 1.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[1, 67, 180], [19, 40, 121]]
    hsv=[[218, 100, 70], [228, 84, 47]]
2. 2.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[210, 159, 73], [140, 105, 51]]
    hsv=[[38, 65, 82], [36, 64, 55]]
3. 3.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[229, 229, 229], [180, 180, 180]]
    hsv=[[330, 0, 90], [180, 0, 70]]
4. 4.jpg: n=4, algorithm=kmeans, color_space=lab 
    rgb=[[54, 35, 42], [113, 70, 84], [157, 122, 149], [244, 178, 155]]
    hsv=[[337, 35, 21], [340, 39, 44], [314, 22, 62], [15, 36, 96]]
5. 5.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[137, 157, 36], [60, 83, 6]]
    hsv=[[70, 77, 62], [78, 93, 32]]
6. 6.jpg: n=3, algorithm=kmeans, color_space=lab 
    rgb=[[236, 195, 199], [193, 130, 146], [50, 59, 95]]
    hsv=[[354, 17, 93], [345, 32, 76], [228, 48, 37]]
7. 7.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[79, 79, 79], [148, 148, 148]]
    hsv=[[323, 0, 31], [330, 0, 58]]
8. 8.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[46, 46, 46], [216, 216, 216]]
    hsv=[[323, 0, 18], [180, 0, 85]]
9. 9.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[49, 60, 89], [211, 174, 78]]
    hsv=[[223, 45, 35], [44, 63, 83]]
10. 10.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[151, 176, 203], [77, 102, 132]]
    hsv=[[211, 26, 80], [213, 42, 52]]
11. 11.jpg: n=3, algorithm=kmeans, color_space=lab 
    rgb=[[91, 131, 97], [102, 157, 74], [166, 90, 154]]
    hsv=[[129, 30, 51], [100, 53, 61], [309, 45, 65]]
12. 12.jpg: n=4, algorithm=kmeans, color_space=lab 
    rgb=[[79, 80, 93], [109, 97, 81], [225, 174, 26], [213, 181, 86]]
    hsv=[[235, 15, 37], [35, 26, 43], [45, 88, 88], [45, 60, 84]]
```


### Example 2
We could also sort the images by the hue of their dominant color.

```
$ colortools input/tutorial --sort hue
```

Output:
```
Sorted 12 images:
   1. input/tutorial/4.jpg
   2. input/tutorial/6.jpg
   3. input/tutorial/2.jpg
   4. input/tutorial/5.jpg
   5. input/tutorial/11.jpg
   6. input/tutorial/10.jpg
   7. input/tutorial/1.jpg
   8. input/tutorial/9.jpg
   9. input/tutorial/12.jpg
  10. input/tutorial/8.jpg
  11. input/tutorial/7.jpg
  12. input/tutorial/3.jpg
```


### Example 3
Or we could generate graphics depicting the dominant colors that were computed. (By default, all output graphics are saved to a folder in the current directory named `output`. If we wanted to change where these output graphics were saved, we could use the `--output-dir` argument.)

```
$ colortools input/tutorial --dominant_colors
```

Sample of resulting graphics: 

Image 1 | Image 2 | image 3
:------:|:-------:|:-------:
<img src="example-images/3/1.jpg" width="250">|<img src="example-images/3/2.jpg" width="250">|<img src="example-images/3/3.jpg" width="250">|


### Example 4
We can do the same thing with a different dominant color algorithm. Here's we'll use the `hue_dist` algorithm. 

```
$ colortools input/tutorial --dominant_colors --algorithm hue_dist
```

Sample of resulting graphics: 

Image 1 | Image 2 | image 3
:------:|:-------:|:-------:
<img src="example-images/4/1.jpg" width="250">|<img src="example-images/4/2.jpg" width="250">|<img src="example-images/4/3.jpg" width="250">|


### Example 5
Notice something about the results in the previous example? Many of the computed dominant colors are quite similar. (You probably saw a warning about this in the console after you ran this command.) This dominant color detection algorithm only works well for determining the _single_ most dominant color. 

To do that, we can use the `--n_colors` argument. 

```
$ colortools input/tutorial --dominant_colors --algorithm hue_dist --n_colors 1
```

Sample of resulting graphics: 

Image 1 | Image 2 | image 3
:------:|:-------:|:-------:
<img src="example-images/5/1.jpg" width="250">|<img src="example-images/5/2.jpg" width="250">|<img src="example-images/5/3.jpg" width="250">|


### Example 6
Without the `--n_colors` argument, the number of colors to find is determined dynamically. It is possible to use a different heuristic for setting the number of colors, but in general, these heuristics are mostly experimental. You can try them out using the `--n_colors-heuristic` argument. 

```
$ colortools input/tutorial --dominant_colors --n_colors_heuristic auto_n_hue
```

Sample of resulting graphics: 

Image 1 | Image 2 | image 3
:------:|:-------:|:-------:
<img src="example-images/6/1.jpg" width="250">|<img src="example-images/6/2.jpg" width="250">|<img src="example-images/6/3.jpg" width="250">|


### Example 7
If using the default `kmeans` algorithm for computing dominant colors, you are able to map each pixel of the original image to the closest dominant color using the `--dominant_colors_remapped` argument. (This argument is ignored if using the `hue_dist` algorithm.)

```
$ colortools input/tutorial --dominant_colors --dominant_colors_remapped
```

Image 1 | Image 2 | image 3
:------:|:-------:|:-------:
<img src="example-images/7/1.jpg" width="250">|<img src="example-images/7/2.jpg" width="250">|<img src="example-images/7/3.jpg" width="250">|


### Example 8
In addition to generating graphics for the dominant colors, we can also generate what I call a "spectrum" for the input images. Each bar in the spectrum represents the dominant color of one of the input images. 

```
$ colortools input/tutorial --spectrum
```

Output graphic: 

<img src="example-images/8/1.jpg" width="500">

### Example 9
Notice that each bar consists of only one color, even though multiple dominant colors were likely computed for each image. If we would like to include all of these colors in the spectrum graphic, we can use the `--spectrum-all-colors` argument. When this argument is used, each bar represents a distribution of dominant colors for the underlying input image. 

```
$ colortools input/tutorial --spectrum --spectrum_all_colors
```

Output graphic: 

<img src="example-images/9/1.jpg" width="500">

### Example 10
You can also generate collages of the input images. 

```
$ colortools input/tutorial --collage
```

Output graphic: 

<img src="example-images/10/1.jpg" width="500">


### Example 11
Collages on their own aren't too interesting, however. We can make them more interesting by sorting the images by their _hue_ before creating the collage. Let's also generate a sorted spectrum graphic while we're at it. 

Note when sorting by hue, black and white images always appear at the end of the sequence.

```
$ colortools input/tutorial --spectrum --collage --sort hue
```

Output graphics: 

<img src="example-images/11/1.jpg" width="500">

<img src="example-images/11/2.jpg" width="500">


### Example 12
We can reverse the sort order. 

```
$ colortools input/tutorial --spectrum --collage --sort hue --sort_reverse
```

Output graphics: 

<img src="example-images/12/1.jpg" width="500">

<img src="example-images/12/2.jpg" width="500">


### Example 13
We can also use a different method of sorting. Here, we'll sort the images by the _saturation_ of their dominant color. Results are returned in ascending order, with ties broken by the value of the dominant color, then by color. 

```
$ colortools input/tutorial --spectrum --collage --sort saturation
```

Output graphics: 

<img src="example-images/13/1.jpg" width="500">

<img src="example-images/13/2.jpg" width="500">


### Example 14
Or we can sort by the _value_ of the dominant color, which approximates brightness. Again, results are returned in ascending order. This time, ties are broken by the hue of the dominant color, then by saturation.

```
$ colortools input/tutorial --spectrum --collage --sort value
```

Output graphics: 

<img src="example-images/14/1.jpg" width="500">

<img src="example-images/14/2.jpg" width="500">


### Example 15
We can set an image as a sort anchor when we are sorting. When we do this, sort order is maintained, but the anchor image is used as the first image in the sequence.

In this example, we'll use this image (stored on my machine as `input/11.jpg`) as the anchor image: 

<img src="example-images/15/1.jpg" width="300">

```
$ colortools input/tutorial --spectrum --collage --sort hue --sort_anchor 11.jpg
```

Output graphics: 

<img src="example-images/15/2.jpg" width="500">

<img src="example-images/15/3.jpg" width="500">

Again, note that when sorting by hue, even when using a sort anchor, black and white images will appear at the end of the sorted sequence. 


### Example 16
However, if we wanted to, we could exclude black and white images from all output graphics. 

```
$ colortools input/tutorial --spectrum --collage --sort hue --sort_anchor 11.jpg --exclude_bw
```

Output graphics: 

<img src="example-images/16/1.jpg" width="500">

<img src="example-images/16/2.jpg" width="500">


### Example 17
It is also possible to generate all output graphic types with a single command. 

Some notes on the input arguments: 
- When `--dominant_colors-remapped` is provided, there is no need to also include `--dominant_colors`. 
- When `--sort_saved` is provided, there is no need to provide a value for `--sort`; the default sorting method is by _hue_. 

```
$ colortools input/tutorial --summary --dominant_colors_remapped --spectrum --collage --save_sorted
```

Summary printout: 
```
Analyzed image summary:
1. 4.jpg: n=4, algorithm=kmeans, color_space=lab 
    rgb=[[54, 35, 42], [113, 70, 84], [157, 122, 149], [244, 178, 155]]
    hsv=[[337, 35, 21], [340, 39, 44], [314, 22, 62], [15, 36, 96]]
2. 6.jpg: n=3, algorithm=kmeans, color_space=lab 
    rgb=[[236, 195, 199], [193, 130, 146], [50, 59, 95]]
    hsv=[[354, 17, 93], [345, 32, 76], [228, 48, 37]]
3. 2.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[210, 159, 73], [140, 105, 51]]
    hsv=[[38, 65, 82], [36, 64, 55]]
4. 5.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[137, 157, 36], [60, 83, 6]]
    hsv=[[70, 77, 62], [78, 93, 32]]
5. 11.jpg: n=3, algorithm=kmeans, color_space=lab 
    rgb=[[91, 131, 97], [102, 157, 74], [166, 90, 154]]
    hsv=[[129, 30, 51], [100, 53, 61], [309, 45, 65]]
6. 10.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[151, 176, 203], [77, 102, 132]]
    hsv=[[211, 26, 80], [213, 42, 52]]
7. 1.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[1, 67, 180], [19, 40, 121]]
    hsv=[[218, 100, 70], [228, 84, 47]]
8. 9.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[49, 60, 89], [211, 174, 78]]
    hsv=[[223, 45, 35], [44, 63, 83]]
9. 12.jpg: n=4, algorithm=kmeans, color_space=lab 
    rgb=[[79, 80, 93], [109, 97, 81], [225, 174, 26], [213, 181, 86]]
    hsv=[[235, 15, 37], [35, 26, 43], [45, 88, 88], [45, 60, 84]]
10. 8.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[46, 46, 46], [216, 216, 216]]
    hsv=[[323, 0, 18], [180, 0, 85]]
11. 7.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[79, 79, 79], [148, 148, 148]]
    hsv=[[323, 0, 31], [330, 0, 58]]
12. 3.jpg: n=2, algorithm=kmeans, color_space=lab 
    rgb=[[229, 229, 229], [180, 180, 180]]
    hsv=[[330, 0, 90], [180, 0, 70]]
```

Selected dominant color graphics with remapping: 

Image 1 | Image 2 | image 3
:------:|:-------:|:-------:
<img src="example-images/17/1.jpg" width="250">|<img src="example-images/17/2.jpg" width="250">|<img src="example-images/17/3.jpg" width="250">|

Spectrum graphic: 

<img src="example-images/17/4.jpg" width="500">

Collage graphic: 

<img src="example-images/17/5.jpg" width="500">

Finally, sorted images are saved to a folder named by the current timestamp in `output/sorted/`.

### Example 18

As of version 1.1.0, the default color space for all internal processing is [L\*a\*b*](https://en.wikipedia.org/wiki/CIELAB_color_space). However, you can still use the older RGB processing. 


```
$ colortools input/tutorial --summary --dominant_colors_remapped --color-space rgb
```

Image 1: 

RGB | L\*a\*b*
:------:|:-------:
<img src="example-images/18/1-rgb.jpg" width="250">|<img src="example-images/18/1-lab.jpg" width="250">

Image 2: 

RGB | L\*a\*b*
:------:|:-------:
<img src="example-images/18/2-rgb.jpg" width="250">|<img src="example-images/18/2-lab.jpg" width="250">

Image 3: 

RGB | L\*a\*b*
:------:|:-------:
<img src="example-images/18/3-rgb.jpg" width="250">|<img src="example-images/18/3-lab.jpg" width="250">

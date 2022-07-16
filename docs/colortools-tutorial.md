# ColorTools Tutorial

## What is ColorTools?

ColorTools is a commandline interface (CLI) application for analyzing and sorting images by their dominant colors. 

At its core is an image analysis module, which performs color analysis on the provided images using one of a couple different algorithms. Once the images are analyzed, the results can be used for sorting images along a number of different dimensions, as well as generating numerous types of summary graphics. 

## Illustrated Examples

### Example 1 
The simplest way to use ColorTools is to simply point it to a directory of images and generate a summary of the results.

```
$ colortools input/tutorial --summary
```

Output:
```
Analyzed image summary:
1. 8.jpg: n=1, algorithm=kmeans 
    rgb=[[62, 62, 62]]
    hsv=[[0, 0, 24]]
2. 9.jpg: n=2, algorithm=kmeans 
    rgb=[[46, 58, 86], [208, 173, 75]]
    hsv=[[222, 46, 34], [44, 64, 82]]
3. 12.jpg: n=5, algorithm=kmeans 
    rgb=[[87, 88, 101], [70, 67, 67], [119, 106, 87], [215, 180, 83], [222, 172, 12]]
    hsv=[[234, 14, 39], [0, 5, 27], [36, 27, 46], [44, 61, 84], [46, 95, 87]]
4. 11.jpg: n=3, algorithm=kmeans 
    rgb=[[104, 159, 95], [73, 109, 55], [162, 148, 168]]
    hsv=[[112, 40, 62], [101, 50, 43], [283, 12, 66]]
5. 10.jpg: n=1, algorithm=kmeans 
    rgb=[[122, 147, 176]]
    hsv=[[212, 30, 69]]
6. 4.jpg: n=4, algorithm=kmeans 
    rgb=[[56, 35, 42], [111, 72, 91], [156, 121, 147], [237, 173, 156]]
    hsv=[[339, 36, 22], [331, 35, 43], [315, 22, 61], [13, 34, 93]]
7. 5.jpg: n=1, algorithm=kmeans 
    rgb=[[100, 122, 20]]
    hsv=[[73, 84, 48]]
8. 7.jpg: n=1, algorithm=kmeans 
    rgb=[[98, 98, 98]]
    hsv=[[0, 0, 38]]
9. 6.jpg: n=5, algorithm=kmeans 
    rgb=[[230, 199, 209], [45, 55, 91], [241, 182, 178], [170, 115, 138], [216, 146, 153]]
    hsv=[[341, 13, 90], [226, 51, 36], [4, 26, 94], [335, 32, 67], [354, 32, 85]]
10. 2.jpg: n=1, algorithm=kmeans 
    rgb=[[173, 131, 60]]
    hsv=[[38, 65, 68]]
11. 3.jpg: n=1, algorithm=kmeans 
    rgb=[[220, 220, 220]]
    hsv=[[0, 0, 86]]
12. 1.jpg: n=1, algorithm=kmeans 
    rgb=[[1, 58, 162]]
    hsv=[[219, 99, 63]]
```

For each image, a list of dominant colors is provided in both RGB and HSV. Dominant colors are represented as lists of length 3 (for [R, G, B] or [H, S, V]). 


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
Notice something about the results in the previous example? Many of the computed dominant colors are quite similar. This dominant color detection algorithm only works well for determining the _single_ most dominant color. 

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

<p align="center">
<img src="example-images/8/1.jpg" width="500">
</p>

### Example 9
Notice that each bar consists of only one color, even though multiple dominant colors were likely computed for each image. If we would like to include all of these colors in the spectrum graphic, we can use the `--spectrum-all-colors` argument. When this argument is used, each bar represents a distribution of dominant colors for the underlying input image. 

```
$ colortools input/tutorial --spectrum --spectrum_all_colors
```

Output graphic: 

<p align="center">
<img src="example-images/9/1.jpg" width="500">
</p>

### Example 10
You can also generate collages of the input images. 

```
$ colortools input/tutorial --collage
```

Output graphic: 

<p align="center">
<img src="example-images/10/1.jpg" width="500">
</p>


### Example 11
Collages on their own aren't too interesting, however. We can make them more interesting by sorting the images by their _hue_ before creating the collage. Let's also generate a sorted spectrum graphic while we're at it. 

```
$ colortools input/tutorial --spectrum --collage --sort hue
```

Output graphics: 

<p align="center">
<img src="example-images/11/1.jpg" width="500">
<br>
<img src="example-images/11/2.jpg" width="500">
</p>


### Example 12
We can reverse the sort order. 

```
$ colortools input/tutorial --spectrum --collage --sort hue --sort_reverse
```

Output graphics: 

<p align="center">
<img src="example-images/12/1.jpg" width="500">
<br>
<img src="example-images/12/2.jpg" width="500">
</p>

Note that black and white images always appear at the end of the sequence when sorting by color.


### Example 13
We can also use a different method of sorting. Here, we'll sort the images by the _saturation_ of their dominant color. Results are returned in ascending order, with ties broken by the value of the dominant color, then by color. 

```
$ colortools input/tutorial --spectrum --collage --sort saturation
```

Output graphics: 

<p align="center">
<img src="example-images/13/1.jpg" width="500">
<br>
<img src="example-images/13/2.jpg" width="500">
</p>


### Example 14
Or we can sort by the _value_ of the dominant color, which approximates brightness. Again, results are returned in ascending order. This time, ties are broken by the hue of the dominant color, then by saturation.

```
$ colortools input/tutorial --spectrum --collage --sort value
```

Output graphics: 

<p align="center">
<img src="example-images/14/1.jpg" width="500">
<br>
<img src="example-images/14/2.jpg" width="500">
</p>


### Example 15
We can set an anchor images when we are sorting. When we do this, sort order is maintained, but the anchor image is used as the first image in the sequence. 

In this example, we'll use this image (stored on my machine as `input/11.jpg`) as the anchor image: 

<p align="center">
<img src="example-images/15/1.jpg" width="300">
</p>

```
$ colortools input/tutorial --spectrum --collage --sort hue --sort_anchor 11.jpg
```

Output graphics: 

<p align="center">
<img src="example-images/15/2.jpg" width="500">
<br>
<img src="example-images/15/3.jpg" width="500">
</p>

Again, note that when sorting by hue, black and white images always appear at the end of the sorted sequence. 


### Example 16
However, if we wanted to, we could exclude black and white images from all output graphics. 

```
$ colortools input/tutorial --spectrum --collage --sort hue --sort_anchor 11.jpg --exclude_bw
```

Output graphics: 

<p align="center">
<img src="example-images/16/1.jpg" width="500">
<br>
<img src="example-images/16/2.jpg" width="500">
</p>


### Example 17
It is also possible to generate all output graphic types with a single command. 

Note that when `--dominant_colors-remapped` is provided, there is no need to also include `--dominant_colors`. 

Note also that when `--sort_saved` is provided, there is no need to provide a value for `--sort`; the default sorting method is by _hue_. 

```
$ colortools input/tutorial --summary --dominant_colors_remapped --spectrum --collage --save_sorted
```

Summary printout: 
```
Analyzed image summary:
1. 4.jpg: n=4, algorithm=kmeans 
    rgb=[[56, 35, 42], [111, 72, 91], [156, 121, 147], [237, 173, 156]]
    hsv=[[339, 36, 22], [331, 35, 43], [315, 22, 61], [13, 34, 93]]
2. 6.jpg: n=5, algorithm=kmeans 
    rgb=[[230, 199, 209], [45, 55, 91], [241, 182, 178], [170, 115, 138], [216, 146, 153]]
    hsv=[[341, 13, 90], [226, 51, 36], [4, 26, 94], [335, 32, 67], [354, 32, 85]]
3. 2.jpg: n=1, algorithm=kmeans 
    rgb=[[173, 131, 60]]
    hsv=[[38, 65, 68]]
4. 5.jpg: n=1, algorithm=kmeans 
    rgb=[[100, 122, 20]]
    hsv=[[73, 84, 48]]
5. 11.jpg: n=3, algorithm=kmeans 
    rgb=[[104, 159, 95], [73, 109, 55], [162, 148, 168]]
    hsv=[[112, 40, 62], [101, 50, 43], [283, 12, 66]]
6. 10.jpg: n=1, algorithm=kmeans 
    rgb=[[122, 147, 176]]
    hsv=[[212, 30, 69]]
7. 1.jpg: n=1, algorithm=kmeans 
    rgb=[[1, 58, 162]]
    hsv=[[219, 99, 63]]
8. 9.jpg: n=2, algorithm=kmeans 
    rgb=[[46, 58, 86], [208, 173, 75]]
    hsv=[[222, 46, 34], [44, 64, 82]]
9. 12.jpg: n=5, algorithm=kmeans 
    rgb=[[87, 88, 101], [70, 67, 67], [119, 106, 87], [215, 180, 83], [222, 172, 12]]
    hsv=[[234, 14, 39], [0, 5, 27], [36, 27, 46], [44, 61, 84], [46, 95, 87]]
10. 8.jpg: n=1, algorithm=kmeans 
    rgb=[[62, 62, 62]]
    hsv=[[0, 0, 24]]
11. 7.jpg: n=1, algorithm=kmeans 
    rgb=[[98, 98, 98]]
    hsv=[[0, 0, 38]]
12. 3.jpg: n=1, algorithm=kmeans 
    rgb=[[220, 220, 220]]
    hsv=[[0, 0, 86]]
```

Selected dominant color graphics with remapping: 

Image 1 | Image 2 | image 3
:------:|:-------:|:-------:
<img src="example-images/4/1.jpg" width="250">|<img src="example-images/4/2.jpg" width="250">|<img src="example-images/4/3.jpg" width="250">|

Spectrum graphic: 

<p align="center">
<img src="example-images/17/4.jpg" width="500">
</p>

Collage graphic: 

<p align="center">
<img src="example-images/17/5.jpg" width="500">
</p>

Finally, sorted images are saved to a folder named by the current timestamp in `output/sorted/`. 
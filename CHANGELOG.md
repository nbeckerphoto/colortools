# Changelog
All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Next Release] - In Progress
### Added 
- Option for cropping edges before image analysis, including parameter in config and CLI option to skip analysis cropping. Updated tests (and fixed those that were broken due to new constructor signature for `AnalyzedImage`). 
- New `DEFAULT_N_COLORS_MAX` parameter in config (and removed hard-coded value in `heuristics.py`). 
- Upper limit on the size of output visualizations.

### Changed
- Updated default values: 
    - `DEFAULT_N_COLORS_MIN` to 2 instead of 1.
    - `DEFAULT_BAR_WIDTH` to 50 instead of 100. 
    - `DEFAULT_RESIZE_LONG_AXIS` to 500 instead of 400. 
- Use natural ordering for image processing order if not sorting output images.
- Removed imports from `config.py`.

### Fixed 
- Bug in which `DEFAULT_N_COLORS_MIN` was not being used.
- Bug in which `--spectrum` was not automatically enabled if `--spectrum_all_colors` was enabled.
- Erroneous type references of `np.array` changed to `np.ndarray`.


## [1.0.0-beta.2] - In Progress
### Added 
- Sort functions for sorting by saturation and value. 
- Many new tests, bringing coverage to 96%. Excluded `tests` folder from `coverage` reports with new entry in `pyproject.toml`.
- Configurable width in collages.
- Many additions to documentation: 
    - Missing docstrings
    - `docs/references.md`

### Changed
- Moved `cli.py` back into `colortools` module and moved call to `run()` to new `__main__.py` file.
- Refactored `sort.py`. 
- Set `AnalyzedImage.is_bw()` to return `True` if the saturation of the image's dominant color is less than 1. 
- Reorganized test image folders. 
- Minor tweaks to argument and enum option names. 
- Reduced minimum `n_colors` from auto N heuristics to from 2 to 1.
- Reverse vertical order of histogram bars in spectrum graphics.

### Fixed
- Minor bug that caused errors when instantiating `AnalyzedImage` for low-saturation images. 
- Enum parsing error for algorithm argument in CLI.


## [1.0.0-beta.1] - 10 Jul 2022
### Added 
- Scripts and configuration for pip package build.
- More tests.

## Changed
- Improved commandline interface and argument checking.
- Improved logging.
- Updated documentation.


## [0.3.0] - 10 Jul 2022
### Changed 
- Overhauled CLI: 
    - Removed subparsers `analyze` and `sort` and parameterized sorting. Graphics can now be generated independent of sorting.
    - Made argument naming and ordering more consistent and logical.
    - Added additional argument checking.
    - Use configuration file more consistently.
- Cleaned up configuration file and some default settings.
- Moved `colorsort()` function out of `AnalyzedImage` class and into new `sort.py` file.
- Improved logging
- Renamed main directory from `colorsort` to `colortools`


## [0.2.0] - 9 Jul 2022
### Added
- Option for generating collages of sorted images.
- Option for ignoring black and white images in generated graphics.
- Many more tests, increasing coverage to 95%, including required test images.
- Configuration for running `black` and `flake8` as pre-commit hooks.

### Changed
- Removed dependency on OpenCV and rewrote all functionality using PIL.
- Restructured codebase.
- Tons of refactoring, addition of docstrings, and general code cleanup.
- Improved handling of floats vs. ints (by using lazy rounding).


## [0.1.0] - 2 Jun 2022
### Added
- Initial `ColorSort` work-in-progress codebase.

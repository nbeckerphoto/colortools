# Changelog
All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0-beta.2] - In Progress
### Added 
- Sort functions for sorting by saturation and value. 
- Many new tests, bringing coverage to 96%. Excluded `tests` folder from `coverage` reports with new entry in `pyproject.toml`.
- Many additions to documentation: 
    - Missing docstrings
    - `docs/references.md`

### Changed
- Moved `cli.py` back into `colortools` module and moved call to `run()` to new `__main__.py` file.
- Refactored `sort.py`. 
- Set `AnalyzedImage.is_bw()` to return `True` if the saturation of the image's dominant color is less than 1. 
- Reorganized test image folders. 
- Minor tweaks to argument and enum option names. 

### Fixed
- Minor bug that caused errors when instantiating `AnalyzedImage` for low-saturation images. 


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

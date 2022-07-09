# Changelog
All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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

import logging
import sys
from pathlib import Path

import colortools.cli as cli
import colortools.config as config
import pytest
from colortools import __version__
from colortools.sort import SortMethod
from colortools.util import ColorSpace, DominantColorAlgorithm, collect_jpg_paths

TEST_IMAGE_DIR = "tests/test_images/test_analyzed_image"
TEST_IMAGE_FILE = f"{TEST_IMAGE_DIR}/red-blue.jpg"


@pytest.fixture(autouse=True)
def fast_resize(monkeypatch):
    """Shrink AnalyzedImage's resize target so run() tests over real fixture images stay fast."""
    monkeypatch.setattr(config, "DEFAULT_RESIZE_LONG_AXIS", 50)


def base_args(**overrides):
    """Build a parsed args namespace with --summary as the default output action, plus given overrides."""
    argv = [TEST_IMAGE_DIR, "--summary"]
    for key, value in overrides.items():
        flag = f"--{key}"
        if value is True:
            argv.append(flag)
        elif value is not False and value is not None:
            argv.extend([flag, str(value)])
    return cli.parse_args(argv)


def run_cli(monkeypatch, argv):
    """Run the CLI's run() entrypoint as if invoked with the given argv."""
    monkeypatch.setattr(sys, "argv", ["colortools"] + argv)
    cli.run()


# --- parse_args ---


def test_parse_args_defaults():
    """With no flags, parse_args fills in the documented config defaults."""
    args = cli.parse_args([TEST_IMAGE_DIR])
    assert args.input == Path(TEST_IMAGE_DIR)
    assert args.algorithm == config.DEFAULT_DOMINANT_COLOR_ALGORITHM
    assert args.color_space == config.DEFAULT_COLOR_SPACE
    assert args.n_colors == config.DEFAULT_N_COLORS
    assert args.sort is None


def test_parse_args_choices():
    """--algorithm, --color_space, --sort, and --sort_reverse parse to their corresponding enum members/flags."""
    args = cli.parse_args(
        [TEST_IMAGE_DIR, "--algorithm", "kmeans", "--color_space", "lab", "--sort", "hue", "--sort_reverse"]
    )
    assert args.algorithm == DominantColorAlgorithm.KMEANS
    assert args.color_space == ColorSpace.LAB
    assert args.sort == SortMethod.HUE
    assert args.sort_reverse is True


def test_parse_args_version(capsys):
    """--version exits immediately and prints this package's actual version string."""
    with pytest.raises(SystemExit):
        cli.parse_args(["--version"])
    captured = capsys.readouterr()
    assert captured.out.strip() == __version__


# --- check_args ---


def test_check_args_save_sorted_defaults_sort_method(caplog):
    """--save_sorted with no --sort falls back to the configured default sort method, with a warning."""
    args = base_args(save_sorted=True)
    with caplog.at_level(logging.WARNING):
        checked = cli.check_args(args)
    assert checked.sort == config.DEFAULT_SORT_METHOD
    assert "defaulting to" in caplog.text


def test_check_args_no_sort_warns(caplog):
    """Omitting --sort entirely logs a warning pointing the user at --help."""
    args = base_args()
    with caplog.at_level(logging.WARNING):
        cli.check_args(args)
    assert "No sort method provided" in caplog.text


def test_check_args_remapped_ignored_for_hue_dist(caplog):
    """--dominant_colors_remapped is cleared with a warning when the algorithm isn't kmeans."""
    args = base_args(algorithm="hue_dist", dominant_colors_remapped=True)
    with caplog.at_level(logging.WARNING):
        checked = cli.check_args(args)
    assert checked.dominant_colors_remapped is False
    assert "ignoring --dominant_colors_remapped" in caplog.text


def test_check_args_color_space_ignored_for_hue_dist(caplog):
    """--color_space lab is reset to rgb with a warning when the algorithm isn't kmeans."""
    args = base_args(algorithm="hue_dist", color_space="lab")
    with caplog.at_level(logging.WARNING):
        checked = cli.check_args(args)
    assert checked.color_space == ColorSpace.RGB
    assert "ignoring --color_space" in caplog.text


def test_check_args_hue_dist_n_colors_warns_once(caplog):
    """hue_dist with n_colors != 1 logs a single warning upfront, not once per image."""
    args = base_args(algorithm="hue_dist")
    with caplog.at_level(logging.WARNING):
        cli.check_args(args)
    assert caplog.text.count("dominant colors may be very similar") == 1


def test_check_args_hue_dist_n_colors_1_no_warning(caplog):
    """hue_dist with an explicit n_colors=1 doesn't warn, since colors won't be similar."""
    args = base_args(algorithm="hue_dist", n_colors=1)
    with caplog.at_level(logging.WARNING):
        cli.check_args(args)
    assert "dominant colors may be very similar" not in caplog.text


def test_check_args_exclude_both_errors(caplog):
    """Setting both --exclude_bw and --exclude_color is rejected outright."""
    args = base_args(exclude_bw=True, exclude_color=True)
    with caplog.at_level(logging.ERROR):
        checked = cli.check_args(args)
    assert checked is None
    assert "Cannot set both" in caplog.text


def test_check_args_spectrum_all_colors_enables_spectrum():
    """--spectrum_all_colors implicitly turns on --spectrum too."""
    args = base_args(spectrum_all_colors=True)
    checked = cli.check_args(args)
    assert checked.spectrum is True


def test_check_args_no_output_action_errors(caplog):
    """With no output action selected at all, check_args rejects the arguments."""
    args = cli.parse_args([TEST_IMAGE_DIR])
    with caplog.at_level(logging.ERROR):
        checked = cli.check_args(args)
    assert checked is None
    assert "No output action selected" in caplog.text


# --- print_verbose_output ---


def test_print_verbose_output(capsys):
    """The verbose summary reports the algorithm, color space, and sort settings that were configured."""
    args = base_args(algorithm="kmeans", color_space="rgb", sort="hue")
    checked = cli.check_args(args)
    cli.print_verbose_output(checked)
    captured = capsys.readouterr()
    assert "algorithm=" in captured.out and "KMEANS" in captured.out
    # color_space defaults to lab, so seeing RGB here proves the override was actually threaded through
    assert "color_space=" in captured.out and "RGB" in captured.out
    assert "Images will be sorted by hue" in captured.out


# --- run() ---


def test_run_no_images_found(tmp_path, monkeypatch, capsys):
    """Pointing at a directory with no images reports that fact instead of crashing."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    run_cli(monkeypatch, [str(empty_dir), "--summary"])
    captured = capsys.readouterr()
    assert "No images found" in captured.out


def test_run_invalid_args_returns_without_crash(tmp_path, monkeypatch, caplog):
    """An invalid argument combination is reported and run() exits cleanly rather than raising."""
    with caplog.at_level(logging.ERROR):
        run_cli(monkeypatch, [str(tmp_path)])  # no output action selected
    assert "No output action selected" in caplog.text


def test_run_summary(tmp_path, monkeypatch, capsys):
    """--summary prints a per-image summary block naming the analyzed file."""
    run_cli(monkeypatch, [TEST_IMAGE_FILE, "--summary", "--output_dir", str(tmp_path)])
    captured = capsys.readouterr()
    assert "Analyzed image summary" in captured.out
    assert "red-blue.jpg" in captured.out


def test_run_verbose(tmp_path, monkeypatch, capsys):
    """--verbose prints the settings summary ahead of the normal run output."""
    run_cli(monkeypatch, [TEST_IMAGE_FILE, "--summary", "--verbose", "--output_dir", str(tmp_path)])
    captured = capsys.readouterr()
    assert "Analyze settings" in captured.out


def test_run_sort_and_save_sorted(tmp_path, monkeypatch):
    """--save_sorted writes exactly one sorted output file per input image."""
    n_input_images = len(collect_jpg_paths(TEST_IMAGE_DIR))
    run_cli(monkeypatch, [TEST_IMAGE_DIR, "--sort", "hue", "--save_sorted", "--output_dir", str(tmp_path)])
    sorted_files = list((tmp_path / config.DEFAULT_SORTED_DIR).glob("*/*.jpg"))
    assert len(sorted_files) == n_input_images


def test_run_sort_without_save_sorted_prints_order(tmp_path, monkeypatch, capsys):
    """Without --save_sorted, the sorted order is printed listing every input image by name."""
    input_names = [path.name for path in collect_jpg_paths(TEST_IMAGE_DIR)]
    run_cli(monkeypatch, [TEST_IMAGE_DIR, "--sort", "hue", "--output_dir", str(tmp_path)])
    captured = capsys.readouterr()
    assert "Sorted" in captured.out and "images:" in captured.out
    for name in input_names:
        assert name in captured.out


def test_run_exclude_bw_only_color_images_remain(tmp_path, monkeypatch, capsys):
    """--exclude_bw drops black/white/gray images from the analyzed set, keeping color ones."""
    run_cli(monkeypatch, [TEST_IMAGE_DIR, "--exclude_bw", "--summary", "--output_dir", str(tmp_path)])
    captured = capsys.readouterr()
    assert "100-by-100-black.jpg" not in captured.out
    assert "100-by-100-white.jpg" not in captured.out
    assert "100-by-100-gray.jpg" not in captured.out
    assert "100-by-100-red.jpg" in captured.out


def test_run_exclude_color_only_bw_images_remain(tmp_path, monkeypatch, capsys):
    """--exclude_color drops non-grayscale images from the analyzed set, keeping black/white/gray ones."""
    run_cli(monkeypatch, [TEST_IMAGE_DIR, "--exclude_color", "--summary", "--output_dir", str(tmp_path)])
    captured = capsys.readouterr()
    assert "100-by-100-red.jpg" not in captured.out
    assert "100-by-100-black.jpg" in captured.out
    assert "100-by-100-white.jpg" in captured.out


def test_run_dominant_colors_and_remapped(tmp_path, monkeypatch):
    """--dominant_colors with --dominant_colors_remapped saves one visualization for the single input image."""
    run_cli(
        monkeypatch,
        [
            TEST_IMAGE_FILE,
            "--algorithm",
            "kmeans",
            "--n_colors",
            "2",
            "--dominant_colors",
            "--dominant_colors_remapped",
            "--output_dir",
            str(tmp_path),
        ],
    )
    dc_files = list((tmp_path / config.DEFAULT_DOMINANT_COLOR_DIR).glob("*/*.jpg"))
    assert len(dc_files) == 1


def test_run_spectrum_all_colors(tmp_path, monkeypatch):
    """--spectrum_all_colors with kmeans runs end to end and saves exactly one spectrum graphic."""
    run_cli(
        monkeypatch,
        [
            TEST_IMAGE_DIR,
            "--algorithm",
            "kmeans",
            "--spectrum_all_colors",
            "--output_dir",
            str(tmp_path),
        ],
    )
    spectrum_files = list((tmp_path / config.DEFAULT_SPECTRUM_DIR).glob("*.jpg"))
    assert len(spectrum_files) == 1


def test_run_collage(tmp_path, monkeypatch):
    """--collage saves exactly one collage graphic for the input directory."""
    run_cli(monkeypatch, [TEST_IMAGE_DIR, "--collage", "--output_dir", str(tmp_path)])
    collage_files = list((tmp_path / config.DEFAULT_COLLAGE_DIR).glob("*.jpg"))
    assert len(collage_files) == 1

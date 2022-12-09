# Update Notes

## Uploading to PyPI 

1. Build 

```
$ python -m build
```

2. Upload to TestPyPI

```
$ twine upload -r testpypi dist/*
```

3. Test pip installation

```
$ python3 -m venv venv-test
$ source venv-test/bin/activate
$ (venv-test) pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ nbp-colortools
```

4. Upload to PyPI

```
$ twine upload dist/*
```

References: 
- [Using Twine](https://twine.readthedocs.io/en/stable/#using-twine)

## Update Checklist

- Test suite passes
- CHANGELOG is updated
- README is updated, if necessary
- Version number in `colortools/__init__.py` is updated
- Test package is build and uploaded to Test PyPI
- Test package is used to run all examples for tutorial
- All examples for tutorial are re-run; console output and sample images are updated
- Release branch is created and tutorial inspected
- Release branch merged (via PR) to main and tagged with version number
- Main merged to develop
- Package re-built and uploaded to PyPI

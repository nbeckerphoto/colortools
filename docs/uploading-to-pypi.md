# Uploading to PyPI 

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

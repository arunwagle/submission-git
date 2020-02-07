# Steps to deploy module to pypi
### Make sure we update the version in setup.py. If we try to upload the same version twice it throws and error.
### Every new deployment should be a new version

#TEST pypi API token
# pypi-AgENdGVzdC5weXBpLm9yZwIkYzgyYmNhNWYtMDM0Ni00NjBhLWExOTAtOGUyMmQ5MDcyMGNjAAIleyJwZXJtaXNzaW9ucyI6ICJ1c2VyIiwgInZlcnNpb24iOiAxfQAABiCNZOI10c8dZCF3XI_lJ8rXzsH7hGPtZ5zaxkY1n0D7JQ

#PYPI Token
# username: __token__
# pypi-AgEIcHlwaS5vcmcCJDZiYmU4ZGY0LTNjYTctNDhmOS1hYmQwLTI5MzdiNjlkZmExZAACJXsicGVybWlzc2lvbnMiOiAidXNlciIsICJ2ZXJzaW9uIjogMX0AAAYgE5OFm8CUUZgalGMXWuXeVHtlbiULaMuxeMAT_JNm_Kc

# Create distribution 
python3 setup.py sdist bdist_wheel

# Upload to pypi
python3 -m twine upload  --repository-url https://upload.pypi.org/legacy/ dist/*

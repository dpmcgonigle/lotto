# ########################################################################################
#   Lotto
# ########################################################################################
from distutils.core import setup

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = list(map(lambda line: line.rstrip('\n'), open('requirements.txt', 'r')))

setup(name='lotto',
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      author='Dan McGonigle',
      long_description_content_type="text/markdown",
      packages=setuptools.find_packages(exclude=["test"]),
      install_requires=requirements,
      python_requires="~=3.11",
      )

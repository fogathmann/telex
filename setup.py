"""
This file is part of the telex project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jul 5, 2014.
"""
from setuptools import find_packages
from setuptools import setup

setup(name='telex',
      version='0.1',
      description='REST server for remote execution of command line tools.',
      author='F. Oliver Gathmann',
      author_email='fogathmann at gmail.com',
      license="MIT",
      packages=find_packages(),
      package_data={'': ["*.zcml"]},
      include_package_data=True,
      zip_safe=False,
      install_requires=['everest'],
      dependency_links=
        ['https://github.com/gathmann/telex/tarball/master#egg=telex-dev'],
      entry_points="""\
      [paste.app_factory]
      app = everest.run:app_factory
      """
      )

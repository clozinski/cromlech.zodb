from setuptools import setup, find_packages
import os

version = '0.1'

install_requires = [
    'setuptools',
    'cromlech.io',
    'transaction',
    'zope.interface',
    'zope.cachedescriptors',
    'zope.component',
    'zope.location',
    'ZODB3', # included Btrees
    ]

tests_require = [
    'zope.testing',
    ]

setup(name='cromlech.zodb',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['cromlech',],
      include_package_data=True,
      zip_safe=False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
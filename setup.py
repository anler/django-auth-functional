from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='auth_functional',
      version=version,
      description="Functional library for working with authentication and authorization in django",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django auth authentication authorization decorator functional',
      author='ikame',
      author_email='anler86@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

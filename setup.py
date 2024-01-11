# see https://github.com/pypa/sampleproject

import setuptools

import os
import sys

if sys.version_info < (3, 7):
    sys.exit('Minimum supported Python version is 3.7')

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Get the current version
exec(open("attotree/version.py").read())

setuptools.setup(
    name='attotree',
    version=VERSION,
    description='description',
    long_description=long_description,
    url='https://github.com/karel-brinda/attotree',
    author='Karel Brinda',
    author_email='karel.brinda@inria.fr',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: Unix',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='',
    packages=["attotree"],
    install_requires=[
        'wheel',
    ],
    package_data={
        'attotree': [
            '*.py',
        ],
    },
    entry_points={
        'console_scripts': [
            'attotree = attotree.attotree:main',
        ],
    },
)

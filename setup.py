import os

from setuptools import setup, find_packages

long_description = open('README.rst').read() if os.path.exists('README.rst') else\
    open('README.md').read()

setup(
    name='sofia',
    version='1.8.0',
    author='Liam H. Childs',
    author_email='liam.h.childs@gmail.com',
    packages=find_packages(exclude=['tests']),
    package_data={'templates': ['genomics/*.json', 'genomics/data/*']},
    url='https://github.com/childsish/sofia',
    license='LICENSE.txt',
    description='Software for the Flexible Integration of Annotation',
    long_description=long_description,
    install_requires=['lhc-python==1.3.9'],
    entry_points={
        'console_scripts': [
            'sofia = sofia.__main__:main'
        ]
    }
)

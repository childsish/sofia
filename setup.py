import os

from setuptools import setup, find_packages

long_description = open('README.rst').read() if os.path.exists('README.rst') else\
    open('README.md').read()

setup(
    name='sofia',
    version='1.7.2',
    author='Liam H. Childs',
    author_email='liam.h.childs@gmail.com',
    packages=find_packages(exclude=['test']),
    url='https://github.com/childsish/sofia',
    license='LICENSE.txt',
    description='Software for the Flexible Integration of Annotation',
    long_description=long_description,
    install_requires=['lhc-python'],
    entry_points={
        'console_scripts': [
            'sofia = sofia.__main__:main'
        ]
    }
)

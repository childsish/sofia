import os

from subprocess import Popen, PIPE
from setuptools import setup, find_packages

with open('README.rst', encoding='utf-8') if os.path.exists('README.rst') else \
        open('README.md', encoding='utf-8') as fileobj:
    long_description = fileobj.read()

if os.path.exists('.git'):
    prc = Popen(['git', 'describe', '--tags', '--dirty'],
                stdout=PIPE,
                cwd=os.path.dirname(os.path.realpath(__file__)))
    version, _ = prc.communicate()
    version = version.decode(encoding='utf-8').strip()
else:
    version = os.path.basename(os.path.dirname(os.path.realpath(__file__))).rsplit('-', 1)[1]

setup(
    name='sofia',
    version=version,
    author='Liam H. Childs',
    author_email='liam.h.childs@gmail.com',
    packages=find_packages(exclude=['tests']),
    package_data={'templates': ['genomics/*.json', 'genomics/data/*']},
    url='https://github.com/childsish/sofia',
    license='LICENSE.txt',
    description='Software for the Flexible Integration of Annotation',
    long_description=long_description,
    install_requires=['lhc-python==2.0.3'],
    entry_points={
        'console_scripts': [
            'sofia = sofia.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics']
)

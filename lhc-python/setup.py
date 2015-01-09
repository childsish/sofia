from distutils.core import setup

setup(
    name='lhc-python',
    version='0.0.1',
    author='Liam H. Childs',
    author_email='liam_childs@hotmail.com',
    packages=['lhc', 'lhc.test'],
    package_data={'lhc': ['data/*.dat']},
    scripts=[],
    url='https://github.com/childsish/lhc-python',
    license='LICENSE.txt',
    description='My python library of classes and functions that help me work',
    long_description=open('README.txt').read(),
    install_requires=['numpy', 'netCDF4'],
)

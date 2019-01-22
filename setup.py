"""A setuptools based setup module.

"""
import os

from setuptools import setup, find_packages



def read(file_name):
    try:
        return open(os.path.join(os.path.dirname(__file__), file_name)).read()
    except FileNotFoundError:
        return ''

setup(
    name='PyUBCG',
    version='0.1',
    description='Python implementation of UBCG pipeline',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='',
    author='',
    classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers, Biologist',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],
    keywords='phylogenetic tree',
    packages=find_packages(exclude=['tests']),
    install_requires=['pyyaml'],
    extras_require={
            'dev': ['pytest', 'pylint'],
        },
    entry_points={
        'console_scripts': [
            'pyubcg=PyUBCG.__main__:main',
        ],
    },
    test_suite='tests'

)
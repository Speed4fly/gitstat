from setuptools import setup

setup(
    name='gitstat',
    version='0.2.666666  scripts=['gitstat/gittools.py',],
    install_requires=['Click',
                      'PyInquirer',
                      'rich',
                      ],
    entry_points={
        'console_scripts': ['gitstat=gitstat.gittools:cli']
    },
)

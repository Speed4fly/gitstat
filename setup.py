from setuptools import setup

setup(
    name='gitstat',
    version='0.2.8',
    scripts=['gitstat/gittools.py',],
    install_requires=['Click',
                      'PyInquirer',
                      'rich',
                      ],
    long_description='README.md',
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': ['gitstat=gitstat.gittools:cli']
    },
)

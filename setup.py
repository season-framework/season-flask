import os
from setuptools import setup, find_packages

SRC_DIR = 'src'
SEASON_PKG_DIR = os.path.join(SRC_DIR, 'season')

setup(
    name='season',
    version='0.1.1',
    description='web framework',
    url='https://github.com/season-framework/season-flask',
    author='proin',
    author_email='proin@season.co.kr',
    license='MIT',
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    zip_safe=False,
    entry_points={'console_scripts': [
        'season = season.cmdtools:main [season]',
    ]},
    install_requires=[
        'flask',
        'watchdog'
    ],
    python_requires='>=3.6'
)
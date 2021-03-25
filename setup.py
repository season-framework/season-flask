import importlib.util
import os
from setuptools import setup, find_packages

SRC_DIR = 'src'
SEASON_PKG_DIR = os.path.join(SRC_DIR, 'season')

spec = importlib.util.spec_from_file_location('version', os.path.join(SEASON_PKG_DIR, 'version.py'))
version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version)

setup(
    name='season',
    version=version.VERSION_STRING,
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
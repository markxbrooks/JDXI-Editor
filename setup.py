from setuptools import setup, find_packages

setup(
    name="jdxi_manager",
    version="0.30",
    packages=find_packages(),
    install_requires=[
        "PySide6",
        "python-rtmidi",
    ],
    entry_points={
        'console_scripts': [
            'jdxi_manager=jdxi_manager.main:main',
        ],
    },
) 
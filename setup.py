import setuptools
import re

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="seabreeze-server",
    version="0.1.1",
    author="Jonathan D B Van Schenck",
    author_email="vanschej@oregonstate.edu",
    description="A TCP server to host the `python-seabreeze.cseabreeze` backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonathanvanschenck/python-seabreeze-server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    setup_requires = ['numpy'],
    install_requires = ['numpy>=1.18.2','future>=0.18.2',
                        'remote_object>=0.2.1','seabreeze>=1.0.1',
                        'seatease>=0.3']
)

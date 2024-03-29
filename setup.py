import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="strava-map",
    version="0.0.5",
    description="Create maps from your Strava Activities",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tcramm0nd/strava_map",
    author="tcramm0nd",
    author_email="25987791+tcramm0nd@users.noreply.github.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    install_requires=['folium>=0.12.1',
                      'pandas>=1.2.1',
                      'polyline>=1.4.0'
                      ],
    include_package_data=True
)

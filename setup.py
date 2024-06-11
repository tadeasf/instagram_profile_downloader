from setuptools import setup, find_packages

setup(
    name="instagram_profile_downloader",
    version="1.1.7",
    author="Tadeas Fort",
    author_email="taddy.fort@gmail.com",
    description="A tool to download all images and videos and story highlights from an Instagram profile.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tadeasf/instagram_profile_downloader",
    packages=find_packages(),
    install_requires=[
        "click",
        "rich-click",
        "opencv-python",
        "pillow",
        "loguru",
        "requests",
        "instaloader",
        "asyncio",
        "aiohttp",
        "setuptools",
    ],
    entry_points={
        "console_scripts": [
            "instagram_profile_downloader = instagram_profile_downloader.instagram_profile_downloader:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)

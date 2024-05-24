# Instagram Profile Downloader

## Overview

`instagram_profile_downloader` is a powerful and user-friendly tool for downloading all images, videos, and story highlights from an Instagram profile. This command-line interface (CLI) tool leverages the `instaloader` library to fetch media content efficiently and provides a seamless way to manage and store your downloaded media.\n\n

## Features
**Download Images and Videos**: Fetch all posts including images, videos, and sidecar posts (multiple images/videos in one post).
**Download Story Highlights**: Optionally download story highlights from a profile.\n- **Progress Display**: Visual progress display using the `rich` library for better user experience.
**Flexible Directory Management**: Choose the base directory for media storage interactively or via CLI argument.
**Headless System Compatibility**: Falls back to CLI input if the graphical interface is not available.

## Installation

To install the `instagram_profile_downloader` package, you can use `pip`:

```bash
    pip install instagram_profile_downloader
```

## Usage

### Basic Usage

To download media from an Instagram profile, simply run the following command:

```bash
    instagram_profile_downloader <profile_name>
```

### Command-Line Options

- `--media-root`: Specify the base directory for media output. If not provided, you will be prompted to select a directory interactively.
- `--no-highlights`: Do not download story highlights.
- `--no-posts`: Do not download posts.
- `--user`: Instagram username (required for downloading story highlights).
- `--password`: Instagram password (required for downloading story highlights).

### Examples

#### Download Media from a Profile

```bash
    instagram_profile_downloader natgeo
```

#### Specify a Base Directory for Media Output

```bash
    instagram_profile_downloader natgeo --media-root /path/to/media
```

#### Download Only Posts (No Highlights)

```bash
    instagram_profile_downloader natgeo --no-highlights
```

#### Download Only Highlights (No Posts)

```bash
    instagram_profile_downloader natgeo --no-posts
```

#### Provide Instagram Credentials for Highlights

```bash
    instagram_profile_downloader natgeo --user your_username --password your_password
```

### Step-by-Step Tutorial

1. **Install the Tool**:

```bash
    pip install instagram_profile_downloader
```

2. **Run the Tool**:

- **Interactive Directory Selection**:

```bash
    instagram_profile_downloader natgeo
```

Follow the prompts to select the base directory for media storage.

- **Specify Directory via CLI**:

```bash
     instagram_profile_downloader natgeo --media-root /path/to/media
```

3. **Optional Flags**:

- To exclude highlights:

```bash
    instagram_profile_downloader natgeo --no-highlights
```

- To exclude posts:

```bash
instagram_profile_downloader natgeo --no-posts
```

4. **Credentials for Highlights**:

- If you want to download story highlights, you need to provide your Instagram credentials:

```bash
    instagram_profile_downloader natgeo --user your_username --password your_password
```

### Logging

All activities and errors are logged in a log file located in the `logs` directory under your specified media root directory. The log file is named based on the profile and the current date.

By following this guide, you should be able to efficiently use the `instagram_profile_downloader` tool to manage and download media from Instagram profiles. If you encounter any issues or have questions, feel free to open an issue on the [GitHub repository](https://github.com/tadeasf/instagram_profile_downloader)."


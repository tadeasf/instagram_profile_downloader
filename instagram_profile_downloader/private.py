import os
import re
import requests


def download_file(url, output_dir):
    local_filename = os.path.join(output_dir, url.split("/")[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def extract_media_links(log_content):
    # Regex pattern for media files
    pattern = re.compile(r"(https?://\S+\.(?:mp4|jpg|jpeg|png|webp|mov|heic|heif))")
    return pattern.findall(log_content)


def main():
    log_file_path = input("Enter the log file path: ")
    output_dir = input("Enter the output directory path: ")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(log_file_path, "r") as log_file:
        log_content = log_file.read()

    media_links = extract_media_links(log_content)

    for link in media_links:
        try:
            print(f"Downloading {link}")
            download_file(link, output_dir)
        except Exception as e:
            print(f"Failed to download {link}: {e}")


if __name__ == "__main__":
    main()

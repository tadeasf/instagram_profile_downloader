import os
import time
import instaloader
import rich_click as click
from loguru import logger
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.console import Console
from rich.traceback import install
from PIL import Image
import cv2
import tkinter as tk
from tkinter import filedialog
import yaml
import asyncio
from aiohttp import ClientSession

# Install rich traceback handler
install()

# Initialize rich console
console = Console()

# Configure loguru to log to a file
logger.remove()

CONFIG_PATH = os.path.expanduser("~/.config/instagram_profile_downloader/config.yml")


def load_config():
    """Load the configuration file."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as file:
            return yaml.safe_load(file)
    return {}


def generate_log_filename(profile_name):
    # Create the filename from the name of the profile we are downloading + current date - DD/MM/YYYY
    return f"{profile_name}_{time.strftime('%d-%m-%Y')}.log"


def format_size(size):
    # Format size to be in B/KB/MB
    for unit in ["B", "KB", "MB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def select_input_directory():
    """Open file dialog to select input directory."""
    try:
        root = tk.Tk()
        root.withdraw()
        input_dir = filedialog.askdirectory(title="Select Input Directory")
        return input_dir
    except Exception as e:
        logger.error(f"Tkinter file dialog failed: {e}")
        return cli_select_input_directory()


def cli_select_input_directory():
    """Fallback method to select input directory via CLI."""
    while True:
        input_dir = input("Enter the input directory path: ").strip()
        if os.path.isdir(input_dir):
            return input_dir
        else:
            print(f"Directory does not exist: {input_dir}")


@click.command()
@click.argument("profile_names", required=False)
@click.option("--media-root", required=False, help="Base directory for media output.")
@click.option("--no-highlights", is_flag=True, help="Do not download highlights.")
@click.option("--no-posts", is_flag=True, help="Do not download posts.")
@click.option("--user", required=False, help="Instagram username.")
@click.option("--password", required=False, help="Instagram password.")
def main(profile_names, media_root, no_highlights, no_posts, user, password):
    config = load_config()

    if not profile_names:
        console.print(
            "[bold magenta]Please enter the Instagram profile names separated by commas[/bold magenta]"
        )
        profile_names = click.prompt("", type=str)

    profile_names = [name.strip() for name in profile_names.split(",")]

    for profile_name in profile_names:
        console.print(
            f"[green]Profile name set to:[/green] [bold]{profile_name}[/bold]"
        )

    media_root = media_root or config.get("download_directory")
    if not media_root:
        media_root = select_input_directory()

    # Check if credentials are provided in the config file
    user = user or config.get("username")
    password = password or config.get("password")

    if not user or not password:
        console.print(
            "[bold magenta]Please enter your Instagram credentials[/bold magenta]"
        )
        console.print("[bold cyan]Username:[/bold cyan]", end=" ")
        user = click.prompt("", type=str)
        console.print("[bold cyan]Password:[/bold cyan]", end=" ")
        password = click.prompt("", type=str, hide_input=True)

    # Create an instance of Instaloader
    L = instaloader.Instaloader()
    L.login(user, password)

    async def download_media(
        url, output_dir, session: ClientSession, semaphore: asyncio.Semaphore
    ):
        async with semaphore:
            try:
                # Ensure the output directory exists
                os.makedirs(output_dir, exist_ok=True)

                # Extract filename from URL
                filename = os.path.join(output_dir, url.split("?")[0].split("/")[-1])
                short_filename = os.path.basename(filename)  # Get only the filename

                # Download the media
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(filename, "wb") as f:
                            async for chunk in response.content.iter_chunked(1024):
                                f.write(chunk)
                        logger.info(f"Downloaded {url} to {filename}")

                        file_size = os.path.getsize(filename)
                        formatted_size = format_size(file_size)

                        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                            with Image.open(filename) as img:
                                width, height = img.size
                            console.print(
                                f"[cyan bold]Downloaded:[/cyan bold] {short_filename} [magenta]({width}x{height}px, {formatted_size})[/magenta]"
                            )
                        elif filename.lower().endswith((".mp4", ".avi", ".mov")):
                            cap = cv2.VideoCapture(filename)
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                            duration = total_frames / fps
                            console.print(
                                f"[cyan bold]Downloaded:[/cyan bold] {short_filename} [magenta](FPS: {fps:.2f}, Duration: {duration:.2f}s, {formatted_size})[/magenta]"
                            )
                        else:
                            console.print(
                                f"[cyan bold]Downloaded:[/cyan bold] {short_filename} [magenta]({formatted_size})[/magenta]"
                            )
                    else:
                        logger.error(
                            f"Failed to download {url}: HTTP {response.status}"
                        )
                        console.print(
                            f"[red]Failed to download {url}: HTTP {response.status}[/red]"
                        )
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")
                console.print(f"[red]Failed to download {url}: {e}[/red]")

    async def get_profile_media(profile_name, progress):
        try:
            # Define directories based on the profile name
            base_dir = os.path.join(media_root, f"{profile_name}_media")
            log_dir = os.path.join(base_dir, "logs")
            media_dir = base_dir

            # Ensure the directories exist
            os.makedirs(log_dir, exist_ok=True)
            os.makedirs(media_dir, exist_ok=True)

            log_filename = os.path.join(log_dir, generate_log_filename(profile_name))

            logger.add(
                log_filename,
                rotation="50 MB",
                retention="10 days",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level="INFO",
                compression="zip",
                serialize=False,
                backtrace=True,
                diagnose=True,
            )

            # Load the profile
            profile = instaloader.Profile.from_username(L.context, profile_name)

            # Get total number of posts and story highlights
            total_posts = profile.mediacount

            # Fetch story highlights separately
            if not no_highlights:
                L.context.log("Fetching highlights...")
                try:
                    highlights = list(L.get_highlights(profile))
                    total_highlights = len(highlights)
                except instaloader.exceptions.LoginRequiredException:
                    logger.error(
                        "Login is required to fetch story highlights. Please login and try again."
                    )
                    console.print(
                        "[red]Login is required to fetch story highlights. Please login and try again.[/red]"
                    )
                    total_highlights = 0
                except Exception as e:
                    logger.error(f"Error fetching highlights: {e}")
                    console.print(f"[red]Error fetching highlights: {e}[/red]")
                    total_highlights = 0
            else:
                total_highlights = 0

            logger.info(f"Total posts: {total_posts}")
            logger.info(f"Total highlights: {total_highlights}")
            console.print(f"[blue]Total posts: {total_posts}[/blue]")
            console.print(f"[blue]Total highlights: {total_highlights}[/blue]")

            async with ClientSession() as session:
                semaphore = asyncio.Semaphore(4)  # Limiting to 4 concurrent downloads
                tasks = []
                if not no_posts:
                    post_task = progress.add_task(
                        f"Downloading posts for {profile_name}...", total=total_posts
                    )

                    for post in profile.get_posts():
                        try:
                            if post.typename == "GraphImage":
                                logger.info(f"Downloading image: {post.url}")
                                tasks.append(
                                    download_media(
                                        post.url, media_dir, session, semaphore
                                    )
                                )
                            elif post.typename == "GraphVideo":
                                logger.info(f"Downloading video: {post.video_url}")
                                tasks.append(
                                    download_media(
                                        post.video_url, media_dir, session, semaphore
                                    )
                                )
                            elif post.typename == "GraphSidecar":
                                for sidecar in post.get_sidecar_nodes():
                                    if sidecar.is_video:
                                        logger.info(
                                            f"Downloading sidecar video: {sidecar.video_url}"
                                        )
                                        tasks.append(
                                            download_media(
                                                sidecar.video_url,
                                                media_dir,
                                                session,
                                                semaphore,
                                            )
                                        )
                                    else:
                                        logger.info(
                                            f"Downloading sidecar image: {sidecar.display_url}"
                                        )
                                        tasks.append(
                                            download_media(
                                                sidecar.display_url,
                                                media_dir,
                                                session,
                                                semaphore,
                                            )
                                        )
                            # Implement rate limiting
                            await asyncio.sleep(0.2)
                        except Exception as e:
                            logger.error(f"Error processing post: {e}")
                            console.print(f"[red]Error processing post: {e}[/red]")
                        progress.update(post_task, advance=1)

                    await asyncio.gather(*tasks, return_exceptions=True)

                if not no_highlights:
                    for highlight in highlights:
                        highlight_title = (
                            f"[bold magenta]{highlight.title}[/bold magenta]"
                        )
                        highlight_task = progress.add_task(
                            f"Downloading highlight {highlight_title}",
                            total=len(highlight.get_items()),
                        )

                        for item in highlight.get_items():
                            try:
                                if item.is_video:
                                    logger.info(
                                        f"Downloading highlight video: {item.video_url}"
                                    )
                                    tasks.append(
                                        download_media(
                                            item.video_url,
                                            media_dir,
                                            session,
                                            semaphore,
                                        )
                                    )
                                else:
                                    logger.info(
                                        f"Downloading highlight image: {item.url}"
                                    )
                                    tasks.append(
                                        download_media(
                                            item.url, media_dir, session, semaphore
                                        )
                                    )
                                # Implement rate limiting
                                await asyncio.sleep(0.2)
                            except Exception as e:
                                logger.error(f"Error processing highlight item: {e}")
                                console.print(
                                    f"[red]Error processing highlight item: {e}[/red]"
                                )
                            progress.update(highlight_task, advance=1)

                    await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Error fetching profile {profile_name}: {e}")
            console.print(f"[red]Error fetching profile {profile_name}: {e}[/red]")

    async def main_async():
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            TextColumn("{task.description}"),
            console=console,
        ) as progress:
            tasks = [
                get_profile_media(profile_name, progress)
                for profile_name in profile_names
            ]
            await asyncio.gather(*tasks)

    asyncio.run(main_async())


if __name__ == "__main__":
    main()

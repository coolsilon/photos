import json
import secrets
from concurrent.futures import ProcessPoolExecutor
from contextlib import suppress
from os import mkdir, path, scandir
from pathlib import Path
from shutil import rmtree
from typing import Annotated

import ffmpeg
import typer
from dotenv import load_dotenv
from passlib.hash import argon2
from PIL import Image
from pillow_heif import register_heif_opener
from structlog import get_logger
from thumbnail import generate_thumbnail

load_dotenv()
register_heif_opener()

logger = get_logger()

DIM_SHORT = 540
DIM_LONG = 720

app = typer.Typer()


def input_get_size(path_input: Path) -> tuple[int, int]:
    width, height = 0, 0

    if path_input.name.split(".")[-1].lower() in ("mp4", "mov"):
        meta = ffmpeg.probe(path_input, select_streams="v")

        width, height = meta["streams"][0]["width"], meta["streams"][0]["height"]

    else:
        width, height = Image.open(path_input).size

    return width, height


def thumbnail_make(path_io: tuple[Path, Path]) -> dict[str, str | bool | int]:
    path_input, path_output = path_io

    width, height = input_get_size(path_input)
    is_portrait = width < height
    is_video = False

    if path_input.name.split(".")[-1].lower() in ("mp4", "mov"):
        is_video = True
        generate_thumbnail(
            str(path_input),
            str(path_output),
            options={
                "trim": True,
                "height": DIM_LONG if is_portrait else DIM_SHORT,
                "width": DIM_SHORT if is_portrait else DIM_LONG,
                "quality": 100,
                "type": "thumbnail",
            },
        )
    else:
        image = Image.open(path_input)

        image.thumbnail((DIM_SHORT, DIM_LONG) if is_portrait else (DIM_LONG, DIM_SHORT))
        image.save(path_output, quality=85)

    width_output, height_output = input_get_size(path_output)

    return {
        "file": path_input.name,
        "path": str(path_input),
        "is_portrait": is_portrait,
        "is_video": is_video,
        "width": width,
        "height": height,
        "width_thumbnail": width_output,
        "height_thumbnail": height_output,
        "thumbnail": str(path_output),
    }


@app.command()
def index(path_data: Annotated[Path, typer.Option()] = Path("./data")) -> None:
    path_meta = path_data / "_meta"

    with suppress(FileNotFoundError):
        rmtree(path_meta)

    mkdir(path_meta)

    for album in scandir(path_data):
        if path.samefile(album.path, path_meta) or album.name.startswith("_"):
            continue

        logger.info("Indexing album", album=album.name)
        path_meta_album = path_meta / album.name

        mkdir(path_meta_album)

        with (
            ProcessPoolExecutor() as executor,
            open(path_meta_album / "index.jsonlines", "w") as index,
        ):
            index.writelines(
                f"{json.dumps(data)}\n"
                for data in executor.map(
                    thumbnail_make,
                    tuple(
                        (
                            Path(file.path),
                            Path(path_meta_album) / f"{file.name.split('.')[0]}.jpg",
                        )
                        for file in sorted(
                            scandir(album.path),
                            key=lambda file: file.stat().st_ctime,
                            reverse=True,
                        )
                        if (
                            "mov" not in file.name.lower()
                            and "heif" not in file.name.lower()
                            and "mp" not in file.name.lower()
                        )
                    ),
                    chunksize=50,
                )
            )


@app.command()
def register(
    name: Annotated[str, typer.Argument()],
    path_data: Annotated[Path, typer.Option()] = Path("./data"),
):
    path_db = path_data / "_db"
    path_db_user = path_db / "users.json"

    if not path_db.exists():
        mkdir(path_db)

    if not path_db_user.exists():
        with open(path_db_user, "w") as file:
            file.write("{}")

    logger.info("Loading users")
    db = {}
    with open(path_db_user, "r") as file:
        db = json.load(file)

    password = typer.prompt("Enter password", hide_input=True)

    if password != typer.prompt("Confirm password", hide_input=True):
        print("Bad password")
        return

    db[name] = {"password": argon2.hash(password)}

    with open(path_db_user, "w") as file:
        json.dump(db, file)


@app.command()
def init():
    path_env = Path(".env")

    with open(path_env, "w") as file:
        file.write(f"JWT_SECRET_KEY={secrets.token_hex(64)}\n")
        file.write(
            f"ALBUM_URL={typer.prompt('The web address of the album').rstrip('/')}\n"
        )


if __name__ == "__main__":
    app()

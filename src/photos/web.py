import json
from os import scandir
from pathlib import Path
from typing import Any

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from structlog import get_logger

logger = get_logger()

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.1.122:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (fastapi.HTTPException, StarletteHTTPException) as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


def row_check_can_commit(row: list[dict[str, Any]]) -> bool:
    count = sum(1 if photo["is_portrait"] else 10 for photo in row)

    return (len(row) == 4 and (count == 4 or count == 13)) or (
        len(row) == 3 and count == 21
    )


def row_check_can_append(row, incoming) -> bool:
    result, count = False, sum(1 if photo["is_portrait"] else 10 for photo in row)

    if incoming["is_portrait"]:
        result = (len(row) < 4 and (count <= 3 or count <= 12)) or (
            len(row) < 3 and count <= 20
        )

    else:
        result = (len(row) < 3 and count <= 11) or (len(row) < 4 and count <= 3)

    return result


@app.get("/api/album")
async def album_list() -> list[dict[str, str]]:
    return [
        {"name": album.name, "url": f"/api/album/{album.name}"}
        for album in scandir(Path("./data"))
        if album.name != "_meta"
    ]


@app.get("/api/album/{album_name}")
async def photo_list(album_name: str) -> dict[str, Any]:
    result, row, cached = {"name": album_name, "photos": []}, [], []

    with open(Path("./data/_meta") / album_name / "index.jsonlines") as index:
        for photo in map(json.loads, index):
            record = {
                "name": photo["file"],
                "photo": f"/photo/{album_name}/{photo['file']}",
                "download": f"/download/{album_name}/{photo['file']}",
                "thumbnail": f"/thumbnail/{album_name}/{photo['file'].split('.')[0]}.jpg",
                "is_portrait": photo["is_portrait"],
                "is_video": photo["is_video"],
            }

            if row_check_can_commit(cached):
                result["photos"].append(cached)
                cached = []

            elif row_check_can_commit(row):
                result["photos"].append(row)
                row = cached
                cached = []

            (row if row_check_can_append(row, photo) else cached).append(record)

    if row:
        result["photos"].append(row)

    if cached:
        result["photos"].append(cached)

    return result


@app.get("/download/{album_name}/{photo}")
async def download(album_name: str, photo: str):
    file_path = Path("./data") / album_name / photo

    if file_path.exists():
        return FileResponse(file_path, filename=file_path.name)


for album in scandir(Path("./data")):
    if album.name == "_meta":
        continue

    app.mount(
        f"/thumbnail/{album.name}",
        StaticFiles(directory=Path("./data/_meta") / album.name, html=True),
        name=f"photo-{album.name}",
    )
    app.mount(
        f"/photo/{album.name}",
        StaticFiles(directory=Path("./data") / album.name, html=True),
        name=f"photo-{album.name}",
    )


app.mount("/", SPAStaticFiles(directory=Path("./src/frontend/dist"), html=True))

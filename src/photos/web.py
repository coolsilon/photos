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


@app.get("/api/album")
async def album_list() -> list[dict[str, str]]:
    return [
        {"name": album.name, "url": f"/api/album/{album.name}"}
        for album in scandir(Path("./data"))
        if album.name != "_meta"
    ]


@app.get("/api/album/{album_name}")
async def photo_list(album_name: str) -> dict[str, Any]:
    result = {"name": album_name, "photos": []}

    with open(Path("./data/_meta") / album_name / "index.jsonlines") as index:
        for photo in map(json.loads, index):
            result["photos"].append(
                {
                    "name": photo["file"],
                    "photo": f"/photo/{album_name}/{photo['file']}",
                    "download": f"/download/{album_name}/{photo['file']}",
                    "thumbnail": f"/thumbnail/{album_name}/{photo['file'].split('.')[0]}.jpg",
                    "size_thumbnail": (
                        photo["width_thumbnail"],
                        photo["height_thumbnail"],
                    ),
                    "size": (
                        photo["width"],
                        photo["height"],
                    ),
                    "is_portrait": photo["is_portrait"],
                    "is_video": photo["is_video"],
                }
            )

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

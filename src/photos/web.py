import asyncio
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta
from os import environ, environb, scandir
from pathlib import Path
from typing import Annotated, Any

import fastapi
import jwt
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Mount
from structlog import get_logger
from passlib.hash import argon2

load_dotenv()

logger = get_logger()


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> AsyncGenerator[None, Any]:
    asyncio.create_task(mount_photos())

    yield


app = fastapi.FastAPI(lifespan=lifespan)
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


def authenticate_jwt(
    access_token: Annotated[str | None, fastapi.Cookie()] = None,
) -> str | None:
    if access_token is None:
        return None

    try:
        payload = jwt.decode(
            access_token,
            environ["JWT_SECRET_KEY"],
            "HS256",
            audience=environ["ALBUM_URL"],
        )

        db = {}
        with open(Path("./data/_db/users.json")) as file:
            db = json.load(file)

        if payload["sub"] in db:
            return payload["sub"]
        else:
            return None

    except Exception as e:
        logger.exception(e)

        return None


def authenticate_password(
    form_data: OAuth2PasswordRequestForm, db: dict[str, Any]
) -> str:
    match form_data.username in db:
        case True if argon2.verify(
            form_data.password, db[form_data.username]["password"]
        ):
            return form_data.username

        case _:
            raise fastapi.HTTPException(401)


@app.post("/api/login")
async def login(
    response: fastapi.Response, form_data: OAuth2PasswordRequestForm = fastapi.Depends()
) -> None:
    db = {}
    with open(Path("./data/_db/users.json")) as file:
        db = json.load(file)

    user = authenticate_password(form_data, db)

    delta_expiry = timedelta(hours=6)
    dt_current = datetime.now()
    dt_expiry = dt_current + delta_expiry

    token = jwt.encode(
        {
            "iss": environ["ALBUM_URL"],
            "sub": user,
            "aud": environ["ALBUM_URL"],
            "exp": dt_expiry.timestamp(),
            "nbf": dt_current.timestamp(),
            "iat": dt_current.timestamp(),
        },
        environ["JWT_SECRET_KEY"],
        "HS256",
    )

    response.set_cookie(
        key="access_token",
        value=token,
        max_age=int(delta_expiry.total_seconds()),
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
    )


@app.get("/api/album")
async def album_list(
    user: Annotated[str, fastapi.Depends(authenticate_jwt)],
) -> list[dict[str, str]]:
    return [
        {
            "name": album.name,
            "display": album.name.split(".")[0],
            "url": f"/api/album/{album.name}",
        }
        for album in scandir(Path("./data"))
        if not (
            album.name.startswith("_")
            or (
                user is None
                and (album.name.endswith(".private") or album.name.endswith(".hidden"))
            )
        )
    ]


@app.get("/api/album/{album_name}")
async def photo_list(
    album_name: str, user: Annotated[str, fastapi.Depends(authenticate_jwt)]
) -> dict[str, Any]:
    if album_name.endswith(".private") and user is None:
        raise fastapi.HTTPException(401)

    result = {"display": album_name.split(".")[0], "name": album_name, "photos": []}

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


async def mount_photos() -> None:
    with suppress(asyncio.CancelledError):
        for album in scandir(Path("./data")):
            if album.name.startswith("_"):
                continue

            logger.info("Adding album", name=album.name)
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

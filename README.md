Usage:

1. Install
    ```
    poetry install
    ```
2. Create a folder to hold photo albums
    ```
    mkdir data
    ```
3. Drop your photo albums folders to the folder
    ```
    mv $YOUR_PHOTO_ALBUM data
    ```
4. Generate index
    ```
    poetry run python -m photos.main
    ```
6. Build frontend
    ```
    yarn install && yarn build2
    ```
7. Start webserver
    ```
    poetry run fastapi run src/photos/web.py
    ```
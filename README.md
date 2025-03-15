# Super Simple Photo Album

**EARLY DEVELOPMENT STAGE - USE WITH CAUTION**

This project is in early development and may contain bugs or incomplete features. Use at your own risk.

**Development Status:** Active development is intermittent. Features and bug fixes are implemented at my own pace, as time permits. Please be aware that updates may be infrequent.

## Design Philosophy: Intentionally Minimalist

This project embraces a deliberately simple design, prioritizing ease of use for small-scale, private photo albums. Key decisions reflect this philosophy:

* **Database-Free Data Storage:** To minimize complexity and dependencies, data is stored in JSON and JSON Lines files, eliminating the need for a database. This approach is well-suited for personal use and small collections.
* **Command-Line User Management:** User registration is handled exclusively via the command-line interface. This choice streamlines setup and enhances security by avoiding web-based registration vulnerabilities.
* **Configuration by Convention:** A settings page is intentionally omitted. Configuration is achieved through file naming conventions (e.g., `.hidden`, `.private`) and direct file manipulation. This design promotes a self-contained and transparent system.

These design choices prioritize simplicity and security for private photo album management. While they may limit scalability or certain features, they create a lightweight and manageable solution for personal use.

## Usage

1.  **Installation:**

    ```bash
    uv sync
    ```

2.  **Configure Environment Variables:**

    Initialize the environment variables

    ```
    uv run python -m photos.main init
    ```

    Answer the prompt to setup the running environment

3.  **Create Data Directory:**

    ```bash
    mkdir data
    ```

4.  **Add Photo Albums:**

    Move your photo album folders into the `data` directory.

    ```bash
    mv $YOUR_PHOTO_ALBUM data
    ```

    * **Hidden Albums:** To hide an album from the public listing (accessible via direct link), rename the album folder with the `.hidden` suffix. Example: `MyVacation.hidden`.
    * **Private Albums:** To restrict access to an album requiring login, rename the album folder with the `.private` suffix. Example: `FamilyPhotos.private`.

5.  **Generate Album Index:**

    ```bash
    uv run python -m photos.main index
    ```

6.  **Create User Account:**

    ```bash
    uv run python -m photos.main register $USERNAME
    ```

    Follow the prompts to set up a password for the new user.

7.  **Build Frontend:**

    ```bash
    yarn install && yarn build2
    ```

8.  **Start Web Server:**

    ```bash
    uv uvicorn photos.web:app --reload
    ```
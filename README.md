# A/D SOCD Cleaner

A simple Windows application to clean Simultaneous Opposing Cardinal Direction (SOCD) inputs for the 'a' and 'd' keys. This is useful for fighting games and other applications where precise keyboard inputs are required.

## Features

*   **Last Input Priority:** When both 'a' and 'd' are pressed, the last key pressed will be the one that is registered.
*   **Configurable Delay:** Set a minimum and maximum delay for the SOCD cleaning to fine-tune the behavior.
*   **Toggle On/Off:** Easily enable or disable the SOCD cleaning on the fly.
*   **License Activation:** The application requires a valid license key to run.
*   **Runs as Administrator:** The application requests administrator privileges to ensure system-wide keyboard hooking.

## Download

You can download the latest version of the application from our website:
[https://marffinn.github.io/SOCDBitchBetterRecognize/](https://marffinn.github.io/SOCDBitchBetterRecognize/)

## License

This project is under a proprietary license. See the `LICENSE` file for more details.

## Project Structure

*   `main.py`: The main application script.
*   `KEY.txt`: A file for the license key (gitignored).
*   `manifest.xml`: Application manifest to request administrator privileges.
*   `qodana.yaml`: Configuration for the Qodana code quality tool.
*   `SOCDunk.spec`: PyInstaller specification file for building the executable.
*   `uttanka.ico`, `uttanka.png`: Application icons.
*   `requirements.txt`: A list of Python dependencies for the project.
*   `LICENSE`: The license for the project.
*   `.gitignore`: A file specifying which files and directories to ignore in version control.
*   `build/`: Directory for build artifacts.
*   `dist/`: Directory for the final distributable.
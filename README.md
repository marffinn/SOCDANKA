# A/D SOCD Cleaner

A simple Windows application to clean Simultaneous Opposing Cardinal Direction (SOCD) inputs for the 'a' and 'd' keys. This is useful for fighting games and other applications where precise keyboard inputs are required.

## Features

*   **Last Input Priority:** When both 'a' and 'd' are pressed, the last key pressed will be the one that is registered.
*   **Configurable Delay:** Set a minimum and maximum delay for the SOCD cleaning to fine-tune the behavior.
*   **Toggle On/Off:** Easily enable or disable the SOCD cleaning on the fly.
*   **License Activation:** The application requires a valid license key to run.
*   **Runs as Administrator:** The application requests administrator privileges to ensure system-wide keyboard hooking.

## Installation

To run the application from source, you will need Python installed.

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2.  Navigate to the project directory:
    ```bash
    cd SOCDBitchBetterRecognize
    ```
3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the application:
    ```bash
    python main.py
    ```

## Building

To build the executable from the source, you will need to have PyInstaller installed.

1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Build the executable:
    ```bash
    pyinstaller SOCDunk.spec
    ```
    The executable will be located in the `dist` directory.

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
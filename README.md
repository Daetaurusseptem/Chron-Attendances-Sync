
# Chron Attendances Sync

## Overview

Chron Attendances Sync is a Python app that automates the synchronization of biometric attendance data with a backend system. It runs on Windows, sets itself to execute at startup, and schedules daily sync tasks. The app securely stores configurations and handles errors robustly, ensuring seamless operation with minimal user intervention.

## Features

- **Biometric Data Synchronization:** Automatically syncs attendance data from biometric devices to a specified backend system.
- **Automatic Startup Configuration:** The application configures itself to run on Windows startup, ensuring that it operates without user intervention.
- **Daily Scheduled Tasks:** A built-in scheduler triggers the synchronization process at a specified time each day.
- **Secure Configuration Management:** User credentials and device configuration settings are securely stored and managed.
- **Error Handling:** Robust error handling mechanisms ensure the application continues running smoothly, even when unexpected issues arise.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone github.com/Daetaurusseptem/script-zk-python-exe.git
   ```

2. **Install Dependencies:**
   - Ensure you have Python 3.x installed.
   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Build the Executable (Optional):**
   - To package the script into a standalone executable using `PyInstaller`:
     ```bash
     pyinstaller --onefile chron-attendances-sync.py
     ```

4. **Run the Application:**
   - Execute the script or the built executable:
     ```bash
     python chron-attendances-sync.py
     ```
     or
     ```bash
     ./dist/chron-attendances-sync.exe
     ```

## Usage

1. **Initial Setup:**
   - On first run, the application will prompt you to enter the IP address and port of the biometric device, as well as your backend API credentials.
   - These settings will be saved securely for future use.

2. **Automatic Synchronization:**
   - The application will schedule a daily synchronization task at 17:00 (5:00 PM) by default.
   - The application will also configure itself to run automatically on Windows startup.

3. **Manual Synchronization:**
   - You can manually trigger a synchronization by running the application again.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions, bug reports, or feature requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- Thanks to the contributors of the [ZK Python SDK](https://github.com/bdraco/pyzk) for providing the tools to interact with biometric devices.

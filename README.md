# Password Checking Service

This Flask-based application provides a service to check passwords against the "Have I Been Pwned" database to determine if they have been exposed in data breaches.

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- Flask[async]

### Installation

First, clone the repository to your local machine:
```
git clone https://github.com/axhse-petrkamnev-projects/password-checking-service
cd password-checking-service
```
Install the necessary Python packages:
```
pip install -r requirements.txt
pip install "Flask[async]"
```
### Prepare the Storage

Before running the application, you must prepare the storage. This project uses a script located in the `devops_cli` directory to accomplish this.

Activate your virtual environment:
```
source venv/Scripts/activate # Or an equivalent command based on your OS
```
Run the `update_storage` script with the following command, specifying the storage location and other optional parameters:
```
py -m devops_cli.update_storage "/path/to/storage" -c 64 -f "/home/user/pwnedpasswords.txt"
```

In this example, storage resources will be located in `/path/to/storage`, and the `/home/user/pwnedpasswords.txt` file will be used to build the storage from 64 coroutines. The file must contain pwned password hashes sorted by prefix (as the official [HIBP downloader](https://github.com/HaveIBeenPwned/PwnedPasswordsDownloader) one-file download result)

For more detailed instructions, refer to the README in the `devops_cli` directory.

### Update Storage in Runtime

To update the storage while the application is running, simply execute the `update_storage` script again with your desired parameters. This allows the application to refresh its data without needing to restart.

### Running the Application

To start the application, run the following command from the root directory of the project:
```
python app.py
```
It is recommended to use another WCGI server in production (for instance, Gunicorn):
```
gunicorn 'app:create_app()'
```
Make sure to adjust paths and commands as necessary for your specific project setup.

### Back-up
For backup purposes it is enough to save the `resource_dir` folder.

# Gmail-Analysis

This Python-based tool automates the analysis of emails through the Gmail API. It enables users to analyze and process email data directly from their Gmail accounts.


## Getting Started

These instructions will guide you through setting up the project on your local machine for development and usage.

### Prerequisites

You will need the following to run this project:

- Python 3.x
- Pip package manager
- Gmail API credentials in the form of a `credentials.json` file

### Installation

To set up the project, follow these steps:

Clone the repository to your local machine:

```bash 
git clone https://github.com/your-username/Gmail-Analysis.git
```
Change directory into the project:
```bash 
cd Gmail-Analysis
```
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the required dependencies:
```bash 
pip install -r requirements.txt
```

**Important:** Always activate the virtual environment before running any scripts:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Gmail API Setup

Before using the tool, you need to configure your Gmail API credentials:

1. Go to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project and enable the Gmail API for it.
3. Create credentials for the project and download the `credentials.json` file.
4. Place the `credentials.json` file in the `config` project directory.

## Authentication

To authenticate with the Gmail API, you will need to use the `quickstart.py` script. **Make sure to activate your virtual environment first**, then provide the script with the paths to your `token_path` and `credentials_path`:

```bash
source venv/bin/activate  # Activate virtual environment first
python quickstart.py --token_path <path/to/your/credentials.json> <path/to/your/token.json>
```

Or use the default paths:
```bash
source venv/bin/activate  # Activate virtual environment first
python quickstart.py
```
This command initializes the authentication process and stores the necessary tokens for API access.

## Built With
* [Gmail API](https://developers.google.com/gmail/api/v3/about-sdk) - The API used for interacting with Gmail.
* [Python](https://www.python.org/) - The programming language used.

## Authors

* **Your Name** - *Initial work* - [ArthurZakirov](https://github.com/ArthurZakirov)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.


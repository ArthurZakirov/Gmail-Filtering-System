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

## Usage

### 1. Authentication

To authenticate with the Gmail API, you will need to use the `gmail_auth_setup.py` script. **Make sure to activate your virtual environment first**, then provide the script with the paths to your `token_path` and `credentials_path`:

```bash
source venv/bin/activate  # Activate virtual environment first
python gmail_auth_setup.py --token_path config/token.json --credentials_path config/credentials.json
```

Or use the default paths:
```bash
source venv/bin/activate  # Activate virtual environment first
python gmail_auth_setup.py
```

### 2. Fetch Gmail Data

To fetch emails from your Gmail account and save them to a CSV file:

```bash
source venv/bin/activate  # Activate virtual environment first
python fetch_gmail_data.py --after 2025/03/01 --before 2025/03/31 --output data/processed/emails.csv
```

This will fetch emails between the specified dates and save them to the output file.

### 3. Filter Job Application Emails

Once you have fetched email data, you can filter it to extract job application-related emails:

```bash
source venv/bin/activate  # Activate virtual environment first
python filter_job_applications.py --input data/processed/emails.csv --output data/processed/job_applications.csv
```

#### Job Application Filter Options

The job application filter supports various customization options:

```bash
# Basic usage with default settings
python filter_job_applications.py --input emails.csv --output job_apps.csv

# Custom keywords and columns
python filter_job_applications.py \
    --input emails.csv \
    --output job_apps.csv \
    --columns Subject Body From \
    --keywords application bewerbung job position career \
    --exclude-keywords github newsletter spam

# Dry run to see results without saving
python filter_job_applications.py --input emails.csv --dry-run --verbose

# Verbose output for detailed logging
python filter_job_applications.py --input emails.csv --output job_apps.csv --verbose
```

#### Filter Parameters

- `--input, -i`: Input CSV file containing email data (required)
- `--output, -o`: Output CSV file for filtered results (default: filtered_applications.csv)
- `--columns, -c`: Column names to search in (default: Subject Body)
- `--keywords, -k`: Keywords to search for (default: application bewerbung)
- `--exclude-keywords, -e`: Keywords to exclude (default: github)
- `--verbose, -v`: Enable verbose output
- `--dry-run`: Show results without saving to file

### 4. Example Workflow

Here's a complete workflow example:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Set up authentication (first time only)
python gmail_auth_setup.py

# 3. Fetch recent emails
python fetch_gmail_data.py --last-days 30 --output data/processed/recent_emails.csv

# 4. Filter for job applications
python filter_job_applications.py \
    --input data/processed/recent_emails.csv \
    --output data/processed/job_applications.csv \
    --verbose

# 5. Preview results with dry run
python filter_job_applications.py \
    --input data/processed/recent_emails.csv \
    --dry-run --verbose
```

## Authentication

To authenticate with the Gmail API, you will need to use the `quickstart.py` script. **Make sure to activate your virtual environment first**, then provide the script with the paths to your `token_path` and `credentials_path`:

```bash
source venv/bin/activate  # Activate virtual environment first
python quickstart.py --token_path config/token.json --credentials_path config/credentials.json
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
# Test change

# Advanced Gmail Data Extraction Tool

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Gmail API](https://img.shields.io/badge/Gmail-API-red.svg)](https://developers.google.com/gmail/api)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful, production-ready Python tool for extracting and processing Gmail messages using the Gmail API. Features intelligent email parsing, system message filtering, and robust error handling.

## Features

- **Intelligent Email Parsing**: Recursively extracts email content from complex MIME structures
- **Smart Filtering**: Automatically filters out system messages, delivery failures, and auto-replies
- **Robust Error Handling**: Comprehensive error management and logging
- **Progress Tracking**: Real-time processing status updates
- **Pagination Support**: Handles large email collections efficiently
- **Format Preservation**: Maintains email formatting and character encoding
- **JSON Export**: Clean, well-structured JSON output

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Google Cloud Platform account
- Gmail API enabled
- Google OAuth 2.0 credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mukiralad/fetch-emails-gcp.git
cd fetch-emails-gcp
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop application"
   - Download the credentials JSON file
5. Rename the downloaded file to `credentials.json` and place it in your project directory

### Configuration

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Update the `.env` file with your configuration:
```env
GMAIL_CREDENTIALS_PATH=credentials.json
```

## Usage

1. Run the script:
```bash
python fetch_gmail_emails.py
```

2. First-time usage:
   - A browser window will open
   - Log in with your Google account
   - Grant the requested permissions
   - The script will save the authentication token for future use

3. The script will:
   - Process all emails with the specified label
   - Show progress updates
   - Filter out system messages
   - Save results to `emails_data.json`

## Output Format

```json
{
    "subject": "Email Subject",
    "from": "sender@example.com",
    "date": "Thu, 15 Aug 2024 14:30:00 +0000",
    "snippet": "Email preview...",
    "body": "Full email content..."
}
```

## Advanced Configuration

### Custom Label Processing

Modify the `label_name` variable in `fetch_gmail_emails.py`:
```python
label_name = 'YOUR_LABEL'  # Default: 'COE'
```

### Filtering Customization

Add custom filtering patterns in `should_skip_email()`:
```python
skip_patterns = {
    'subjects': [
        'your_pattern_here',
    ],
    # ... other patterns
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Show Your Support

If you find this tool useful, please consider giving it a star ⭐️ on GitHub!

## Keywords

gmail-api, email-extraction, python-automation, data-processing, email-parsing, gmail-automation, email-filtering, python-gmail, gmail-tools, email-processing, data-extraction, gmail-integration, python-email, email-automation, gmail-parser

---
Made with ❤️ by [mukiralad](https://github.com/mukiralad)
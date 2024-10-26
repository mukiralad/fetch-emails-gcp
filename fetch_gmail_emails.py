from __future__ import print_function
import os.path
import base64
import json
import html
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import email
import re

# Load environment variables
load_dotenv()

# Load credentials path from .env file
credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH')

# Scope for Gmail API read-only access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_emails_with_label(service, label_name):
    try:
        labels_response = service.users().labels().list(userId='me').execute()
        labels = labels_response.get('labels', [])
        
        label_id = None
        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break

        if not label_id:
            print(f"Label '{label_name}' not found.")
            return []

        messages = []
        next_page_token = None
        
        while True:
            results = service.users().messages().list(
                userId='me', 
                labelIds=[label_id],
                pageToken=next_page_token,
                maxResults=500
            ).execute()
            
            if 'messages' in results:
                messages.extend(results['messages'])
            
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

        return messages

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def decode_base64url(data):
    """Decode base64url-encoded data"""
    pad = len(data) % 4
    if pad:
        data += '=' * (4 - pad)
    try:
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return ""

def extract_body_from_payload(payload, depth=0, max_depth=10):
    if depth > max_depth:
        return ""
    
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part.get('body', {}):
                    return decode_base64url(part['body']['data'])
                elif 'parts' in part:
                    return extract_body_from_payload(part, depth + 1)
        
        for part in payload['parts']:
            if part['mimeType'] == 'text/html':
                if 'data' in part.get('body', {}):
                    html_content = decode_base64url(part['body']['data'])
                    soup = BeautifulSoup(html_content, 'html.parser')
                    return soup.get_text(separator=' ', strip=True)
                elif 'parts' in part:
                    return extract_body_from_payload(part, depth + 1)
        
        for part in payload['parts']:
            body = extract_body_from_payload(part, depth + 1)
            if body:
                return body
    
    elif 'body' in payload and 'data' in payload['body']:
        data = payload['body']['data']
        if payload['mimeType'] == 'text/plain':
            return decode_base64url(data)
        elif payload['mimeType'] == 'text/html':
            html_content = decode_base64url(data)
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
    
    return body

def should_skip_email(subject, from_email, body):
    """
    Determine if an email should be skipped based on various criteria
    """
    # List of patterns that indicate system messages or delivery failures
    skip_patterns = {
        'subjects': [
            r'delivery status notification',
            r'mail delivery failed',
            r'undeliverable',
            r'delivery failure',
            r'failure notice',
            r'returned mail',
            r'automatic reply',
            r'out of office',
            r'auto-reply'
        ],
        'from_addresses': [
            r'mailer-daemon@',
            r'postmaster@',
            r'no-reply@',
            r'noreply@',
            r'auto-reply@'
        ],
        'body_content': [
            r'delivery has failed',
            r'address not found',
            r'user unknown',
            r'550 5\.1\.1',
            r'permanent failure',
            r'delayed delivery notification'
        ]
    }
    
    # Convert inputs to lowercase for case-insensitive matching
    subject_lower = subject.lower()
    from_lower = from_email.lower()
    body_lower = body.lower() if body else ""
    
    # Check subject patterns
    if any(re.search(pattern, subject_lower) for pattern in skip_patterns['subjects']):
        return True
        
    # Check from address patterns
    if any(re.search(pattern, from_lower) for pattern in skip_patterns['from_addresses']):
        return True
        
    # Check body content patterns
    if any(re.search(pattern, body_lower) for pattern in skip_patterns['body_content']):
        return True
    
    return False

def fetch_and_save_emails():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    
    label_name = 'COE'
    messages = get_emails_with_label(service, label_name)
    
    email_data = []
    total_messages = len(messages)
    skipped_count = 0
    
    for idx, message in enumerate(messages, 1):
        try:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            headers = msg['payload'].get('headers', [])
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            from_email = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
            date = next((header['value'] for header in headers if header['name'].lower() == 'date'), 'Unknown Date')
            
            email_body = extract_body_from_payload(msg['payload'])
            
            # Skip system messages and delivery failures
            if should_skip_email(subject, from_email, email_body):
                skipped_count += 1
                continue
            
            if email_body:
                email_data.append({
                    "subject": subject,
                    "from": from_email,
                    "date": date,
                    "body": email_body
                })

        except HttpError as error:
            print(f'An error occurred processing message {idx}/{total_messages}: {error}')
        
        if idx % 10 == 0:
            print(f"Processed {idx}/{total_messages} emails...")

    # Save all emails into a JSON file
    with open('emails_data.json', 'w', encoding='utf-8') as f:
        json.dump(email_data, f, ensure_ascii=False, indent=4)
    
    print(f"\nComplete! Processed {total_messages} emails.")
    print(f"Successfully extracted content from {len(email_data)} emails.")
    print(f"Skipped {skipped_count} system messages and delivery failures.")

if __name__ == '__main__':
    fetch_and_save_emails()
#!/usr/bin/env python3
"""
Automatic Email Replier for Gmail.
Reads emails, generates AI-powered replies, and saves them as drafts.
"""

import os
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.compose']

def authenticate_gmail():
    """Authenticate and return Gmail service."""
    creds = None
    token_path = 'token.json'
    creds_path = 'credentials.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_emails(service, max_results=10):
    """Fetch the latest emails."""
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages

def get_email_content(service, msg_id):
    """Get email content."""
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg['payload']
    headers = payload['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
    
    if 'parts' in payload:
        parts = payload['parts']
        data = parts[0]['body']['data']
    else:
        data = payload['body']['data']
    
    text = base64.urlsafe_b64decode(data).decode('utf-8')
    return subject, sender, text

def generate_reply(subject, sender, body):
    """Generate AI reply."""
    prompt = f"Subject: {subject}\nFrom: {sender}\nBody: {body}\n\nGenerate a polite reply email."
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def create_draft(service, to, subject, body):
    """Create a draft reply."""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = f"Re: {subject}"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft = {'message': {'raw': raw}}
    service.users().drafts().create(userId='me', body=draft).execute()

def main():
    service = authenticate_gmail()
    messages = get_emails(service)
    
    for msg in messages:
        msg_id = msg['id']
        subject, sender, body = get_email_content(service, msg_id)
        print(f"Processing email: {subject} from {sender}")
        
        reply = generate_reply(subject, sender, body)
        # Extract email from sender, assuming format "Name <email>"
        email = sender.split('<')[-1].rstrip('>')
        create_draft(service, email, subject, reply)
        print("Draft created.")

if __name__ == "__main__":
    main()
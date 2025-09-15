"""
Google Sheets Setup Guide for Chatbot Logging

This script helps you set up Google Sheets integration for logging chatbot conversations.

Steps:
1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a Service Account
4. Download credentials JSON
5. Create a Google Sheet
6. Share the sheet with the service account email
7. Add the sheet URL to Streamlit Secrets

For detailed instructions, see: https://docs.gspread.org/en/latest/oauth2.html
"""

import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

def setup_google_sheets():
    """Setup Google Sheets for logging"""
    
    # You'll need to replace this with your actual credentials
    # Download from Google Cloud Console -> Service Accounts
    credentials_path = "path/to/your/credentials.json"
    
    try:
        # Authenticate
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Create or open a spreadsheet
        sheet_name = "Chatbot Conversations Log"
        try:
            spreadsheet = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            spreadsheet = client.create(sheet_name)
        
        # Get the first worksheet
        worksheet = spreadsheet.sheet1
        
        # Set up headers if the sheet is empty
        if not worksheet.get_all_records():
            headers = [
                "Session ID", "Timestamp", "Persona", "Message Count", 
                "Conversation Summary", "Student Intents", "Advisor Intents"
            ]
            worksheet.append_row(headers)
        
        print(f"✅ Google Sheets setup complete!")
        print(f"📊 Sheet URL: {spreadsheet.url}")
        print(f"📧 Share this sheet with: {creds.service_account_email}")
        
        return spreadsheet.url
        
    except Exception as e:
        print(f"❌ Error setting up Google Sheets: {e}")
        return None

def log_conversation(session_data: dict, sheet_url: str):
    """Log a conversation to Google Sheets"""
    try:
        # This would be called from your main app
        # For now, just print the data
        print(f"Logging conversation: {session_data}")
        
        # In the actual implementation, you'd use gspread to append the data
        # worksheet.append_row([
        #     session_data.get("session_id", ""),
        #     session_data.get("timestamp", ""),
        #     session_data.get("persona", ""),
        #     session_data.get("message_count", 0),
        #     session_data.get("summary", ""),
        #     json.dumps(session_data.get("student_intents", [])),
        #     json.dumps(session_data.get("advisor_intents", []))
        # ])
        
    except Exception as e:
        print(f"Error logging conversation: {e}")

if __name__ == "__main__":
    print("Google Sheets Setup for Chatbot Logging")
    print("=" * 50)
    
    # Uncomment to run setup
    # setup_google_sheets()
    
    print("\nTo complete setup:")
    print("1. Create Google Cloud Project")
    print("2. Enable Google Sheets API")
    print("3. Create Service Account")
    print("4. Download credentials JSON")
    print("5. Run setup_google_sheets() with your credentials")
    print("6. Add sheet URL to Streamlit Secrets as GOOGLE_SHEETS_URL")

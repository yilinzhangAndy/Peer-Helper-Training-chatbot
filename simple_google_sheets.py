"""
Simple Google Sheets integration using API Key
This is easier to set up than service account credentials
"""

import requests
import json
from datetime import datetime

def log_to_google_sheets(session_data: dict, sheet_url: str, api_key: str) -> bool:
    """
    Log session data to Google Sheets using API Key
    Note: This requires the sheet to be publicly readable
    """
    try:
        # Extract sheet ID from URL
        # URL format: https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        
        # Google Sheets API endpoint
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/A:Z:append"
        
        # Prepare data
        values = [
            [
                session_data.get("session_id", ""),
                datetime.now().isoformat(),
                session_data.get("persona", ""),
                session_data.get("message_count", 0),
                session_data.get("summary", ""),
                json.dumps(session_data.get("student_intents", [])),
                json.dumps(session_data.get("advisor_intents", []))
            ]
        ]
        
        # API request
        params = {
            'valueInputOption': 'RAW',
            'key': api_key
        }
        
        data = {
            'values': values
        }
        
        response = requests.post(url, params=params, json=data)
        
        if response.status_code == 200:
            print(f"✅ Successfully logged to Google Sheets")
            return True
        else:
            print(f"❌ Error logging to Google Sheets: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in Google Sheets logging: {e}")
        return False

def setup_public_sheet():
    """
    Instructions for setting up a public Google Sheet
    """
    print("📋 Google Sheets Setup Instructions:")
    print("=" * 50)
    print("1. Create a new Google Sheet")
    print("2. Add headers in row 1:")
    print("   A1: Session ID")
    print("   B1: Timestamp")
    print("   C1: Persona")
    print("   D1: Message Count")
    print("   E1: Summary")
    print("   F1: Student Intents")
    print("   G1: Advisor Intents")
    print("3. Make the sheet publicly readable:")
    print("   - Click 'Share' button")
    print("   - Change to 'Anyone with the link can view'")
    print("   - Copy the sheet URL")
    print("4. Get your API Key from Google Cloud Console")
    print("5. Add both to Streamlit Secrets")

if __name__ == "__main__":
    setup_public_sheet()

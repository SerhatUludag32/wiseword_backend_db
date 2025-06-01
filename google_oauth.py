import os
from google.auth.transport import requests
from google.oauth2 import id_token
from dotenv import load_dotenv
import logging

load_dotenv()

class GoogleOAuth:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not self.client_id:
            logging.warning("GOOGLE_CLIENT_ID not found in environment variables")
    
    def verify_google_token(self, token: str):
        """
        Verify Google ID token and extract user information
        Returns user info dict or None if invalid
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Extract user information
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }
            
            return user_info
            
        except ValueError as e:
            logging.error(f"Google token verification failed: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error during Google token verification: {e}")
            return None

# Create a global instance
google_oauth = GoogleOAuth() 
import os

class Config:
    HEIDI_API_KEY = os.getenv('HEIDI_API_KEY')
    HEIDI_EMAIL = os.getenv('HEIDI_EMAIL')
    HEIDI_USER_ID = os.getenv('HEIDI_USER_ID')

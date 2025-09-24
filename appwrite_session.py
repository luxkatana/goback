from dotenv import load_dotenv
from os import environ
from appwrite.client import Client
from appwrite.services.storage import Storage

load_dotenv()
APPWRITE_API_KEY = environ['APPWRITE_KEY']
APPWRITE_ENDPOINT = environ['APPWRITE_ENDPOINT']
APPWRITE_PROJECT_ID = environ['APPWRITE_PROJECT_ID']
APPWRITE_STORAGE_BUCKET_ID = environ["APPWRITE_STORAGE_BUCKET_ID"]


def create_name(file_content: str, file_url: str) -> str:
    # Hier komt een url uit, en dat heeft de volgende format:
    # <file_url_hash>__<file_content_hash>
    pass

class AppwriteSession:
    def __init__(self):
        self.client = Client().set_endpoint(APPWRITE_ENDPOINT).set_project(APPWRITE_PROJECT_ID).set_key(APPWRITE_API_KEY)
        self.storage = Storage(self.client)
    
    
    

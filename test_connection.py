from atlassian import Confluence
import urllib.parse
from dotenv import load_dotenv
import os

def test_confluence_connection(base_url, email, token):
    try:
        confluence = Confluence(
            url=base_url,
            username=email,
            password=token,
            cloud=True
        )
        
        print("Testing connection and permissions...")
        print(f"URL: {base_url}")
        print(f"Email: {email}")
        print("Attempting to list all spaces...")
        
        # First try to list all spaces
        spaces = confluence.get_all_spaces(start=0, limit=100, expand='description.plain')
        if spaces and 'results' in spaces:
            print("\nAccessible spaces:")
            for space in spaces['results']:
                print(f"- {space.get('key')}: {space.get('name', 'Unknown name')}")
        
        print("\nTrying to access AE space specifically...")
        # Try to get the space information
        space = confluence.get_space('AE', expand='description.plain,homepage')
        print(f"\nSpace information:")
        print(f"Key: {space.get('key')}")
        print(f"Name: {space.get('name')}")
        print(f"Type: {space.get('type')}")
        
        # Try to get a list of pages
        print("\nTrying to list pages...")
        pages = confluence.get_all_pages_from_space('AE', start=0, limit=1)
        if pages:
            print("Successfully accessed pages in the space")
            print(f"Sample page title: {pages[0].get('title')}")
        else:
            print("No pages found in the space (or no access to pages)")
            
    except Exception as e:
        print(f"\nError connecting to Confluence: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            print("\nHeaders sent:")
            print(e.response.request.headers)

if __name__ == '__main__':
    load_dotenv()
    
    base_url = os.getenv('CONFLUENCE_URL') or input("Enter your Confluence URL: ")
    email = os.getenv('CONFLUENCE_EMAIL') or input("Enter your Confluence email: ")
    token = os.getenv('CONFLUENCE_TOKEN') or input("Enter your Confluence API token: ")
    
    test_confluence_connection(base_url, email, token) 
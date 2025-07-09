from atlassian import Confluence
import urllib.parse
from dotenv import load_dotenv
import os
import re

def extract_space_from_url(url: str) -> str:
    """Extract space key from a Confluence URL.
    
    Example URLs:
    - https://your-domain.atlassian.net/wiki/spaces/SPACEKEY/overview
    - https://your-domain.atlassian.net/wiki/spaces/SPACEKEY/pages/123456789
    """
    space_match = re.search(r'/spaces/([^/]+)', url)
    if space_match:
        return space_match.group(1)
    return None

def get_page_info(confluence: Confluence, page_id: str = None, page_url: str = None):
    """Get information about a specific page."""
    try:
        if page_url and not page_id:
            # Try to extract page ID from URL
            id_match = re.search(r'/pages/(\d+)', page_url)
            if id_match:
                page_id = id_match.group(1)
            else:
                print("Could not extract page ID from URL")
                return

        if page_id:
            page = confluence.get_page_by_id(page_id, expand='space')
            if page:
                print("\nPage Information:")
                print(f"Title: {page.get('title')}")
                print(f"ID: {page.get('id')}")
                space = page.get('space', {})
                print(f"Space Key: {space.get('key')}")
                print(f"Space Name: {space.get('name')}")
                print(f"Space Type: {space.get('type')}")
                return space.get('key')

    except Exception as e:
        print(f"Error getting page information: {str(e)}")
        return None

def test_confluence_connection(base_url, email, token, page_url=None):
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
        
        if page_url:
            print(f"\nAnalyzing page URL: {page_url}")
            space_key = extract_space_from_url(page_url)
            if space_key:
                print(f"Space Key from URL: {space_key}")
                
            # If URL contains a page ID, get its information
            get_page_info(confluence, page_url=page_url)
        
        print("\nListing all accessible spaces...")
        spaces = confluence.get_all_spaces(start=0, limit=100, expand='description.plain')
        if spaces and 'results' in spaces:
            print("\nAccessible spaces:")
            for space in spaces['results']:
                print(f"- {space.get('key')}: {space.get('name', 'Unknown name')}")
            
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
    
    # Ask for a page URL (optional)
    page_url = input("Enter a Confluence page URL (optional, press Enter to skip): ").strip() or None
    
    test_confluence_connection(base_url, email, token, page_url) 
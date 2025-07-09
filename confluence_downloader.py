import os
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import html2text
import requests
from atlassian import Confluence
from dotenv import load_dotenv
from tqdm import tqdm


class ConfluenceDownloader:
    def __init__(self, site_url: str, email: str, token: str):
        """Initialize the Confluence downloader.
        
        Args:
            site_url: The Confluence site URL (e.g., https://your-domain.atlassian.net)
            email: The Atlassian account email
            token: The API token for authentication
        """
        # Validate and clean the site URL
        parsed_url = urlparse(site_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid site URL. Please provide a complete URL (e.g., https://your-domain.atlassian.net)")
        
        self.site_url = site_url.rstrip('/')
        self.confluence = Confluence(
            url=self.site_url,
            username=email,
            password=token,
            cloud=True
        )
        
        # Configure HTML to Markdown converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.body_width = 0  # Don't wrap text
        self.html_converter.ignore_images = False
        self.html_converter.protect_links = True
        self.html_converter.unicode_snob = True
        self.html_converter.ignore_tables = False
        self.html_converter.mark_code = True
        
    def get_all_pages_in_space(self, space_key: str) -> list:
        """Get all pages in a Confluence space.
        
        Args:
            space_key: The key of the Confluence space
            
        Returns:
            List of pages in the space
        """
        try:
            start = 0
            limit = 100
            pages = []
            
            while True:
                results = self.confluence.get_all_pages_from_space(
                    space=space_key,
                    start=start,
                    limit=limit,
                    status='current'
                )
                
                if not results:
                    break
                    
                pages.extend(results)
                start += limit
                
                if len(results) < limit:
                    break
                    
            return pages
        except Exception as e:
            print(f"Error getting pages from space {space_key}: {str(e)}")
            return []

    def download_attachments(self, page_id: str, output_dir: Path) -> list:
        """Download all attachments for a specific page.
        
        Args:
            page_id: The ID of the Confluence page
            output_dir: Directory to save the attachments
            
        Returns:
            List of downloaded attachment information (for Markdown linking)
        """
        downloaded_attachments = []
        try:
            attachments = self.confluence.get_attachments_from_content(page_id)
            if not attachments.get('results'):
                return downloaded_attachments

            attachments_dir = output_dir / 'attachments'
            attachments_dir.mkdir(exist_ok=True)

            for attachment in attachments['results']:
                try:
                    filename = attachment['title']
                    attachment_id = attachment['id']
                    
                    # Get attachment download URL
                    download_url = f"{self.site_url}/download/attachments/{page_id}/{attachment_id}/{filename}"
                    
                    # Download the attachment
                    response = requests.get(
                        download_url,
                        headers={'Authorization': f'Basic {self.confluence._session.auth}'},
                        stream=True
                    )
                    response.raise_for_status()
                    
                    file_path = attachments_dir / filename
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Store attachment info for Markdown linking
                    downloaded_attachments.append({
                        'filename': filename,
                        'path': os.path.join('attachments', filename)
                    })
                                
                except Exception as e:
                    print(f"Error downloading attachment {filename}: {str(e)}")

        except Exception as e:
            print(f"Error getting attachments for page {page_id}: {str(e)}")
            
        return downloaded_attachments

    def convert_to_markdown(self, html_content: str, attachments: list) -> str:
        """Convert HTML content to Markdown and update attachment links.
        
        Args:
            html_content: The HTML content to convert
            attachments: List of attachment information
            
        Returns:
            Markdown formatted content
        """
        # Convert HTML to Markdown
        markdown_content = self.html_converter.handle(html_content)
        
        # Add a section for attachments if any exist
        if attachments:
            markdown_content += "\n\n## Attachments\n\n"
            for attachment in attachments:
                markdown_content += f"- [{attachment['filename']}]({attachment['path']})\n"
        
        return markdown_content

    def download_space(self, space_key: str, output_dir: Optional[str] = None) -> None:
        """Download all pages and attachments from a Confluence space.
        
        Args:
            space_key: The key of the Confluence space
            output_dir: Directory to save the downloaded content (default: ./confluence_export)
        """
        # Set up output directory
        if output_dir is None:
            output_dir = Path('./confluence_export')
        else:
            output_dir = Path(output_dir)
            
        space_dir = output_dir / space_key
        space_dir.mkdir(parents=True, exist_ok=True)

        # Get all pages
        print(f"Fetching pages from space {space_key}...")
        pages = self.get_all_pages_in_space(space_key)
        
        if not pages:
            print(f"No pages found in space {space_key}")
            return

        print(f"Found {len(pages)} pages. Starting download...")
        
        # Download each page and its attachments
        for page in tqdm(pages, desc="Downloading pages"):
            try:
                page_id = page['id']
                page_title = page['title']
                
                # Create sanitized filename
                safe_title = "".join(c for c in page_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                page_file = space_dir / f"{safe_title}.md"
                
                # Get page content
                content = self.confluence.get_page_by_id(
                    page_id, 
                    expand='body.storage'
                )
                
                # Download attachments first
                attachments = self.download_attachments(page_id, space_dir)
                
                # Convert content to Markdown
                markdown_content = self.convert_to_markdown(
                    content['body']['storage']['value'],
                    attachments
                )
                
                # Add title as heading
                full_content = f"# {page_title}\n\n{markdown_content}"
                
                # Save markdown content
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                
            except Exception as e:
                print(f"Error downloading page {page_title}: {str(e)}")

        print(f"\nDownload completed! Content saved to: {space_dir.absolute()}")


def main():
    """Main function to run the Confluence downloader."""
    load_dotenv()
    
    # Get configuration from environment variables or command line arguments
    site_url = os.getenv('CONFLUENCE_URL') or input("Enter your Confluence URL: ")
    email = os.getenv('CONFLUENCE_EMAIL') or input("Enter your Confluence email: ")
    token = os.getenv('CONFLUENCE_TOKEN') or input("Enter your Confluence API token: ")
    space_key = os.getenv('CONFLUENCE_SPACE') or input("Enter the Confluence space key: ")
    output_dir = os.getenv('OUTPUT_DIR')
    
    try:
        downloader = ConfluenceDownloader(site_url, email, token)
        downloader.download_space(space_key, output_dir)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main() 
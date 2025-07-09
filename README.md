# Confluence Downloader

A Python tool to download content from Confluence spaces and convert it to Markdown format.

## Features

- Download all pages from a Confluence space
- Convert HTML content to Markdown format
- Download and preserve attachments
- Maintain links to attachments in Markdown
- Support for tables, code blocks, and other Confluence formatting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/alakob/confluence_downloader.git
cd confluence_downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables or create a `.env` file:

```env
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_EMAIL=your-email@domain.com
CONFLUENCE_TOKEN=your-api-token
CONFLUENCE_SPACE=SPACE_KEY
OUTPUT_DIR=/path/to/output  # Optional
```

To get an API token:
1. Log in to https://id.atlassian.com
2. Go to Security → Create and manage API tokens
3. Create a new token and copy it

## Usage

Run the script:
```bash
python confluence_downloader.py
```

The script will:
1. Connect to your Confluence instance
2. Download all pages from the specified space
3. Convert content to Markdown format
4. Save attachments and update links
5. Create a directory structure with all content

## Output Structure

```
confluence_export/
└── SPACE_KEY/
    ├── Page Title 1.md
    ├── Page Title 2.md
    └── attachments/
        ├── file1.pdf
        └── file2.png
```

## Testing Connection

To test your Confluence connection:
```bash
python test_connection.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this code in your projects.

## Author

Blaise Alako (@alakob) 
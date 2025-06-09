 # Email Collector from Search Results

A Python tool that helps collect email addresses from web search results using DuckDuckGo as the search engine. The tool provides both command-line and interactive interfaces for ease of use.

## ⚠️ Important Notice

This tool is for educational purposes only. Before using this tool, please be aware:
- Web scraping may violate websites' terms of service
- Always respect robots.txt and rate limits
- Consider using official APIs when available
- Ensure compliance with data protection regulations

## Features

- 🔍 Uses DuckDuckGo search engine for finding relevant websites
- 📧 Extracts email addresses using regex pattern matching
- 🌐 Respects rate limits with configurable delays between requests
- 📊 Provides detailed summary of collected emails
- 💾 Saves results in CSV format
- 🔄 Implements domain-based rate limiting
- 🚦 Includes built-in error handling and logging

## Installation

1. Clone this repository:
```bash
git clone https://github.com/dieh4cker/web_scraper.git

```

2. Install required dependencies:
```bash
pip install requests beautifulsoup4
```

## Usage

### Command Line Interface

Basic usage:
```bash
python web_scraper.py "your search query"
```

Advanced options:
```bash
python web_scraper.py "your search query" \
    --results 20 \
    --output results.csv \
    --delay 2 4 \
    --max-pages 5
```

Available options:
- `--results`, `-r`: Number of search results to process (default: 10)
- `--output`, `-o`: Output CSV file path (default: collected_emails.csv)
- `--delay`, `-d`: Delay range between requests in seconds (default: 1 3)
- `--max-pages`, `-m`: Maximum pages to check per domain (default: 3)

### Interactive Mode

Run without arguments to use interactive mode:
```bash
python web_scraper.py
```

Interactive mode will guide you through:
1. Entering a search query
2. Specifying number of results to process
3. Setting output filename
4. Configuring delay between requests

## Output Format

The tool generates a CSV file with two columns:
- `URL`: The source website URL
- `Email`: Email address found on that URL

Example output:
```csv
URL,Email
https://example.com,john@example.com
https://example.com,jane@example.com
https://another.com,contact@another.com
```

## Rate Limiting

The tool implements several measures to be respectful to websites:
- Configurable delay between requests
- Maximum pages per domain limit
- User-Agent header to identify the bot
- Domain-based request tracking

## Error Handling

The script includes robust error handling for:
- Network connection issues
- Invalid URLs
- Parsing errors
- Rate limiting responses
- User interruptions (Ctrl+C)

## Logging

Detailed logging is enabled by default and includes:
- Search progress
- URL processing status
- Email extraction results
- Error messages

## Requirements

- Python 3.6+
- requests
- beautifulsoup4


## Disclaimer

This tool is provided as-is without any warranties. Users are responsible for ensuring their use of this tool complies with all applicable laws, regulations, and terms of service. 

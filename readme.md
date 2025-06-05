# ScreenScraper.fr Python Library

A clean, modern Python library for accessing retro game art and metadata from [ScreenScraper.fr](https://www.screenscraper.fr/).

## Features

- **Easy-to-use API** - Simple methods for searching games and downloading media
- **Multiple search methods** - Search by ROM file hashes, game name, or ScreenScraper ID
- **Rich game metadata** - Access game descriptions, publishers, developers, ratings, and more
- **Media downloads** - Download box art, screenshots, videos, manuals, and other game media
- **Rate limiting** - Built-in rate limiting to respect API quotas
- **Error handling** - Comprehensive error handling with specific exception types
- **Type hints** - Full type annotations for better IDE support
- **Flexible configuration** - Support for both developer and user credentials

## Installation

```bash
pip install requests
```

Then copy the `screenscraper.py` file to your project.

## Quick Start

### 1. Get API Credentials

First, you need to register for developer credentials at [ScreenScraper.fr](https://www.screenscraper.fr/):

1. Create an account
2. Request developer access in their forums
3. Get your `devid` and `devpassword`

Optionally, register as a user to get higher rate limits and access during busy periods.

### 2. Basic Usage

```python
from screenscraper import ScreenScraperClient, quick_search

# Initialize client
client = ScreenScraperClient(
    dev_id="your_dev_id",
    dev_password="your_dev_password",
    user_id="your_username",  # Optional but recommended
    user_password="your_user_password"  # Optional but recommended
)

# Search for a game by ROM file
game = client.search_by_file("./roms/super_mario_bros.nes", "nes")

if game:
    print(f"Found: {game.name}")
    print(f"Publisher: {game.publisher}")
    print(f"Year: {game.release_date}")
    
    # Download box art
    client.download_media(game, ['box-2D'], './artwork/')
```

### 3. Quick Functions

For simple use cases, you can use the convenience functions:

```python
from screenscraper import quick_search, download_box_art

# Quick search
game = quick_search("dev_id", "dev_password", "./rom.nes", "nes")

# Quick box art download
success = download_box_art(
    "dev_id", "dev_password", 
    "./rom.nes", "nes", 
    "./artwork/"
)
```

## Detailed Usage

### Searching for Games

#### Search by ROM File (Recommended)

This method uses file hashes (MD5, SHA1, CRC32) for the most accurate results:

```python
game = client.search_by_file("./roms/zelda.nes", "nes")
```

#### Search by Game Name

```python
game = client.search_by_name("The Legend of Zelda", "nes")
```

#### Search by ScreenScraper ID

```python
game = client.search_by_id("12345")
```

### Working with Game Information

The `GameInfo` object contains comprehensive game data:

```python
if game:
    print(f"Game ID: {game.id}")
    print(f"Name: {game.name}")
    print(f"Description: {game.description}")
    print(f"Publisher: {game.publisher}")
    print(f"Developer: {game.developer}")
    print(f"Players: {game.players}")
    print(f"Rating: {game.rating}")
    print(f"Release Date: {game.release_date}")
    print(f"Genre: {game.genre}")
    print(f"System: {game.system}")
    
    # Available media
    print("Available media:")
    for media in game.media:
        print(f"  - {media.media_type} ({media.format})")
```

### Downloading Media

#### Download Specific Media Types

```python
# Download multiple media types
results = client.download_media(
    game, 
    ['box-2D', 'screenshot', 'video'], 
    './downloads/',
    preferred_regions=['us', 'wor', 'eu']
)

for media_type, success in results.items():
    print(f"{media_type}: {'✓' if success else '✗'}")
```

#### Available Media Types

The library supports all ScreenScraper media types:

- `box-2D` - 2D box art
- `box-3D` - 3D box art
- `screenshot` - In-game screenshots
- `title` - Title screens
- `marquee` - Marquee/wheel artwork
- `video` - Video previews
- `manual` - Game manuals
- `map` - Game maps
- `mix` - Mixed artwork compositions

#### Get Specific Media

```python
# Get the best box art for a game
box_art = game.get_best_media('box-2D', ['us', 'eu'])
if box_art:
    box_art.download('./artwork/box_art.jpg')

# Get all screenshots
screenshots = game.get_media_by_type('screenshot')
for i, screenshot in enumerate(screenshots):
    screenshot.download(f'./screenshots/shot_{i}.jpg')
```

### Supported Platforms

The library includes mappings for common retro gaming platforms:

```python
PLATFORMS = {
    'nes': 3,
    'snes': 4,
    'n64': 14,
    'gamecube': 13,
    'wii': 16,
    'gameboy': 9,
    'gbc': 10,
    'gba': 12,
    'nds': 15,
    'genesis': 1,
    'megadrive': 1,
    'mastersystem': 2,
    'saturn': 22,
    'dreamcast': 23,
    'psx': 57,
    'ps2': 58,
    'psp': 61,
    'arcade': 75,
    'mame': 75,
    'atari2600': 26,
    'atari7800': 43,
    'colecovision': 48,
    'intellivision': 115,
    # ... and many more
}
```

## Advanced Configuration

### Rate Limiting

The client includes built-in rate limiting:

```python
client = ScreenScraperClient(
    dev_id="your_dev_id",
    dev_password="your_dev_password",
    request_delay=2.0,  # 2 seconds between requests
    max_requests_per_day=5000
)
```

### Language Preferences

Set your preferred language for game descriptions:

```python
client = ScreenScraperClient(
    dev_id="your_dev_id",
    dev_password="your_dev_password",
    language="fr"  # French, English="en", Spanish="es", etc.
)
```

### Custom User Agent

```python
client = ScreenScraperClient(
    dev_id="your_dev_id",
    dev_password="your_dev_password",
    software_name="MyRetroFrontend v1.0"
)
```

## Error Handling

The library provides specific exception types for different error conditions:

```python
from screenscraper import (
    ScreenScraperError, 
    APIQuotaExceededError, 
    APIClosedError, 
    GameNotFoundError
)

try:
    game = client.search_by_file("./rom.nes", "nes")
except APIQuotaExceededError:
    print("Daily quota exceeded. Try again tomorrow.")
except APIClosedError:
    print("API is currently closed. Try again later.")
except GameNotFoundError:
    print("Game not found in database.")
except ScreenScraperError as e:
    print(f"ScreenScraper error: {e}")
```

## Batch Processing Example

Here's an example of processing multiple ROM files:

```python
import os
from pathlib import Path
from screenscraper import ScreenScraperClient

def process_rom_directory(rom_dir, platform, output_dir):
    client = ScreenScraperClient(
        dev_id="your_dev_id",
        dev_password="your_dev_password",
        user_id="your_username",
        user_password="your_password"
    )
    
    rom_dir = Path(rom_dir)
    output_dir = Path(output_dir)
    
    # Common ROM extensions
    rom_extensions = {'.nes', '.smc', '.sfc', '.n64', '.z64', '.gb', '.gbc', '.gba'}
    
    for rom_file in rom_dir.iterdir():
        if rom_file.suffix.lower() in rom_extensions:
            print(f"Processing {rom_file.name}...")
            
            try:
                game = client.search_by_file(rom_file, platform)
                if game:
                    # Create game-specific directory
                    game_dir = output_dir / rom_file.stem
                    game_dir.mkdir(exist_ok=True)
                    
                    # Download media
                    client.download_media(
                        game, 
                        ['box-2D', 'screenshot'], 
                        game_dir
                    )
                    
                    # Save game info
                    with open(game_dir / 'info.txt', 'w') as f:
                        f.write(f"Name: {game.name}\n")
                        f.write(f"Publisher: {game.publisher}\n")
                        f.write(f"Year: {game.release_date}\n")
                        f.write(f"Description: {game.description}\n")
                    
                    print(f"✓ Processed {game.name}")
                else:
                    print(f"✗ Game not found: {rom_file.name}")
                    
            except Exception as e:
                print(f"✗ Error processing {rom_file.name}: {e}")

# Usage
process_rom_directory("./roms/nes/", "nes", "./artwork/")
```

## File Hash Calculation

The library can calculate file hashes for ROM identification:

```python
from screenscraper import ScreenScraperClient

md5, sha1, crc = ScreenScraperClient.calculate_file_hashes("./rom.nes")
print(f"MD5: {md5}")
print(f"SHA1: {sha1}")
print(f"CRC32: {crc}")
```

## Best Practices

1. **Use ROM file searching when possible** - It's more accurate than name-based searching
2. **Register as a user** - Get higher rate limits and access during busy periods
3. **Implement proper error handling** - The API can be rate-limited or temporarily unavailable
4. **Cache results** - Store game information locally to avoid repeated API calls
5. **Respect rate limits** - Don't hammer the API; it's a community resource
6. **Contribute back** - Consider contributing game information to the database

## API Limits and Quotas

ScreenScraper.fr has daily quotas and rate limits:

- **Unregistered users**: Very limited access, often blocked during busy periods
- **Registered users**: Higher quotas and priority access
- **Contributing users**: Even higher quotas
- **Patreon supporters**: Additional benefits and quota increases

The library automatically handles rate limiting, but you should monitor your usage and consider upgrading if you need higher limits.

## Contributing

This library is designed to be extended. Some areas for improvement:

- Add support for more ScreenScraper endpoints
- Implement caching mechanisms
- Add more platform mappings
- Improve error recovery
- Add async support for batch operations

## License

MIT License - see the library file for full details.

## Disclaimer

This library is not affiliated with ScreenScraper.fr. Please respect their terms of service and consider supporting their project if you find it useful.

"""
ScreenScraper.fr Python Library
===============================

A clean, modern Python library for accessing retro game art and metadata 
from ScreenScraper.fr API.

Author: Assistant
License: MIT
"""

import requests
import hashlib
import time
import json
import xml.etree.ElementTree as ET
import zlib
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GameMedia:
    """Represents a single media item (image, video, etc.) for a game."""
    media_type: str
    url: str
    format: str
    region: str = ""
    size: str = ""
    
    def download(self, save_path: Union[str, Path]) -> bool:
        """Download the media file to the specified path."""
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded {self.media_type} to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {self.media_type}: {e}")
            return False


@dataclass
class GameInfo:
    """Represents comprehensive game information from ScreenScraper."""
    id: str
    name: str
    description: str = ""
    publisher: str = ""
    developer: str = ""
    players: str = ""
    rating: str = ""
    release_date: str = ""
    genre: str = ""
    system: str = ""
    media: List[GameMedia] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)
    
    def get_media_by_type(self, media_type: str) -> List[GameMedia]:
        """Get all media items of a specific type (e.g., 'box-2D', 'screenshot')."""
        return [m for m in self.media if m.media_type == media_type]
    
    def get_best_media(self, media_type: str, preferred_regions: Optional[List[str]] = None) -> Optional[GameMedia]:
        """Get the best media item of a type, preferring certain regions."""
        if preferred_regions is None:
            preferred_regions = ['us', 'wor', 'eu', 'jp']
        
        candidates = self.get_media_by_type(media_type)
        if not candidates:
            return None
        
        # Try to find media from preferred regions
        for region in preferred_regions:
            for media in candidates:
                if media.region.lower() == region.lower():
                    return media
        
        # Return first available if no regional preference matches
        return candidates[0]


class ScreenScraperError(Exception):
    """Base exception for ScreenScraper API errors."""
    pass


class APIQuotaExceededError(ScreenScraperError):
    """Raised when API quota is exceeded."""
    pass


class APIClosedError(ScreenScraperError):
    """Raised when API is closed for non-registered users."""
    pass


class GameNotFoundError(ScreenScraperError):
    """Raised when a game is not found in the database."""
    pass


class ScreenScraperClient:
    """
    Main client for interacting with the ScreenScraper.fr API.
    
    Provides methods to search for games and download retro game art and metadata.
    """
    
    BASE_URL = "https://www.screenscraper.fr/api2"
    
    # Common media types available from ScreenScraper
    MEDIA_TYPES = {
        'box-2D': 'box-2D',           # 2D box art
        'box-3D': 'box-3D',           # 3D box art  
        'screenshot': 'ss',            # In-game screenshots
        'title': 'sstitle',           # Title screens
        'marquee': 'wheel',           # Marquee/wheel art
        'video': 'video',             # Video previews
        'manual': 'manuel',           # Game manuals
        'map': 'map',                 # Game maps
        'mix': 'mixrbv1',             # Mixed artwork
    }
    
    # Platform mappings (partial list - ScreenScraper has many more)
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
    }
    
    def __init__(self, 
                 dev_id: str, 
                 dev_password: str, 
                 software_name: str = "ScreenScraperPython",
                 user_id: Optional[str] = None,
                 user_password: Optional[str] = None,
                 language: str = "en",
                 max_requests_per_day: int = 10000,
                 request_delay: float = 1.0):
        """
        Initialize the ScreenScraper client.
        
        Args:
            dev_id: Developer ID from ScreenScraper
            dev_password: Developer password
            software_name: Name of your software (for identification)
            user_id: Optional user ID for registered users
            user_password: Optional user password
            language: Language preference (en, fr, es, de, etc.)
            max_requests_per_day: Maximum requests per day (for rate limiting)
            request_delay: Delay between requests in seconds
        """
        self.dev_id = dev_id
        self.dev_password = dev_password
        self.software_name = software_name
        self.user_id = user_id
        self.user_password = user_password
        self.language = language
        self.max_requests_per_day = max_requests_per_day
        self.request_delay = request_delay
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'{software_name}/1.0'
        })
        
        self.request_count = 0
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _build_params(self, **kwargs) -> Dict[str, str]:
        """Build common API parameters."""
        params = {
            'devid': self.dev_id,
            'devpassword': self.dev_password,
            'softname': self.software_name,
            'output': 'json',
        }
        
        if self.user_id and self.user_password:
            params.update({
                'ssid': self.user_id,
                'sspassword': self.user_password
            })
        
        params.update(kwargs)
        return params
    
    def _make_request(self, endpoint: str, params: Dict[str, str]) -> Dict:
        """Make a request to the ScreenScraper API."""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Handle potential encoding issues
            try:
                data = response.json()
            except json.JSONDecodeError:
                # Try to fix common JSON issues from ScreenScraper
                text = response.text.replace('],\n\t\t}', ']\n\t\t}')
                data = json.loads(text)
            
            self.request_count += 1
            
            # Check for API errors in response
            header = data.get('header', {})
            if 'erreur' in header:
                error_msg = header['erreur']
                if 'quota' in error_msg.lower():
                    raise APIQuotaExceededError(f"API quota exceeded: {error_msg}")
                elif 'fermé' in error_msg.lower() or 'closed' in error_msg.lower():
                    raise APIClosedError(f"API closed: {error_msg}")
                else:
                    raise ScreenScraperError(f"API error: {error_msg}")
            
            return data
            
        except requests.RequestException as e:
            raise ScreenScraperError(f"Request failed: {e}")
    
    @staticmethod
    def calculate_file_hashes(file_path: Union[str, Path]) -> Tuple[str, str, str]:
        """Calculate MD5, SHA1, and CRC32 hashes for a ROM file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # For large files, we should be careful about memory usage
        file_size = file_path.stat().st_size
        chunk_size = 64 * 1024  # 64KB chunks
        
        md5_hash = hashlib.md5()
        sha1_hash = hashlib.sha1()
        crc32_hash = 0
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5_hash.update(chunk)
                sha1_hash.update(chunk)
                crc32_hash = zlib.crc32(chunk, crc32_hash)
        
        return (
            md5_hash.hexdigest().upper(),
            sha1_hash.hexdigest().upper(),
            f"{crc32_hash & 0xFFFFFFFF:08X}"
        )
    
    def search_by_file(self, 
                      file_path: Union[str, Path], 
                      platform: str,
                      rom_name: Optional[str] = None) -> Optional[GameInfo]:
        """
        Search for a game by ROM file (using file hashes).
        
        Args:
            file_path: Path to the ROM file
            platform: Platform name (e.g., 'nes', 'snes', 'psx')
            rom_name: Optional ROM name override
            
        Returns:
            GameInfo object if found, None otherwise
        """
        file_path = Path(file_path)
        
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}. Supported: {list(self.PLATFORMS.keys())}")
        
        # Calculate file hashes
        try:
            md5, sha1, crc = self.calculate_file_hashes(file_path)
        except Exception as e:
            logger.error(f"Failed to calculate hashes for {file_path}: {e}")
            return None
        
        rom_name = rom_name or file_path.name
        file_size = file_path.stat().st_size
        
        params = self._build_params(
            md5=md5,
            sha1=sha1,
            crc=crc,
            romnom=rom_name,
            romtaille=str(file_size),
            systemeid=str(self.PLATFORMS[platform]),
            romtype='rom'
        )
        
        try:
            data = self._make_request('jeuInfos.php', params)
            return self._parse_game_data(data)
        except GameNotFoundError:
            return None
    
    def search_by_name(self, 
                      game_name: str, 
                      platform: str) -> Optional[GameInfo]:
        """
        Search for a game by name and platform.
        
        Args:
            game_name: Name of the game
            platform: Platform name
            
        Returns:
            GameInfo object if found, None otherwise
        """
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        
        params = self._build_params(
            recherche=game_name,
            systemeid=str(self.PLATFORMS[platform])
        )
        
        try:
            data = self._make_request('jeuInfos.php', params)
            return self._parse_game_data(data)
        except GameNotFoundError:
            return None
    
    def search_by_id(self, game_id: str) -> Optional[GameInfo]:
        """
        Search for a game by ScreenScraper game ID.
        
        Args:
            game_id: ScreenScraper game ID
            
        Returns:
            GameInfo object if found, None otherwise
        """
        params = self._build_params(gameid=game_id)
        
        try:
            data = self._make_request('jeuInfos.php', params)
            return self._parse_game_data(data)
        except GameNotFoundError:
            return None
    
    def _parse_game_data(self, data: Dict) -> GameInfo:
        """Parse API response into GameInfo object."""
        if 'response' not in data:
            raise GameNotFoundError("Game not found in response")
        
        response = data['response']
        if 'jeu' not in response:
            raise GameNotFoundError("No game data in response")
        
        jeu = response['jeu']
        
        # Extract basic game information
        game_info = GameInfo(
            id=str(jeu.get('id', '')),
            name=self._get_localized_text(jeu.get('noms', [])),
            description=self._get_localized_text(jeu.get('synopsis', [])),
            publisher=self._get_text_from_list(jeu.get('editeur', [])),
            developer=self._get_text_from_list(jeu.get('developpeur', [])),
            players=jeu.get('joueurs', {}).get('text', ''),
            rating=jeu.get('note', {}).get('text', ''),
            release_date=self._get_release_date(jeu.get('dates', [])),
            genre=self._get_text_from_list(jeu.get('genres', [])),
            system=jeu.get('systeme', {}).get('text', ''),
            raw_data=jeu
        )
        
        # Parse media
        medias = jeu.get('medias', [])
        for media_group in medias:
            for media_item in media_group.get('media', []):
                media_type = media_item.get('type', '')
                media_url = media_item.get('url', '')
                
                if media_url:
                    game_media = GameMedia(
                        media_type=media_type,
                        url=media_url,
                        format=media_item.get('format', ''),
                        region=media_item.get('region', ''),
                        size=media_item.get('size', '')
                    )
                    game_info.media.append(game_media)
        
        return game_info
    
    def _get_localized_text(self, text_list: List[Dict]) -> str:
        """Get localized text, preferring the configured language."""
        if not text_list:
            return ""
        
        # Try to find text in preferred language
        for item in text_list:
            if item.get('langue') == self.language:
                return item.get('text', '')
        
        # Fall back to first available text
        return text_list[0].get('text', '') if text_list else ""
    
    def _get_text_from_list(self, item_list: List[Dict]) -> str:
        """Extract text from a list of items."""
        if not item_list:
            return ""
        return item_list[0].get('text', '') if item_list else ""
    
    def _get_release_date(self, dates_list: List[Dict]) -> str:
        """Get release date, preferring worldwide or regional releases."""
        if not dates_list:
            return ""
        
        # Prefer worldwide release
        for date_item in dates_list:
            if date_item.get('region') in ['wor', 'us']:
                return date_item.get('text', '')
        
        # Fall back to first available date
        return dates_list[0].get('text', '') if dates_list else ""
    
    def download_media(self, 
                      game_info: GameInfo, 
                      media_types: List[str], 
                      output_dir: Union[str, Path],
                      preferred_regions: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Download specific media types for a game.
        
        Args:
            game_info: GameInfo object
            media_types: List of media types to download
            output_dir: Directory to save media files
            preferred_regions: Preferred regions for media
            
        Returns:
            Dictionary mapping media types to download success status
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for media_type in media_types:
            media = game_info.get_best_media(media_type, preferred_regions)
            if media:
                # Generate filename
                safe_name = "".join(c for c in game_info.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_name}_{media_type}.{media.format}"
                filepath = output_dir / filename
                
                results[media_type] = media.download(filepath)
            else:
                logger.warning(f"No {media_type} media found for {game_info.name}")
                results[media_type] = False
        
        return results


# Convenience functions for common use cases
def quick_search(dev_id: str, 
                dev_password: str, 
                rom_path: Union[str, Path], 
                platform: str,
                user_id: Optional[str] = None,
                user_password: Optional[str] = None) -> Optional[GameInfo]:
    """
    Quick search for a ROM file.
    
    Args:
        dev_id: Developer ID
        dev_password: Developer password  
        rom_path: Path to ROM file
        platform: Platform name
        user_id: Optional user ID
        user_password: Optional user password
        
    Returns:
        GameInfo if found, None otherwise
    """
    client = ScreenScraperClient(
        dev_id=dev_id,
        dev_password=dev_password,
        user_id=user_id,
        user_password=user_password
    )
    
    return client.search_by_file(rom_path, platform)


def download_box_art(dev_id: str,
                    dev_password: str,
                    rom_path: Union[str, Path],
                    platform: str,
                    output_dir: Union[str, Path],
                    user_id: Optional[str] = None,
                    user_password: Optional[str] = None) -> bool:
    """
    Quick function to download box art for a ROM.
    
    Returns:
        True if successful, False otherwise
    """
    game_info = quick_search(dev_id, dev_password, rom_path, platform, user_id, user_password)
    
    if not game_info:
        return False
    
    client = ScreenScraperClient(dev_id, dev_password, user_id=user_id, user_password=user_password)
    results = client.download_media(game_info, ['box-2D'], output_dir)
    
    return results.get('box-2D', False)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    import os
    
    # You need to get these from https://www.screenscraper.fr/
    DEV_ID = os.getenv('SCREENSCRAPER_DEV_ID', 'your_dev_id')
    DEV_PASSWORD = os.getenv('SCREENSCRAPER_DEV_PASSWORD', 'your_dev_password')
    
    # Optional user credentials for registered users
    USER_ID = os.getenv('SCREENSCRAPER_USER_ID')
    USER_PASSWORD = os.getenv('SCREENSCRAPER_USER_PASSWORD')
    
    print("ScreenScraper.fr Python Library Example")
    print("=" * 40)
    
    try:
        # Initialize client
        client = ScreenScraperClient(
            dev_id=DEV_ID,
            dev_password=DEV_PASSWORD,
            user_id=USER_ID,
            user_password=USER_PASSWORD,
            software_name="ScreenScraperPython Example"
        )
        
        # Example 1: Search by game name
        print("Searching for 'Super Mario Bros' on NES...")
        game = client.search_by_name("Super Mario Bros", "nes")
        
        if game:
            print(f"Found: {game.name}")
            print(f"Description: {game.description[:100]}...")
            print(f"Publisher: {game.publisher}")
            print(f"Available media types: {[m.media_type for m in game.media]}")
            
            # Download box art
            print("\nDownloading box art...")
            results = client.download_media(game, ['box-2D'], './downloads')
            print(f"Download results: {results}")
        else:
            print("Game not found")
    
    except Exception as e:
        print(f"Error: {e}")

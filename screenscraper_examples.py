#!/usr/bin/env python3
"""
ScreenScraper.fr Python Library - Examples and Test Cases
========================================================

This file contains examples and test cases for the ScreenScraper.fr library.
You can use this as a reference for implementing your own scraping solutions.

Before running, make sure to set your API credentials:
- SCREENSCRAPER_DEV_ID
- SCREENSCRAPER_DEV_PASSWORD
- SCREENSCRAPER_USER_ID (optional but recommended)
- SCREENSCRAPER_USER_PASSWORD (optional but recommended)
"""

import os
import sys
from pathlib import Path
import json

# Import the library (adjust import based on your setup)
try:
    from screenscraper import (
        ScreenScraperClient, 
        GameInfo, 
        GameMedia,
        ScreenScraperError,
        APIQuotaExceededError,
        APIClosedError,
        GameNotFoundError,
        quick_search,
        download_box_art
    )
except ImportError:
    print("Please ensure the screenscraper.py file is in your Python path")
    sys.exit(1)


def get_credentials():
    """Get API credentials from config.json file."""
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        dev_id = config.get('screenscraper', {}).get('dev_id')
        dev_password = config.get('screenscraper', {}).get('dev_password')
        user_id = config.get('screenscraper', {}).get('user_id')
        user_password = config.get('screenscraper', {}).get('user_password')
    except FileNotFoundError:
        print("Error: config.json file not found")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json")
        return None
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return None
    
    if not dev_id or not dev_password:
        print("Error: Please set SCREENSCRAPER_DEV_ID and SCREENSCRAPER_DEV_PASSWORD environment variables")
        print("You can get these credentials from https://www.screenscraper.fr/")
        return None
    
    return dev_id, dev_password, user_id, user_password


def example_1_basic_search():
    """Example 1: Basic game search by name."""
    print("\n" + "="*50)
    print("EXAMPLE 1: Basic Game Search")
    print("="*50)
    
    credentials = get_credentials()
    if not credentials:
        return
    
    dev_id, dev_password, user_id, user_password = credentials
    
    try:
        # Initialize client
        client = ScreenScraperClient(
            dev_id=dev_id,
            dev_password=dev_password,
            user_id=user_id,
            user_password=user_password,
            software_name="ScreenScraperPython Examples"
        )
        
        # Search for a well-known game
        print("Searching for 'Super Mario Bros' on NES...")
        game = client.search_by_name("Super Mario Bros", "nes")
        
        if game:
            print(f"✓ Found: {game.name}")
            print(f"  Publisher: {game.publisher}")
            print(f"  Developer: {game.developer}")
            print(f"  Release Date: {game.release_date}")
            print(f"  Players: {game.players}")
            print(f"  Rating: {game.rating}")
            print(f"  Description: {game.description[:100]}...")
            print(f"  Available media types: {len(game.media)} items")
            
            # Show available media
            media_types = set(m.media_type for m in game.media)
            print(f"  Media types: {', '.join(sorted(media_types))}")
        else:
            print("✗ Game not found")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def example_2_search_by_id():
    """Example 2: Search by ScreenScraper game ID."""
    print("\n" + "="*50)
    print("EXAMPLE 2: Search by Game ID")
    print("="*50)
    
    credentials = get_credentials()
    if not credentials:
        return
    
    dev_id, dev_password, user_id, user_password = credentials
    
    try:
        client = ScreenScraperClient(
            dev_id=dev_id,
            dev_password=dev_password,
            user_id=user_id,
            user_password=user_password
        )
        
        # Search for a game by ID (this is a known Super Mario Bros ID)
        print("Searching for game ID 3...")
        game = client.search_by_id("3")
        
        if game:
            print(f"✓ Found: {game.name}")
            print(f"  Game ID: {game.id}")
            print(f"  System: {game.system}")
        else:
            print("✗ Game not found")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def example_3_media_operations():
    """Example 3: Working with game media."""
    print("\n" + "="*50)
    print("EXAMPLE 3: Media Operations")
    print("="*50)
    
    credentials = get_credentials()
    if not credentials:
        return
    
    dev_id, dev_password, user_id, user_password = credentials
    
    try:
        client = ScreenScraperClient(
            dev_id=dev_id,
            dev_password=dev_password,
            user_id=user_id,
            user_password=user_password
        )
        
        # Search for a game with rich media
        print("Searching for 'The Legend of Zelda' on NES...")
        game = client.search_by_name("The Legend of Zelda", "nes")
        
        if game:
            print(f"✓ Found: {game.name}")
            
            # Analyze available media
            print(f"\nMedia Analysis:")
            print(f"  Total media items: {len(game.media)}")
            
            media_by_type = {}
            for media in game.media:
                if media.media_type not in media_by_type:
                    media_by_type[media.media_type] = []
                media_by_type[media.media_type].append(media)
            
            for media_type, media_list in media_by_type.items():
                print(f"  {media_type}: {len(media_list)} items")
                for media in media_list[:2]:  # Show first 2 items
                    print(f"    - {media.format} ({media.region})")
            
            # Get best media examples
            print(f"\nBest Media Examples:")
            
            box_art = game.get_best_media('box-2D', ['us', 'wor', 'eu'])
            if box_art:
                print(f"  Best box art: {box_art.format} from {box_art.region}")
            
            screenshot = game.get_best_media('screenshot')
            if screenshot:
                print(f"  Best screenshot: {screenshot.format}")
            
            # Demonstrate download (to temp directory)
            temp_dir = Path('./temp_downloads')
            temp_dir.mkdir(exist_ok=True)
            
            print(f"\nDownloading sample media to {temp_dir}...")
            results = client.download_media(
                game, 
                ['box-2D'], 
                temp_dir,
                preferred_regions=['us', 'wor']
            )
            
            for media_type, success in results.items():
                status = "✓" if success else "✗"
                print(f"  {status} {media_type}")
                
        else:
            print("✗ Game not found")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def example_4_platform_support():
    """Example 4: Demonstrate platform support."""
    print("\n" + "="*50)
    print("EXAMPLE 4: Platform Support")
    print("="*50)
    
    credentials = get_credentials()
    if not credentials:
        return
    
    dev_id, dev_password, user_id, user_password = credentials
    
    try:
        client = ScreenScraperClient(
            dev_id=dev_id,
            dev_password=dev_password,
            user_id=user_id,
            user_password=user_password
        )
        
        # Test different platforms
        test_games = [
            ("Sonic the Hedgehog", "genesis"),
            ("Super Mario World", "snes"),
            ("Tetris", "gameboy"),
            ("Final Fantasy VII", "psx"),
        ]
        
        print("Testing different platforms:")
        
        for game_name, platform in test_games:
            print(f"\n  Searching '{game_name}' on {platform.upper()}...")
            
            try:
                game = client.search_by_name(game_name, platform)
                if game:
                    print(f"    ✓ Found: {game.name}")
                    print(f"      System: {game.system}")
                    print(f"      Media items: {len(game.media)}")
                else:
                    print(f"    ✗ Not found")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                
        # Show supported platforms
        print(f"\nSupported platforms ({len(client.PLATFORMS)}):")
        for platform, system_id in sorted(client.PLATFORMS.items()):
            print(f"  {platform}: {system_id}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def example_5_error_handling():
    """Example 5: Demonstrate error handling."""
    print("\n" + "="*50)
    print("EXAMPLE 5: Error Handling")
    print("="*50)
    
    credentials = get_credentials()
    if not credentials:
        return
    
    dev_id, dev_password, user_id, user_password = credentials
    
    # Test with invalid credentials
    print("Testing error handling scenarios:")
    
    # 1. Invalid platform
    try:
        client = ScreenScraperClient(dev_id, dev_password)
        game = client.search_by_name("Test", "invalid_platform")
    except ValueError as e:
        print(f"  ✓ Caught invalid platform error: {e}")
    
    # 2. Non-existent game
    try:
        client = ScreenScraperClient(dev_id, dev_password, user_id=user_id, user_password=user_password)
        game = client.search_by_name("This Game Does Not Exist 12345", "nes")
        if not game:
            print(f"  ✓ Correctly handled non-existent game (returned None)")
    except GameNotFoundError:
        print(f"  ✓ Caught GameNotFoundError for non-existent game")
    except Exception as e:
        print(f"  ⚠ Unexpected error: {e}")
    
    # 3. Invalid game ID
    try:
        game = client.search_by_id("999999999")
        if not game:
            print(f"  ✓ Correctly handled invalid game ID (returned None)")
    except GameNotFoundError:
        print(f"  ✓ Caught GameNotFoundError for invalid ID")
    except Exception as e:
        print(f"  ⚠ Unexpected error: {e}")


def example_6_convenience_functions():
    """Example 6: Using convenience functions."""
    print("\n" + "="*50)
    print("EXAMPLE 6: Convenience Functions")
    print("="*50)
    
    credentials = get_credentials()
    if not credentials:
        return
    
    dev_id, dev_password, user_id, user_password = credentials
    
    try:
        # Quick search example
        print("Using quick_search function...")
        
        # Note: This would normally use a real ROM file
        # For demo purposes, we'll show the function call
        print("  quick_search('dev_id', 'dev_password', './rom.nes', 'nes')")
        print("  → This would search for a ROM file and return GameInfo")
        
        # Quick box art download example
        print("\nUsing download_box_art function...")
        print("  download_box_art('dev_id', 'dev_password', './rom.nes', 'nes', './art/')")
        print("  → This would download box art for a ROM file")
        
        print("\n  These functions are ideal for simple scripts and one-off tasks.")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_7_batch_processing_simulation():
    """Example 7: Simulate batch processing workflow."""
    print("\n" + "="*50)
    print("EXAMPLE 7: Batch Processing Simulation")
    print("="*50)
    
    credentials = get_credentials()
    if not credentials:
        return
    
    dev_id, dev_password, user_id, user_password = credentials
    
    try:
        client = ScreenScraperClient(
            dev_id=dev_id,
            dev_password=dev_password,
            user_id=user_id,
            user_password=user_password,
            request_delay=1.5  # Be extra respectful with delays
        )
        
        # Simulate processing a collection of games
        game_collection = [
            ("Super Mario Bros", "nes"),
            ("Sonic the Hedgehog", "genesis"),
            ("Tetris", "gameboy"),
        ]
        
        print("Simulating batch processing of game collection:")
        
        results = []
        
        for game_name, platform in game_collection:
            print(f"\n  Processing: {game_name} ({platform.upper()})")
            
            try:
                game = client.search_by_name(game_name, platform)
                
                if game:
                    print(f"    ✓ Found: {game.name}")
                    
                    # Count available media
                    media_count = len(game.media)
                    box_art = game.get_best_media('box-2D')
                    screenshot = game.get_best_media('screenshot')
                    
                    result = {
                        'name': game.name,
                        'platform': platform,
                        'found': True,
                        'media_count': media_count,
                        'has_box_art': box_art is not None,
                        'has_screenshot': screenshot is not None,
                        'publisher': game.publisher,
                        'year': game.release_date
                    }
                    
                    print(f"      Media items: {media_count}")
                    print(f"      Box art: {'✓' if box_art else '✗'}")
                    print(f"      Screenshot: {'✓' if screenshot else '✗'}")
                    
                else:
                    result = {'name': game_name, 'platform': platform, 'found': False}
                    print(f"    ✗ Not found")
                
                results.append(result)
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
                results.append({'name': game_name, 'platform': platform, 'error': str(e)})
        
        # Summary
        print(f"\nBatch Processing Summary:")
        print(f"  Total games processed: {len(game_collection)}")
        found_count = sum(1 for r in results if r.get('found', False))
        print(f"  Games found: {found_count}")
        print(f"  Success rate: {found_count/len(game_collection)*100:.1f}%")
        
        # Show detailed results
        print(f"\nDetailed Results:")
        for result in results:
            if result.get('found'):
                print(f"  ✓ {result['name']} ({result['platform'].upper()})")
                print(f"    Publisher: {result.get('publisher', 'Unknown')}")
                print(f"    Year: {result.get('year', 'Unknown')}")
                print(f"    Media: {result.get('media_count', 0)} items")
            elif result.get('error'):
                print(f"  ✗ {result['name']} - Error: {result['error']}")
            else:
                print(f"  ✗ {result['name']} - Not found")
                
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all examples."""
    print("ScreenScraper.fr Python Library - Examples and Tests")
    print("=" * 60)
    
    print("This script demonstrates the capabilities of the ScreenScraper.fr library.")
    print("Make sure you have set your API credentials as environment variables:")
    print("  - SCREENSCRAPER_DEV_ID")
    print("  - SCREENSCRAPER_DEV_PASSWORD")
    print("  - SCREENSCRAPER_USER_ID (optional)")
    print("  - SCREENSCRAPER_USER_PASSWORD (optional)")
    
    # Check credentials first
    if not get_credentials():
        return
    
    # Run examples
    examples = [
        example_1_basic_search,
        example_2_search_by_id,
        example_3_media_operations,
        example_4_platform_support,
        example_5_error_handling,
        example_6_convenience_functions,
        example_7_batch_processing_simulation,
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except KeyboardInterrupt:
            print(f"\n\nInterrupted during example {i}")
            break
        except Exception as e:
            print(f"\n✗ Unexpected error in example {i}: {e}")
    
    print(f"\n" + "="*60)
    print("Examples completed!")
    print("\nNext steps:")
    print("1. Modify these examples for your specific use case")
    print("2. Implement proper error handling for production use")
    print("3. Add caching to avoid repeated API calls")
    print("4. Consider contributing to the ScreenScraper database")
    
    # Cleanup
    temp_dir = Path('./temp_downloads')
    if temp_dir.exists():
        print(f"\nNote: Sample downloads are in {temp_dir}")


if __name__ == "__main__":
    main()

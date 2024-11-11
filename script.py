#!/usr/bin/env python3

import os
import yaml
import requests
from datetime import datetime
from pathlib import Path
import argparse
from typing import Dict, List, Optional
import re
import os

class ImgurBlogGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                config['imgur']['client_id'] = os.getenv("IMGUR_CLIENT_ID")
                config['imgur']['client_secret'] = os.getenv("IMGUR_CLIENT_SECRET")
                return config
        except FileNotFoundError:
            return {
                "imgur": {
                    "client_id": os.getenv("IMGUR_CLIENT_ID", ""),
                    "client_secret": os.getenv("IMGUR_CLIENT_SECRET", "")
                },
                "blog": {
                    "layout": "post",
                    "categories": ["Travel"],
                    "tags": ["Travel", "Backpacking", "RoadTrip", "Himalayas", "Photoblog", "WeekendDiaries"],
                    "background_image": "witewall_3.png",
                    "hidden": True
                }
            }

    def _extract_album_hash(self, album_url: str) -> str:
        """Extract album hash from Imgur URL."""
        match = re.search(r'imgur\.com/a/([a-zA-Z0-9-]+)', album_url)
        if not match:
            raise ValueError("Invalid Imgur album URL")
        album_hash = match.group(1)
        
        # Handle URL that includes the album name
        if '-' in album_hash:
            album_hash = album_hash.split('-')[-1]
        
        return album_hash

    def get_album_images(self, album_url: str) -> List[Dict]:
        """Fetch images from Imgur album."""
        album_hash = self._extract_album_hash(album_url)
        response = requests.get(
            f'https://api.imgur.com/3/album/{album_hash}/images',
            headers={
                'Authorization': f'Client-ID {self.config["imgur"]["client_id"]}'
            }
        )
        response.raise_for_status()
        return response.json()['data']

    def create_markdown(self, blog_title: str, image_links: List[str], output_dir: str) -> str:
        """Generate markdown file with specified format."""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        time_str = today.strftime('%H:%M:%S')
        
        # Create filename
        sanitized_title = re.sub(r'[^\w\s-]', '', blog_title).strip().lower()
        sanitized_title = re.sub(r'[-\s]+', '-', sanitized_title)
        filename = f"{date_str}-{sanitized_title}.md"
        
        # Generate markdown content
        markdown_content = [
            "---",
            f"layout: {self.config['blog']['layout']}",
            f'title: "{blog_title}"',
            f"date: {date_str} {time_str}",
            f"categories: {', '.join(self.config['blog']['categories'])}",
            f"hidden: {str(self.config['blog']['hidden']).lower()}",
            f"tags: [{', '.join(self.config['blog']['tags'])}]",
            "image:",
            f"  background: {self.config['blog']['background_image']}",
            "---",
            ""
        ]

        # Add images to markdown
        for image_link in image_links:
            markdown_content.extend([
                f'<img src="{image_link}" alt="{blog_title}">',
                ">",
                ""
            ])

        # Write markdown file
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w') as file:
            file.write('\n'.join(markdown_content))
        
        return output_path

def main():
    parser = argparse.ArgumentParser(description='Generate blog post from Imgur album')
    parser.add_argument('album_url', help='Imgur album URL')
    parser.add_argument('blog_title', help='Title for the blog post')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--output-dir', default='posts', help='Output directory for blog posts')
    
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    try:
        generator = ImgurBlogGenerator(args.config)
        
        # Get images from album
        images = generator.get_album_images(args.album_url)
        image_links = [img['link'] for img in images]
        
        # Create markdown file
        markdown_path = generator.create_markdown(
            args.blog_title,
            image_links,
            args.output_dir
        )
        
        print(f"Successfully created blog post: {markdown_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
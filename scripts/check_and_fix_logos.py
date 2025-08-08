#!/usr/bin/env python3
import re
import requests
import concurrent.futures
import argparse
from urllib.parse import urlparse
import time

class LogoChecker:
    def __init__(self, m3u_file, max_workers=20):
        self.m3u_file = m3u_file
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Alternative logo sources to try
        self.alternative_sources = [
            # Format: (original_pattern, replacement_pattern)
            (r'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/([^/]+)/([^/]+)',
             'https://i.imgur.com/{placeholder}'),  # Would need actual imgur URLs
            
            # Generic placeholder that always works
            (r'.*', 'https://via.placeholder.com/150x100/0088cc/ffffff?text={channel_name}')
        ]
        
        # Known working logos cache (you can expand this)
        self.known_working_logos = {
            'fox': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Fox_Broadcasting_Company_logo_%282019%29.svg/200px-Fox_Broadcasting_Company_logo_%282019%29.svg.png',
            'cbs': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/CBS_logo.svg/200px-CBS_logo.svg.png',
            'nbc': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/NBC_logo.svg/200px-NBC_logo.svg.png',
            'abc': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/ABC_logo.svg/200px-ABC_logo.svg.png',
            'hbo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/HBO_logo.svg/200px-HBO_logo.svg.png',
            'espn': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/ESPN_wordmark.svg/200px-ESPN_wordmark.svg.png',
            'discovery': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Discovery_channel_logo.svg/200px-Discovery_channel_logo.svg.png',
            'showtime': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Showtime.svg/200px-Showtime.svg.png',
            'starz': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Starz_2016.svg/200px-Starz_2016.svg.png',
            'cinemax': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Cinemax_logo.svg/200px-Cinemax_logo.svg.png',
        }
        
        self.broken_logos = []
        self.working_logos = []
        self.fixed_logos = {}
    
    def check_logo_url(self, url):
        """Check if a logo URL is accessible"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                # Double-check with GET for content-type
                response = self.session.get(url, timeout=5, stream=True)
                content_type = response.headers.get('Content-Type', '').lower()
                if 'image' in content_type or response.status_code == 200:
                    return True
        except Exception as e:
            pass
        return False
    
    def find_alternative_logo(self, original_url, channel_name):
        """Find an alternative logo for a broken URL"""
        # First, check known working logos
        channel_key = channel_name.lower().split()[0] if channel_name else ''
        for key, working_url in self.known_working_logos.items():
            if key in channel_key:
                if self.check_logo_url(working_url):
                    return working_url
        
        # Try to extract channel name and create placeholder
        clean_name = re.sub(r'[^\w\s]', '', channel_name).replace(' ', '+')
        placeholder_url = f'https://via.placeholder.com/150x100/0088cc/ffffff?text={clean_name}'
        
        return placeholder_url
    
    def parse_m3u(self):
        """Parse M3U file and extract logo URLs"""
        with open(self.m3u_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        entries = []
        
        for i, line in enumerate(lines):
            if line.startswith('#EXTINF'):
                # Extract logo URL
                logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                if logo_match:
                    logo_url = logo_match.group(1)
                    
                    # Extract channel name
                    name_match = re.search(r',(.+)$', line)
                    channel_name = name_match.group(1) if name_match else 'Unknown'
                    
                    entries.append({
                        'line_num': i,
                        'line': line,
                        'logo_url': logo_url,
                        'channel_name': channel_name
                    })
        
        return lines, entries
    
    def check_all_logos(self, entries):
        """Check all logos in parallel"""
        print(f"Checking {len(entries)} logo URLs...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_entry = {
                executor.submit(self.check_logo_url, entry['logo_url']): entry 
                for entry in entries
            }
            
            for future in concurrent.futures.as_completed(future_to_entry):
                entry = future_to_entry[future]
                is_working = future.result()
                
                if is_working:
                    self.working_logos.append(entry)
                    print(f"✓ {entry['channel_name']}")
                else:
                    self.broken_logos.append(entry)
                    print(f"✗ {entry['channel_name']} - {entry['logo_url']}")
    
    def fix_broken_logos(self):
        """Find alternatives for broken logos"""
        print(f"\nFinding alternatives for {len(self.broken_logos)} broken logos...")
        
        for entry in self.broken_logos:
            alternative = self.find_alternative_logo(entry['logo_url'], entry['channel_name'])
            self.fixed_logos[entry['line_num']] = alternative
            print(f"  {entry['channel_name']} -> {alternative}")
    
    def save_fixed_playlist(self, output_file):
        """Save the playlist with fixed logos"""
        lines, entries = self.parse_m3u()
        
        # Update lines with fixed logos
        for line_num, new_logo_url in self.fixed_logos.items():
            line = lines[line_num]
            # Replace the logo URL
            line = re.sub(r'tvg-logo="[^"]+"', f'tvg-logo="{new_logo_url}"', line)
            lines[line_num] = line
        
        # Write the fixed playlist
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"\n✓ Saved fixed playlist to {output_file}")
    
    def generate_report(self):
        """Generate a report of logo status"""
        report = []
        report.append("=" * 60)
        report.append("LOGO CHECK REPORT")
        report.append("=" * 60)
        report.append(f"Total logos checked: {len(self.working_logos) + len(self.broken_logos)}")
        report.append(f"Working logos: {len(self.working_logos)}")
        report.append(f"Broken logos: {len(self.broken_logos)}")
        report.append(f"Fixed logos: {len(self.fixed_logos)}")
        
        if self.broken_logos:
            report.append("\nBROKEN LOGOS:")
            report.append("-" * 40)
            for entry in self.broken_logos[:20]:  # Show first 20
                report.append(f"  - {entry['channel_name']}")
                report.append(f"    {entry['logo_url']}")
        
        return '\n'.join(report)

def main():
    parser = argparse.ArgumentParser(description='Check and fix broken logos in M3U playlist')
    parser.add_argument('--input', default='playlist_fixed_quotes.m3u',
                       help='Input M3U file')
    parser.add_argument('--output', default='playlist_logos_fixed.m3u',
                       help='Output M3U file with fixed logos')
    parser.add_argument('--workers', type=int, default=20,
                       help='Number of concurrent workers')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check logos, do not fix')
    
    args = parser.parse_args()
    
    checker = LogoChecker(args.input, args.workers)
    
    print("Logo Checker & Fixer")
    print("=" * 60)
    
    # Parse and check logos
    lines, entries = checker.parse_m3u()
    checker.check_all_logos(entries)
    
    # Generate report
    print("\n" + checker.generate_report())
    
    # Fix broken logos if not check-only
    if not args.check_only and checker.broken_logos:
        checker.fix_broken_logos()
        checker.save_fixed_playlist(args.output)
        
        print(f"\n✓ Created {args.output} with fixed logos")
        print(f"  - {len(checker.working_logos)} logos kept as-is")
        print(f"  - {len(checker.fixed_logos)} logos replaced")
    
    # Save report to file
    with open('logo_check_report.txt', 'w') as f:
        f.write(checker.generate_report())
        f.write(f"\n\nGenerated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n✓ Report saved to logo_check_report.txt")

if __name__ == "__main__":
    main()
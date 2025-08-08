#!/usr/bin/env python3
"""
Test IPTV channels and EPG data
"""
import requests
import re
import concurrent.futures
from urllib.parse import urlparse
import time
import xml.etree.ElementTree as ET

def test_channel_stream(url, timeout=5):
    """Test if a stream URL is accessible"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code in [200, 302, 301]:
            return True, response.status_code
        return False, response.status_code
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection Error"
    except Exception as e:
        return False, str(e)

def test_epg_data(epg_url, tvg_ids):
    """Test if EPG data is available for given tvg-ids"""
    print(f"\nTesting EPG from: {epg_url}")
    try:
        response = requests.get(epg_url, timeout=10)
        if response.status_code != 200:
            return {}, f"EPG fetch failed: {response.status_code}"
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Find all channels in EPG
        epg_channels = {}
        for channel in root.findall('.//channel'):
            channel_id = channel.get('id')
            if channel_id:
                display_name = channel.find('display-name')
                epg_channels[channel_id] = display_name.text if display_name is not None else channel_id
        
        # Check which of our channels have EPG
        matched = {}
        unmatched = []
        for tvg_id in tvg_ids:
            if tvg_id in epg_channels:
                matched[tvg_id] = epg_channels[tvg_id]
            else:
                unmatched.append(tvg_id)
        
        return matched, unmatched
        
    except Exception as e:
        return {}, f"EPG parse error: {str(e)}"

def parse_m3u(filename):
    """Parse M3U file and extract channel info"""
    channels = []
    tvg_ids = []
    epg_url = None
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Get EPG URL
    if lines[0].startswith('#EXTM3U'):
        match = re.search(r'url-tvg="([^"]+)"', lines[0])
        if match:
            epg_url = match.group(1)
    
    # Parse channels
    for i in range(len(lines)):
        if lines[i].startswith('#EXTINF'):
            if i+1 < len(lines) and lines[i+1].startswith('http'):
                # Extract channel info
                info_line = lines[i]
                url = lines[i+1].strip()
                
                # Get channel name
                name_match = re.search(r',(.+)$', info_line)
                name = name_match.group(1) if name_match else "Unknown"
                
                # Get tvg-id
                tvg_match = re.search(r'tvg-id="([^"]+)"', info_line)
                tvg_id = tvg_match.group(1) if tvg_match else None
                
                channels.append({
                    'name': name,
                    'url': url,
                    'tvg_id': tvg_id
                })
                
                if tvg_id:
                    tvg_ids.append(tvg_id)
    
    return channels, tvg_ids, epg_url

def main():
    print("IPTV Channel and EPG Tester")
    print("=" * 50)
    
    # Parse playlist
    channels, tvg_ids, epg_url = parse_m3u('playlist1.m3u')
    print(f"Found {len(channels)} channels")
    print(f"Found {len(tvg_ids)} channels with EPG IDs")
    
    # Test EPG first
    if epg_url:
        print(f"\nTesting EPG: {epg_url}")
        matched, unmatched = test_epg_data(epg_url, list(set(tvg_ids)))
        if isinstance(unmatched, str):
            print(f"EPG Error: {unmatched}")
        else:
            print(f"✓ EPG channels found: {len(matched)}")
            print(f"✗ EPG channels missing: {len(unmatched)}")
            if unmatched and len(unmatched) < 20:
                print(f"  Missing: {', '.join(unmatched[:20])}")
    
    # Ask user what to test
    print("\nChannel Testing Options:")
    print("1. Test first 10 channels")
    print("2. Test specific domain channels")
    print("3. Test all channels (may take a while)")
    print("4. Skip channel testing")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '4':
        return
    
    # Select channels to test
    if choice == '1':
        test_channels = channels[:10]
    elif choice == '2':
        domain = input("Enter domain to test (e.g., moveonjoy.com): ").strip()
        test_channels = [ch for ch in channels if domain in ch['url']]
    else:
        test_channels = channels
    
    if not test_channels:
        print("No channels to test")
        return
    
    print(f"\nTesting {len(test_channels)} channels...")
    print("-" * 50)
    
    # Test channels
    working = []
    failed = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_channel = {
            executor.submit(test_channel_stream, ch['url']): ch 
            for ch in test_channels
        }
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_channel), 1):
            channel = future_to_channel[future]
            success, status = future.result()
            
            status_symbol = "✓" if success else "✗"
            print(f"{i:3}. {status_symbol} {channel['name'][:40]:40} - {status}")
            
            if success:
                working.append(channel)
            else:
                failed.append(channel)
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"✓ Working channels: {len(working)} / {len(test_channels)}")
    print(f"✗ Failed channels: {len(failed)} / {len(test_channels)}")
    
    if working:
        print(f"\nSuccess rate: {len(working)/len(test_channels)*100:.1f}%")
    
    # Show failed domains
    if failed:
        failed_domains = {}
        for ch in failed:
            domain = urlparse(ch['url']).netloc
            failed_domains[domain] = failed_domains.get(domain, 0) + 1
        
        print("\nFailed channels by domain:")
        for domain, count in sorted(failed_domains.items(), key=lambda x: x[1], reverse=True):
            print(f"  {domain}: {count} channels")

if __name__ == "__main__":
    main()
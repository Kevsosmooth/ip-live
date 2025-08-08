import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime

print("Testing EPG Data...")
print("=" * 60)

# Get EPG data
epg_url = "https://raw.githubusercontent.com/acidjesuz/EPGTalk/master/guide.xml"
print(f"Fetching EPG from: {epg_url}")

try:
    response = requests.get(epg_url, timeout=10)
    print(f"✓ EPG downloaded ({len(response.content)//1024}KB)")
    
    # Parse XML
    root = ET.fromstring(response.content)
    
    # Get all channel IDs from EPG
    epg_channels = {}
    for channel in root.findall('.//channel'):
        channel_id = channel.get('id')
        if channel_id:
            display_name = channel.find('display-name')
            epg_channels[channel_id] = display_name.text if display_name is not None else channel_id
    
    print(f"✓ EPG contains {len(epg_channels)} channels\n")
    
    # Get our playlist channels
    our_channels = []
    with open('playlist1.m3u', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'tvg-id="' in line:
                match = re.search(r'tvg-id="([^"]+)"', line)
                if match:
                    tvg_id = match.group(1)
                    name_match = re.search(r',(.+)$', line)
                    name = name_match.group(1) if name_match else tvg_id
                    our_channels.append((tvg_id, name))
    
    # Check which channels have EPG
    matched = []
    unmatched = []
    
    for tvg_id, name in our_channels:
        if tvg_id in epg_channels:
            matched.append((tvg_id, name, epg_channels[tvg_id]))
        else:
            unmatched.append((tvg_id, name))
    
    print(f"EPG Coverage:")
    print(f"✓ Channels with EPG: {len(matched)}/{len(our_channels)}")
    print(f"✗ Channels without EPG: {len(unmatched)}/{len(our_channels)}")
    
    # Show some matched channels
    if matched:
        print(f"\nSample channels WITH program guide:")
        for tvg_id, name, epg_name in matched[:15]:
            print(f"  ✓ {name[:30]:30} → EPG: {epg_name}")
    
    # Show unmatched channels
    if unmatched:
        print(f"\nChannels WITHOUT program guide:")
        for tvg_id, name in unmatched[:20]:
            print(f"  ✗ {name[:30]:30} [tvg-id: {tvg_id}]")
    
    # Check for program data
    programs = root.findall('.//programme')
    print(f"\n✓ EPG contains {len(programs)} program entries")
    
    # Sample some programs for popular channels
    popular_channels = ['ABC.us', 'CBS.us', 'NBC.us', 'FOX.us', 'HBO.us', 'ESPN.us']
    print("\nSample programs for popular channels:")
    for ch_id in popular_channels:
        ch_programs = [p for p in programs if p.get('channel') == ch_id]
        if ch_programs and ch_programs[0].find('title') is not None:
            title = ch_programs[0].find('title').text
            print(f"  {ch_id}: '{title}' + {len(ch_programs)-1} more programs")
        else:
            print(f"  {ch_id}: No programs found")
            
except Exception as e:
    print(f"✗ Error: {e}")
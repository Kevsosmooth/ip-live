import requests
import xml.etree.ElementTree as ET

# Get EPG and check actual channel IDs
response = requests.get("https://raw.githubusercontent.com/acidjesuz/EPGTalk/master/guide.xml", timeout=10)
root = ET.fromstring(response.content)

# Get first 30 channel IDs from EPG
epg_channels = []
for channel in root.findall('.//channel')[:50]:
    channel_id = channel.get('id')
    display_name = channel.find('display-name')
    if channel_id and display_name is not None:
        epg_channels.append((channel_id, display_name.text))

print("Sample Channel IDs in EPG:")
print("-" * 60)
for ch_id, name in epg_channels:
    print(f"{ch_id:35} → {name}")

# Check for common US channels
print("\n\nSearching for common US channels:")
print("-" * 60)
search_terms = ['ABC', 'CBS', 'NBC', 'FOX', 'ESPN', 'HBO', 'CNN', 'TNT', 'TBS']
found = []

for channel in root.findall('.//channel'):
    ch_id = channel.get('id')
    display_name = channel.find('display-name')
    name = display_name.text if display_name is not None else ''
    
    if ch_id and any(term in name.upper() for term in search_terms):
        found.append((ch_id, name))
        if len(found) >= 20:
            break

for ch_id, name in found:
    print(f"{ch_id:35} → {name}")
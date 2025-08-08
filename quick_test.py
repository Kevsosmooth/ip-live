import requests
import re
from urllib.parse import urlparse

# Parse playlist
channels = []
with open('playlist1.m3u', 'r') as f:
    lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].startswith('#EXTINF'):
            if i+1 < len(lines) and lines[i+1].startswith('http'):
                name = re.search(r',(.+)$', lines[i]).group(1) if re.search(r',(.+)$', lines[i]) else "Unknown"
                channels.append({'name': name, 'url': lines[i+1].strip()})

print(f"Testing {len(channels[:10])} channels...\n")

# Test first 10 channels
for i, ch in enumerate(channels[:10], 1):
    try:
        domain = urlparse(ch['url']).netloc
        resp = requests.head(ch['url'], timeout=3, allow_redirects=True)
        status = "✓" if resp.status_code in [200, 302, 301, 403] else "✗"
        print(f"{i}. {status} {ch['name'][:35]:35} [{domain}]")
    except:
        print(f"{i}. ✗ {ch['name'][:35]:35} [{domain}]")

# Test EPG
print("\n" + "="*50)
print("Testing EPG...")
try:
    epg_resp = requests.get("https://raw.githubusercontent.com/acidjesuz/EPGTalk/master/guide.xml", timeout=5)
    if epg_resp.status_code == 200:
        print(f"✓ EPG is accessible (Size: {len(epg_resp.content)//1024}KB)")
        # Check for common channel IDs
        epg_text = epg_resp.text[:50000]  # Check first 50KB
        common_ids = ['ABC.us', 'CBS.us', 'NBC.us', 'FOX.us', 'HBO.us']
        found = [id for id in common_ids if f'id="{id}"' in epg_text]
        print(f"✓ Found EPG data for: {', '.join(found)}")
    else:
        print(f"✗ EPG not accessible: {epg_resp.status_code}")
except Exception as e:
    print(f"✗ EPG error: {e}")
#!/usr/bin/env python3
"""
Fix EPG URLs and IDs in the playlist
"""

# Read the playlist
with open('playlist1.m3u', 'r') as f:
    lines = f.readlines()

# Better EPG sources for US channels
# Option 1: iptv-org EPG (most comprehensive)
new_epg_url = 'url-tvg="https://iptv-org.github.io/epg/guides/us/directv.com.epg.xml"'

# Alternative EPG sources:
# url-tvg="https://raw.githubusercontent.com/usa-local-epg/usa-locals/main/epg.xml"
# url-tvg="http://epg.streamstv.me/epg/guide-usa.xml.gz"
# url-tvg="https://i.mjh.nz/PlutoTV/all.xml.gz"

# Update the first line with new EPG
if lines[0].startswith('#EXTM3U'):
    lines[0] = f'#EXTM3U {new_epg_url}\n'

# Save updated playlist
with open('playlist1.m3u', 'w') as f:
    f.writelines(lines)

print("Updated EPG URL to: https://iptv-org.github.io/epg/guides/us/directv.com.epg.xml")
print("\nAlternative EPG sources you can try:")
print("1. https://raw.githubusercontent.com/usa-local-epg/usa-locals/main/epg.xml")
print("2. http://epg.streamstv.me/epg/guide-usa.xml.gz")
print("3. https://i.mjh.nz/PlutoTV/all.xml.gz")
print("4. https://iptv-org.github.io/epg/guides/us/tvguide.com.epg.xml")
print("\nNote: You may need to adjust tvg-id values to match the EPG source.")
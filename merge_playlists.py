import re

# Read the main playlist
with open('playlist_fixed_quotes.m3u', 'r') as f:
    main_playlist = f.read()

# Read the final master channels
with open('final_master_channels.m3u', 'r') as f:
    master_playlist = f.read()

# Extract channels from main playlist
main_channels = {}
lines = main_playlist.split('\n')
for i in range(len(lines)):
    if lines[i].startswith('#EXTINF'):
        if i+1 < len(lines) and lines[i+1].startswith('http'):
            url = lines[i+1].strip()
            info = lines[i].strip()
            main_channels[url] = info

print(f"Main playlist has {len(main_channels)} unique channels")

# Extract channels from master playlist (excluding a1xs and nexgen)
master_channels = {}
lines = master_playlist.split('\n')
for i in range(len(lines)):
    if lines[i].startswith('#EXTINF'):
        if i+1 < len(lines) and lines[i+1].startswith('http'):
            url = lines[i+1].strip()
            info = lines[i].strip()
            # Skip a1xs and nexgen channels
            if 'a1xs.vip' not in url and 'nexgen.bz' not in url:
                # Only add popular channels from 23.237.104.106
                if '23.237.104.106' in url:
                    # Get channel name
                    channel = url.split('/')[-2] if url.endswith('.m3u8') else ''
                    # List of popular channels to add
                    popular = ['USA_HBO', 'USA_HBO2', 'USA_HBO_FAMILY', 'USA_HBO_SIGNATURE', 
                              'USA_HBO_ZONE', 'USA_HBO_COMEDY', 'USA_CINEMAX', 'USA_STARZ',
                              'USA_STARZ_CINEMA', 'USA_STARZ_COMEDY', 'USA_ANIMAL_PLANET',
                              'USA_BOOMERANG', 'USA_CARTOON_NETWORK', 'USA_DISCOVERY',
                              'USA_TLC', 'USA_HISTORY', 'USA_TNT', 'USA_TBS', 'USA_USA',
                              'USA_FOOD_NETWORK', 'USA_DISNEY_JUNIOR', 'USA_NICK_JR',
                              'USA_SCIENCE', 'USA_PARAMOUNT_NETWORK', 'USA_TRUTV',
                              'USA_IFC', 'USA_WE_TV', 'USA_OWN', 'USA_LMN']
                    if any(p in channel for p in popular):
                        if url not in main_channels:  # Don't add duplicates
                            master_channels[url] = info
                # Add other domains (toonami, cvalley, nbcu)
                elif 'toonamiaftermath' in url or 'cvalley' in url or 'nbcu' in url:
                    master_channels[url] = info

print(f"Master playlist has {len(master_channels)} channels to add")

# Create new playlist with proper formatting
output = ['#EXTM3U url-tvg="https://raw.githubusercontent.com/acidjesuz/EPGTalk/master/guide.xml"', '']

# Channel logo mappings for USA channels
logo_map = {
    'USA_HBO': ('HBO.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/hbo-us.png', 'HBO'),
    'USA_HBO2': ('HBO2.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/hbo-2-us.png', 'HBO2'),
    'USA_HBO_FAMILY': ('HBOFamily.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/hbo-family-us.png', 'HBO Family'),
    'USA_HBO_SIGNATURE': ('HBOSignature.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/hbo-signature-us.png', 'HBO Signature'),
    'USA_HBO_ZONE': ('HBOZone.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/hbo-zone-us.png', 'HBO Zone'),
    'USA_HBO_COMEDY': ('HBOComedy.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/hbo-comedy-us.png', 'HBO Comedy'),
    'USA_CINEMAX': ('Cinemax.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cinemax-us.png', 'Cinemax'),
    'USA_STARZ': ('Starz.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/starz-us.png', 'Starz'),
    'USA_STARZ_CINEMA': ('StarzCinema.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/starz-cinema-us.png', 'Starz Cinema'),
    'USA_STARZ_COMEDY': ('StarzComedy.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/starz-comedy-us.png', 'Starz Comedy'),
    'USA_ANIMAL_PLANET': ('AnimalPlanet.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/animal-planet-us.png', 'Animal Planet'),
    'USA_BOOMERANG': ('Boomerang.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/boomerang-us.png', 'Boomerang'),
    'USA_CARTOON_NETWORK': ('CartoonNetwork.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cartoon-network-us.png', 'Cartoon Network'),
    'USA_DISCOVERY': ('DiscoveryChannel.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/discovery-channel-us.png', 'Discovery Channel'),
    'USA_TLC': ('TLC.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/tlc-us.png', 'TLC'),
    'USA_HISTORY': ('History.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/history-us.png', 'History'),
    'USA_TNT': ('TNT.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/tnt-us.png', 'TNT'),
    'USA_TBS': ('TBS.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/tbs-us.png', 'TBS'),
    'USA_USA': ('USANetwork.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/usa-network-us.png', 'USA Network'),
    'USA_FOOD_NETWORK': ('FoodNetwork.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/food-network-us.png', 'Food Network'),
    'USA_DISNEY_JUNIOR': ('DisneyJunior.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/disney-jr-us.png', 'Disney Junior'),
    'USA_NICK_JR': ('NickJr.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/nick-jr-us.png', 'Nick Jr'),
    'USA_SCIENCE': ('ScienceChannel.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/science-channel-us.png', 'Science Channel'),
    'USA_PARAMOUNT_NETWORK': ('ParamountNetwork.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/paramount-network-us.png', 'Paramount Network'),
    'USA_TRUTV': ('truTV.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/trutv-us.png', 'truTV'),
    'USA_IFC': ('IFC.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/ifc-us.png', 'IFC'),
    'USA_WE_TV': ('WeTV.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/we-tv-us.png', 'WE tv'),
    'USA_OWN': ('OWN.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/own-us.png', 'OWN'),
    'USA_LMN': ('LifetimeMovies.us', 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/lifetime-movie-network-us.png', 'Lifetime Movies'),
}

# Group channels by category
categories = {
    'Major Networks': [],
    'News': [],
    'Sports': [],
    'Movies & Premium': [],
    'Entertainment': [],
    'Music': [],
    'Kids & Family': [],
    'Educational & Documentary': [],
    'Lifestyle & Women': [],
    'Shopping & Business': [],
    'Court & Crime': [],
    'Outdoor & Adventure': [],
    'Specialty & Others': [],
    'Canadian Content': []
}

# Add main playlist channels
for url, info in sorted(main_channels.items()):
    # Determine category from existing info
    if 'group-title=' in info:
        match = re.search(r'group-title="([^"]+)"', info)
        if match:
            category = match.group(1)
            if category in categories:
                categories[category].append((url, info))
            else:
                categories['Specialty & Others'].append((url, info))

# Add new channels from master with proper formatting
for url, info in sorted(master_channels.items()):
    if '23.237.104.106' in url:
        # Extract channel name
        channel = url.split('/')[-2] if url.endswith('.m3u8') else ''
        
        # Determine category and format info
        if channel in logo_map:
            tvg_id, logo, name = logo_map[channel]
            
            # Determine category
            if any(x in channel for x in ['HBO', 'STARZ', 'CINEMAX']):
                category = 'Movies & Premium'
            elif any(x in channel for x in ['DISCOVERY', 'ANIMAL', 'SCIENCE', 'HISTORY']):
                category = 'Educational & Documentary'
            elif any(x in channel for x in ['CARTOON', 'BOOMERANG', 'DISNEY', 'NICK']):
                category = 'Kids & Family'
            elif any(x in channel for x in ['TNT', 'TBS', 'USA', 'IFC', 'PARAMOUNT', 'TRUTV']):
                category = 'Entertainment'
            elif any(x in channel for x in ['FOOD']):
                category = 'Lifestyle & Women'
            elif any(x in channel for x in ['WE_TV', 'OWN', 'LMN']):
                category = 'Lifestyle & Women'
            else:
                category = 'Specialty & Others'
            
            new_info = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{category}",USA {name}'
            categories[category].append((url, new_info))
    else:
        # Other domains
        categories['Specialty & Others'].append((url, info))

# Write output
for category, channels in categories.items():
    if channels:
        output.append(f'# === {category} ===')
        for url, info in channels:
            output.append(info)
            output.append(url)
        output.append('')

# Save to file
with open('playlist1.m3u', 'w') as f:
    f.write('\n'.join(output))

print(f"\nCreated playlist1.m3u with {sum(len(ch) for ch in categories.values())} channels")
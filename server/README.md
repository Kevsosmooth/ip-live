# Password-Protected IPTV Setup Options

## Option 1: PHP Server (Simplest)
Deploy `get.php` to any PHP hosting:
- Shared hosting (Hostinger, Bluehost, etc.)
- VPS with Apache/Nginx + PHP
- Free hosting like 000webhost

**Access URL:**
```
http://yourserver.com/get.php?username=user1&password=pass1&type=m3u_plus&output=ts
```

## Option 2: Node.js Server
Run the Express server locally or on a VPS:

```bash
cd server
npm install
npm start
```

**Access URL:**
```
http://yourserver:8080/get.php?username=user1&password=pass1&type=m3u_plus&output=ts
```

## Option 3: Cloudflare Workers (Free & Best)
1. Sign up for Cloudflare Workers (free tier: 100,000 requests/day)
2. Create a new Worker
3. Paste the code from `cloudflare-worker.js`
4. Deploy

**Access URL:**
```
https://your-worker.your-subdomain.workers.dev?username=user1&password=pass1&type=m3u_plus
```

## Option 4: GitHub Private Repo
1. Make your repo private
2. Create a Personal Access Token (PAT)
3. Use this URL format:
```
https://USERNAME:TOKEN@raw.githubusercontent.com/Kevsosmooth/ip-live/main/playlist1.m3u
```

## Option 5: Use a Proxy Service
Services like:
- **Xtream-UI** - Professional IPTV panel ($20/month)
- **Ministra** - Another IPTV middleware
- **Flussonic** - Media server with auth

## Security Tips

### For PHP/Node.js servers:
1. **Use HTTPS** - Get free SSL from Let's Encrypt
2. **IP Whitelisting** - Restrict access to specific IPs
3. **Rate Limiting** - Prevent brute force attacks
4. **Connection Limits** - Limit concurrent streams per user
5. **Token Expiration** - Make tokens expire after X hours

### Example Nginx config for IP restriction:
```nginx
location /get.php {
    allow 192.168.1.0/24;  # Your home IP range
    allow 10.0.0.0/8;      # VPN IP range
    deny all;
    
    proxy_pass http://localhost:8080;
}
```

## Quick Setup with Replit (Free)

1. Go to [Replit.com](https://replit.com)
2. Create new Repl → Node.js
3. Upload `server.js` and `package.json`
4. Click Run
5. Your URL will be: `https://your-repl-name.username.repl.co/get.php?username=user1&password=pass1`

## Recommended: Cloudflare Workers

**Pros:**
- Free (100k requests/day)
- No server needed
- Global CDN
- DDoS protection
- Easy to update

**Setup:**
1. Sign up at [workers.cloudflare.com](https://workers.cloudflare.com)
2. Click "Create a Service"
3. Paste the worker code
4. Save and Deploy
5. Custom domain optional ($5/month)

## Testing Your Setup

Use VLC or any IPTV player:
1. Open VLC
2. Media → Open Network Stream
3. Enter your password-protected URL
4. Should load the playlist

For Tivimate/IPTV Smarters:
- Use Xtream Codes API
- Server: `yourserver.com`
- Username: `user1`
- Password: `pass1`
- Port: `8080` (or your port)
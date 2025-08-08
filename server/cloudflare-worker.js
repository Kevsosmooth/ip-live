// Cloudflare Worker for password-protected IPTV
// Deploy this to Cloudflare Workers

const USERS = {
  'user1': 'pass1',
  'user2': 'pass2',
  // Add more users here
};

// Your M3U playlist URL (can be GitHub raw URL)
const PLAYLIST_URL = 'https://raw.githubusercontent.com/Kevsosmooth/ip-live/main/playlist1.m3u';

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  
  // Parse query parameters
  const params = new URLSearchParams(url.search);
  const username = params.get('username');
  const password = params.get('password');
  const type = params.get('type') || 'm3u_plus';
  
  // Check authentication
  if (!username || !password || USERS[username] !== password) {
    return new Response('Invalid credentials', { 
      status: 401,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
  
  // Fetch the playlist
  const playlistResponse = await fetch(PLAYLIST_URL);
  let playlist = await playlistResponse.text();
  
  // Optional: Add IP restriction by modifying URLs
  const clientIP = request.headers.get('CF-Connecting-IP');
  
  // Log access (you can send this to a logging service)
  console.log(`Access granted: ${username} from ${clientIP} at ${new Date().toISOString()}`);
  
  // Return the playlist
  return new Response(playlist, {
    headers: {
      'Content-Type': 'application/x-mpegurl',
      'Content-Disposition': 'attachment; filename="playlist.m3u8"',
      'Cache-Control': 'no-cache',
    }
  });
}
const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 8080;

// User database (in production, use a real database)
const users = {
    'user1': { 
        password: 'pass1', 
        expires: new Date('2025-12-31'),
        maxConnections: 1,
        activeConnections: new Set()
    },
    'user2': { 
        password: 'pass2', 
        expires: new Date('2025-12-31'),
        maxConnections: 2,
        activeConnections: new Set()
    }
};

// Session tracking
const sessions = new Map();

// Middleware to log requests
app.use((req, res, next) => {
    const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    console.log(`[${new Date().toISOString()}] ${ip} - ${req.method} ${req.url}`);
    next();
});

// Main endpoint
app.get('/get.php', (req, res) => {
    const { username, password, type = 'm3u_plus', output = 'ts' } = req.query;
    
    // Validate credentials
    if (!username || !password || !users[username] || users[username].password !== password) {
        return res.status(401).send('Invalid credentials');
    }
    
    const user = users[username];
    
    // Check expiration
    if (user.expires < new Date()) {
        return res.status(403).send('Subscription expired');
    }
    
    // Generate session token
    const sessionToken = crypto.randomBytes(16).toString('hex');
    sessions.set(sessionToken, {
        username,
        created: new Date(),
        ip: req.ip
    });
    
    // Clean old sessions (older than 24 hours)
    for (const [token, session] of sessions.entries()) {
        if (new Date() - session.created > 24 * 60 * 60 * 1000) {
            sessions.delete(token);
        }
    }
    
    // Read playlist
    const playlistPath = path.join(__dirname, '../playlist1.m3u');
    let playlist = fs.readFileSync(playlistPath, 'utf8');
    
    // Modify URLs to include authentication
    const serverUrl = `http://${req.get('host')}`;
    
    // Replace stream URLs with proxied URLs
    playlist = playlist.replace(/(https?:\/\/[^\s]+\.m3u8)/g, (match, url) => {
        const encodedUrl = Buffer.from(url).toString('base64');
        return `${serverUrl}/stream/${sessionToken}/${encodedUrl}`;
    });
    
    res.setHeader('Content-Type', 'application/x-mpegurl');
    res.setHeader('Content-Disposition', 'attachment; filename="playlist.m3u8"');
    res.send(playlist);
});

// Stream proxy endpoint
app.get('/stream/:token/:encodedUrl', (req, res) => {
    const { token, encodedUrl } = req.params;
    
    // Validate session
    const session = sessions.get(token);
    if (!session) {
        return res.status(401).send('Invalid session');
    }
    
    // Decode original URL
    const originalUrl = Buffer.from(encodedUrl, 'base64').toString('utf8');
    
    // Here you would proxy the stream
    // For demonstration, just redirect (in production, use proper proxying)
    res.redirect(originalUrl);
});

// Player API endpoint (for Xtream Codes compatibility)
app.get('/player_api.php', (req, res) => {
    const { username, password, action } = req.query;
    
    if (!username || !password || !users[username] || users[username].password !== password) {
        return res.status(401).json({ user_info: { auth: 0 } });
    }
    
    const user = users[username];
    
    switch(action) {
        case 'get_account_info':
            res.json({
                user_info: {
                    username,
                    password,
                    auth: 1,
                    status: 'Active',
                    exp_date: Math.floor(user.expires.getTime() / 1000),
                    is_trial: '0',
                    active_cons: user.activeConnections.size.toString(),
                    created_at: Math.floor(new Date('2024-01-01').getTime() / 1000),
                    max_connections: user.maxConnections.toString()
                },
                server_info: {
                    url: req.get('host'),
                    port: PORT,
                    https_port: 443,
                    server_protocol: 'http',
                    rtmp_port: 1935,
                    timezone: 'America/New_York',
                    timestamp_now: Math.floor(Date.now() / 1000),
                    time_now: new Date().toISOString()
                }
            });
            break;
            
        case 'get_live_categories':
            res.json([
                { category_id: "1", category_name: "Major Networks", parent_id: 0 },
                { category_id: "2", category_name: "News", parent_id: 0 },
                { category_id: "3", category_name: "Sports", parent_id: 0 },
                { category_id: "4", category_name: "Movies & Premium", parent_id: 0 },
                { category_id: "5", category_name: "Entertainment", parent_id: 0 }
            ]);
            break;
            
        default:
            res.json({ status: 'error', message: 'Unknown action' });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        uptime: process.uptime(),
        sessions: sessions.size,
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(`IPTV Server running on port ${PORT}`);
    console.log(`Access URL: http://localhost:${PORT}/get.php?username=USER&password=PASS&type=m3u_plus&output=ts`);
});
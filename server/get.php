<?php
// Simple IPTV API with authentication
// Usage: http://yourserver.com/get.php?username=USER&password=PASS&type=m3u_plus&output=ts

// Configuration
$users = [
    'user1' => ['password' => 'pass1', 'expires' => '2025-12-31'],
    'user2' => ['password' => 'pass2', 'expires' => '2025-12-31'],
    // Add more users here
];

// Path to your M3U file
$playlist_file = 'playlist1.m3u';

// Get parameters
$username = $_GET['username'] ?? '';
$password = $_GET['password'] ?? '';
$type = $_GET['type'] ?? 'm3u_plus';
$output = $_GET['output'] ?? 'ts';

// Validate user
if (!isset($users[$username]) || $users[$username]['password'] !== $password) {
    http_response_code(401);
    die('Invalid credentials');
}

// Check expiration
if (strtotime($users[$username]['expires']) < time()) {
    http_response_code(403);
    die('Subscription expired');
}

// Set appropriate headers
header('Content-Type: application/x-mpegurl');
header('Content-Disposition: attachment; filename="playlist.m3u8"');

// Read and modify the playlist
$playlist = file_get_contents($playlist_file);

// Add user agent and referrer protection to URLs if needed
$playlist = preg_replace_callback(
    '/(https?:\/\/[^\s]+)/',
    function($matches) use ($username, $password) {
        $url = $matches[1];
        // Add authentication token to each URL
        $token = base64_encode($username . ':' . $password);
        return $url . '#token=' . $token;
    },
    $playlist
);

echo $playlist;
?>
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3001;
const ROOT = path.join(__dirname, 'frontend');

const MIME_TYPES = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.txt': 'text/plain',
    '.json': 'application/json'
};

http.createServer((req, res) => {
    // Strip query strings (e.g. ?v=4)
    const cleanUrl = req.url.split('?')[0];
    let filePath = path.join(ROOT, cleanUrl === '/' ? 'index.html' : cleanUrl);
    const ext = path.extname(filePath);
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404);
            res.end('File not found');
            return;
        }
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(content, 'utf-8');
    });
}).listen(PORT, () => {
    console.log(`Node server running at http://localhost:${PORT}`);
});

#!/usr/bin/env python3
import urllib.request, urllib.error, json, os, gzip
from http.server import HTTPServer, BaseHTTPRequestHandler

HTML_FILE = os.path.join(os.path.dirname(__file__), 'yki_dashboard.html')
YKI_URL   = 'https://yki.opintopolku.fi/yki/api/exam-session'
YKI_HEADERS = {
    'User-Agent':    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0',
    'Accept':        'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer':       'https://yki.opintopolku.fi/yki/ilmoittautuminen',
    'Caller-Id':     '1.2.246.562.10.00000000001.yki',
    'CSRF':          '6acb9d83-08c6-4b9c-a38f-b227b3a2680a',
    'Cookie':        'CSRF=6acb9d83-08c6-4b9c-a38f-b227b3a2680a',
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/api/exam-session':
            self._proxy()
        elif path in ('/', '/index.html'):
            self._serve_html()
        else:
            self.send_error(404)

    def _proxy(self):
        try:
            req = urllib.request.Request(YKI_URL, headers=YKI_HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                enc = resp.headers.get('Content-Encoding', '')
            body = gzip.decompress(raw) if enc == 'gzip' else raw
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(str(e).encode())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def _serve_html(self):
        try:
            with open(HTML_FILE, 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_error(404, 'yki_dashboard.html not found')

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f'Serving on http://0.0.0.0:{port}')
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

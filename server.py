#!/usr/bin/env python3
"""
Lokale testserver voor stankmelding.html.
Serveert de HTML-pagina en handelt het versturen af (vervangt de Cloudflare Worker).

Gebruik: python3 server.py
Open daarna: http://localhost:8000
"""

import json
import os
import re
import ssl
import urllib.request
import urllib.parse
import urllib.error
import http.server
import random
import time
from datetime import datetime

# formulieren.limburg.nl stuurt sinds de certificaatvernieuwing van 23-07-2026 alleen
# het leaf-certificaat, zonder de Sectigo-tussenliggende CA. Browsers vissen die missende
# schakel zelf op (AIA chasing); Python's ssl-module doet dat niet, dus voegen we hem
# hier expliciet toe als vertrouwd, anders faalt elke HTTPS-call met een certificaatfout.
SECTIGO_OV_R36_INTERMEDIATE = """-----BEGIN CERTIFICATE-----
MIIGTDCCBDSgAwIBAgIQLBo8dulD3d3/GRsxiQrtcTANBgkqhkiG9w0BAQwFADBf
MQswCQYDVQQGEwJHQjEYMBYGA1UEChMPU2VjdGlnbyBMaW1pdGVkMTYwNAYDVQQD
Ey1TZWN0aWdvIFB1YmxpYyBTZXJ2ZXIgQXV0aGVudGljYXRpb24gUm9vdCBSNDYw
HhcNMjEwMzIyMDAwMDAwWhcNMzYwMzIxMjM1OTU5WjBgMQswCQYDVQQGEwJHQjEY
MBYGA1UEChMPU2VjdGlnbyBMaW1pdGVkMTcwNQYDVQQDEy5TZWN0aWdvIFB1Ymxp
YyBTZXJ2ZXIgQXV0aGVudGljYXRpb24gQ0EgT1YgUjM2MIIBojANBgkqhkiG9w0B
AQEFAAOCAY8AMIIBigKCAYEApkMtJ3R06jo0fceI0M52B7K+TyMeGcv2BQ5AVc3j
lYt76TvHIu/nNe22W/RJXX9rWUD/2GE6GF5x0V4bsY7K3IeJ8E7+KzG/TGboySfD
u+F52jqQBbY62ofhYjMeiAbLI02+FqwHeM8uIrUtcX8b2RCxF358TB0NHVccAXZc
FYgZndZCeXxjuca7pJJ20LLUnXtgXcjAE1vY4WvbReW0W6mkeZyNGdmpTcFs5Y+s
yy6LtE5Zocji9J9NlNnReox2RWVyEXpA1ChZ4gqN+ZpVSIQ0HBorVFbBKyhdZyEX
gZgNSNtBRwxqwIzJePJhYd4ZUhO1vk+/uP3nwDk0p95q/j7naXNCSvESnrHPypaB
WRK066nKfPRPi9m9kIOhMdYfS8giFRTcdgL24Ycilj7ecAK9Trh0VbjwouJ4WH+x
bt47u68ZFCD/ac55I0DNHkCpaPruj6e9Rmr7K46wZDAYXuEAqB7tGG/jd6JAA+H2
O44CV98NRsU213f1kScIZntNAgMBAAGjggGBMIIBfTAfBgNVHSMEGDAWgBRWc1hk
lfmSGrASKgRieaFAFYghSTAdBgNVHQ4EFgQU42Z0u3BojSxdTg6mSo+bNyKcgpIw
DgYDVR0PAQH/BAQDAgGGMBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYDVR0lBBYwFAYI
KwYBBQUHAwEGCCsGAQUFBwMCMBsGA1UdIAQUMBIwBgYEVR0gADAIBgZngQwBAgIw
VAYDVR0fBE0wSzBJoEegRYZDaHR0cDovL2NybC5zZWN0aWdvLmNvbS9TZWN0aWdv
UHVibGljU2VydmVyQXV0aGVudGljYXRpb25Sb290UjQ2LmNybDCBhAYIKwYBBQUH
AQEEeDB2ME8GCCsGAQUFBzAChkNodHRwOi8vY3J0LnNlY3RpZ28uY29tL1NlY3Rp
Z29QdWJsaWNTZXJ2ZXJBdXRoZW50aWNhdGlvblJvb3RSNDYucDdjMCMGCCsGAQUF
BzABhhdodHRwOi8vb2NzcC5zZWN0aWdvLmNvbTANBgkqhkiG9w0BAQwFAAOCAgEA
BZXWDHWC3cubb/e1I1kzi8lPFiK/ZUoH09ufmVOrc5ObYH/XKkWUexSPqRkwKFKr
7r8OuG+p7VNB8rifX6uopqKAgsvZtZsq7iAFw04To6vNcxeBt1Eush3cQ4b8nbQR
MQLChgEAqwhuXp9P48T4QEBSksYav7+aFjNySsLYlPzNqVM3RNwvBdvp6vgDtGwc
xlKQZVuuNVIaoYyls8swhxDeSHKpRdxRauTLZ+pl+wGvy0pnrLEJGSz9mOEmfbod
e/XopR2NGqaHJ6bIjyxPu6UtyQGI26En7UAEozACrHz06Nx2jTAY9E6NeB6XuobE
wLK025ZRmvglcURG1BrV24tGHHTgxCe8M3oGlpUSMTKQ2dkgljZVYt+gKdFtWELZ
MuRdi+X3XsrR8LFz+aLUiDRfQqhmw3RxjIyVKvvu9UPYY1nsvxYmFnUSeM+2q1z/
iPUry+xDY9MC6+IhleKT094VKdFVp7LXH42+wvU+17lRolQ2mK2N/nBLVBwaIhib
QXw4VYKwB86Bc6eS6iqsc94KEgD/U4VsjmgfhK+Xp4NM+VYzTTa3QeV3p8xOM0cw
q1p8oZFA+OBcz3FYWpDIe5j0NWKlw9hXsTyPY/HeZUV59akskSOSRSmDfe8wJDPX
58uB9/7lud0G3x0pxQAcffP0ayKavNwDTw4UfJ34cEw=
-----END CERTIFICATE-----
"""

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.load_verify_locations(cadata=SECTIGO_OV_R36_INTERMEDIATE)

KV_FILE = 'kv_store.json'

def kv_load():
    if os.path.exists(KV_FILE):
        with open(KV_FILE) as f:
            return json.load(f)
    return {'totaal': 0, 'dagen': {}}

def kv_save(data):
    with open(KV_FILE, 'w') as f:
        json.dump(data, f)

def kv_increment(dag):
    data = kv_load()
    data['totaal'] = data.get('totaal', 0) + 1
    data['dagen'][dag] = data['dagen'].get(dag, 0) + 1
    kv_save(data)

def kv_teller():
    data = kv_load()
    dagen = sorted(data.get('dagen', {}).items(), reverse=True)[:30]
    return {
        'totaal': data.get('totaal', 0),
        'dagen': [{'datum': d, 'aantal': n} for d, n in dagen]
    }

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Android 14; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
]

PORT = 8002
HTML_FILE = 'stankmelding.html'
FORM_URL = 'https://formulieren.limburg.nl/provincielimburg/milieuklacht'

# Cloudflare-edge foutcodes die meestal tijdelijk zijn (edge kon origin niet bereiken/verifiëren)
RETRYABLE_STATUSES = {502, 503, 504, 522, 523, 524, 525, 526, 527, 530}


def urlopen_with_retry(req, timeout=15, attempts=3, delay=0.5):
    """Zoals urllib.request.urlopen, maar met retries op tijdelijke Cloudflare-foutcodes."""
    last_err = None
    for i in range(attempts):
        try:
            return urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT)
        except urllib.error.HTTPError as e:
            if e.code not in RETRYABLE_STATUSES or i == attempts - 1:
                raise
            last_err = e
        except urllib.error.URLError as e:
            if i == attempts - 1:
                raise
            last_err = e
        time.sleep(delay * (i + 1))
    raise last_err


def fetch_form_tokens():
    """Haal de Limburg-formulierpagina op en extraheer de sessietokens."""
    req = urllib.request.Request(
        FORM_URL,
        headers={
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'nl-NL,nl;q=0.9',
        }
    )
    with urlopen_with_retry(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='replace')
        cookies = resp.getheader('Set-Cookie') or ''
    return html, cookies


def extract_field(html, name):
    for pattern in [
        rf'name="{name}"[^>]*value="([^"]*)"',
        rf'value="([^"]*)"[^>]*name="{name}"',
    ]:
        m = re.search(pattern, html)
        if m:
            return m.group(1)
    return None


def submit_form(data):
    """Haal sessietokens op en verstuur het formulier naar Limburg."""
    anoniem = not data.get('naam') and not data.get('telefoon') and not data.get('email')
    html, cookie_header = fetch_form_tokens()

    rid         = extract_field(html, '_fd_rid')
    guid        = extract_field(html, '_fd_guid')
    action_match = re.search(r'action="(https?://formulieren\.limburg\.nl[^""]*/~new/[^"]+)"', html)

    if not rid or not guid or not action_match:
        raise ValueError('Sessietokens niet gevonden — probeer opnieuw')

    # JavaScript voegt done=1&exists=false toe vóór het versturen
    post_url = action_match.group(1) + '&done=1&exists=false'
    cookies  = '; '.join(c.split(';')[0].strip() for c in cookie_header.split(',') if '=' in c)

    now         = datetime.now()
    started_str = now.strftime('%d-%m-%Y %H:%M:%S')

    fields = [
        ('_fd_dummy',                  'dummy'),
        ('_fd_upd',                    ''),
        ('_fd_asc',                    'ODc0MTI3bWlsaWV1a2xhY2h0'),
        ('_fd_rid',                    rid),
        ('_fd_guid',                   guid),
        ('anoniem',                    'Ja' if anoniem else 'Nee'),
        *([
            ('naam',     data.get('naam', '')),
            ('telefoon', data.get('telefoon', '')),
            ('e_mail',   data.get('email', '')),
            ('adres',    data.get('adres', '')),
        ] if not anoniem else []),
        ('onderwerp1',                 'Geluid, geur, lucht en trillingen door bedrijven'),
        ('omschrijving_milieuklacht',  data['beschrijving']),
        ('locatie_overlast',           data.get('locatie', '')),
        ('mogelijke_veroorzaker',      data.get('veroorzaker', '')),
        ('datum_en_tijdstip_hinder_',  data['datum']),
        ('tijdstip',                   data['tijdstip']),
        ('heeft_u_de_klacht_ook_eld',  'Nee'),
        ('heeft_u_op_dit_moment_nog',  data.get('nog_overlast', 'Nee')),
        ('bijlage',                    ''),
        ('upl_bijlage_name',           ''),
        ('bijlage_readonly',           ''),
        ('hdbijlage',                  '0'),
        *([('wilt_u_een_kopie_ontvange', 'Ja')] if not anoniem else []),
        ('__email',                    ''),
        ('_fd_inputhandler_init',      'hasNum=false, eventsBound=false'),
        ('_fd_hidden',                 '48300836,48292464,48292465,48292467,48319811,48293136,48292546' if anoniem else '48293136'),
        ('_fd_disabled',               ''),
        ('_fd_culture',                'en-US'),
        ('_fd_tz_offset',              '+02:00'),
        ('_fd_charset',                'UTF-8'),
        ('_fd_started',                started_str),
        ('_fd_duration',               f'{60 + random.random() * 90:.2f}'),
        ('_fd_events',                 'mousemove, click, keypress'),
    ]

    body = urllib.parse.urlencode(fields).encode('utf-8')

    with urlopen_with_retry(
        urllib.request.Request(post_url, data=body, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent':   random.choice(USER_AGENTS),
            'Referer':      FORM_URL,
            'Origin':       'https://formulieren.limburg.nl',
            **(({'Cookie': cookies}) if cookies else {}),
        }),
        timeout=15
    ) as resp:
        final_url = resp.geturl()

    success = True
    return {'success': success, 'redirectUrl': final_url}


class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f'  {self.address_string()} - {fmt % args}')

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/teller':
            self.send_json(kv_teller())
            return
        if self.path != '/':
            self.send_response(404)
            self.end_headers()
            return
        try:
            with open(HTML_FILE, 'r', encoding='utf-8') as f:
                html = f.read()
            # Alleen lokaal WORKER_URL naar het lokale endpoint herschrijven — op Render (RENDER=true)
            # serveert dit script de productie-HTML, die zijn eigen hardcoded WORKER_URL moet behouden.
            if not os.environ.get('RENDER'):
                html = re.sub(
                    r"const WORKER_URL = '[^']*';",
                    f"const WORKER_URL = 'http://localhost:{PORT}/verstuur';",
                    html,
                )
            body = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'stankmelding.html niet gevonden')

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)

        try:
            data = json.loads(body)
        except Exception:
            self.send_json({'success': False, 'error': 'Ongeldige invoer'}, 400)
            return

        required = ['beschrijving', 'datum', 'tijdstip']
        if any(not data.get(f) for f in required):
            self.send_json({'success': False, 'error': 'Vul alle verplichte velden in'}, 400)
            return

        try:
            result = submit_form(data)
            if result.get('success'):
                # Gebruik de datum van de overlast (dd-mm-yyyy → yyyy-mm-dd)
                parts = data.get('datum', '').split('-')
                dag = f'{parts[2]}-{parts[1]}-{parts[0]}' if len(parts) == 3 else datetime.now().strftime('%Y-%m-%d')
                kv_increment(dag)
            self.send_json(result)
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, 500)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', PORT))
    server = http.server.HTTPServer(('0.0.0.0', port), Handler)
    print(f'Server draait op http://0.0.0.0:{port}')
    print('Stop met Ctrl+C')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer gestopt.')

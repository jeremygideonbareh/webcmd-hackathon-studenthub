"""Probe Vercel user account state in detail."""
import sys
import urllib.request
import urllib.error

TOKEN = sys.argv[1]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def call(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": UA, "Accept": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, resp.read().decode()[:1200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


for path in ("/v2/user", "/v1/user", "/v3/user", "/v2/teams", "/v1/teams"):
    print(path, "->", call(f"https://api.vercel.com{path}"))
    print()
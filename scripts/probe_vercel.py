"""Dev check — probe Vercel API capabilities with the token."""
import sys
import urllib.request
import urllib.error

TOKEN = sys.argv[1]
TEAM = sys.argv[2] if len(sys.argv) > 2 else "team_CIPs8SFDGc0dWNEi1eb6oIqi"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def call(url):
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": UA, "Accept": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, resp.read().decode()[:1000]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


print("== projects ==")
print(call(f"https://api.vercel.com/v9/projects?teamId={TEAM}&limit=20"))
print("== deployments ==")
print(call(f"https://api.vercel.com/v6/deployments?teamId={TEAM}&limit=5"))
print("== user ==")
print(call("https://api.vercel.com/v2/user"))
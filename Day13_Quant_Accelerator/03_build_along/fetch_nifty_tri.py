"""Fetch NIFTY 50 Total Return Index (TRI) from niftyindices.com: run on YOUR laptop.
NOT tested from Hark's sandbox: the site blocked our server. The endpoint and quirks are documented at
https://github.com/satwikbasu/indian-market-data-endpoints/blob/main/endpoints/niftyindices-tri-api.md
(browser-like User-Agent required; the response 'd' is a JSON string, so parse twice; rows come newest first).
Fallback if it fails: niftyindices.com → Reports → Historical Data → "Total returns Index Values" → CSV by hand.
Writes ../06_data/raw/NIFTY50_TRI_daily.csv. The pipeline then treats it like any raw file (fingerprint, validate, seal)."""
import json, time, urllib.request, csv
from pathlib import Path
URL = "https://www.niftyindices.com/Backpage.aspx/getTotalReturnIndexString"
HDR = {"Content-Type": "application/json; charset=UTF-8", "X-Requested-With": "XMLHttpRequest",
       "Referer": "https://www.niftyindices.com/reports/historical-data",
       "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
def fetch(start, end, name="NIFTY 50"):
    body = json.dumps({"cinfo": f"{{'name':'{name}','startDate':'{start}','endDate':'{end}','indexName':'{name}'}}"}).encode()
    with urllib.request.urlopen(urllib.request.Request(URL, data=body, headers=HDR), timeout=60) as r:
        return json.loads(json.loads(r.read())["d"])
rows = []
for y in range(2007, 2027):
    rows += fetch(f"01-Jan-{y}", f"31-Dec-{y}"); time.sleep(1.5)      # be polite: 1 request per 1.5 s
out = Path(__file__).resolve().parent.parent / "06_data" / "raw" / "NIFTY50_TRI_daily.csv"
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Date", "TRI", "NTR"])
    for r in sorted(rows, key=lambda r: time.strptime(r["Date"], "%d %b %Y")):
        w.writerow([time.strftime("%Y-%m-%d", time.strptime(r["Date"], "%d %b %Y")), r["TotalReturnsIndex"], r["NTR_Value"]])
print(f"wrote {len(rows)} rows → {out}")

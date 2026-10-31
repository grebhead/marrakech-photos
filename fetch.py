import json, os, re, time, urllib.request, urllib.parse, urllib.error
UA = {"User-Agent": "MarrakechBrochure/1.0 (personal, non-commercial)"}
Q = {
 "cover": "Koutoubia Mosque Marrakech",
 "bahia": "Bahia Palace Marrakech",
 "badi": "El Badi Palace Marrakech",
 "saadian": "Saadian Tombs Marrakech",
 "jemaa": "Jemaa el-Fnaa night",
 "souks": "Marrakech souk lanterns",
 "benyoussef": "Ben Youssef Madrasa Marrakech",
 "jardinsecret": "Jardin Secret Marrakech",
 "majorelle": "Jardin Majorelle",
 "ysl": "Musee Yves Saint Laurent Marrakech",
 "menara": "Menara gardens Marrakech",
 "imlil": "Imlil Morocco",
 "essaouira": "Essaouira port",
}
def get(u):
    for attempt in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            wait = 15 * (attempt + 1)
            print(f"  rate limited, waiting {wait}s")
            time.sleep(wait)
    raise SystemExit("still rate limited, run it again in a few minutes")
strip = lambda s: re.sub("<[^>]+>", "", s or "").strip()
credits = json.load(open("credits.json")) if os.path.exists("credits.json") else {}
for key, q in Q.items():
    p = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search",
        "gsrnamespace": 6, "gsrsearch": q + " filetype:bitmap", "gsrlimit": 10,
        "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1400})
    pages = json.loads(get("https://commons.wikimedia.org/w/api.php?" + p)).get("query", {}).get("pages", {})
    time.sleep(2)
    n = 0
    for pg in sorted(pages.values(), key=lambda x: x.get("index", 99)):
        ii = (pg.get("imageinfo") or [{}])[0]
        if ii.get("mime") != "image/jpeg" or ii.get("width", 0) < 1200 or ii.get("width", 0) < ii.get("height", 0):
            continue
        n += 1
        name = f"{key}-{n}.jpg"
        if os.path.exists(name) and os.path.getsize(name) > 0:
            print("have", name)
        else:
            open(name, "wb").write(get(ii["thumburl"]))
            print("saved", name, "-", pg["title"])
            time.sleep(5)
        md = ii.get("extmetadata", {})
        credits[name] = {"title": pg["title"], "source": ii.get("descriptionurl"),
            "author": strip(md.get("Artist", {}).get("value")),
            "license": md.get("LicenseShortName", {}).get("value")}
        json.dump(credits, open("credits.json", "w"), indent=1)
        if n == 2: break
    if n == 0: print("none found for", key)
print("done")

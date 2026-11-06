"""סוכן החדשות היומי: אוסף ידיעות ממקורות RSS אמינים, מסנן ספורט, ובוחר 10 ידיעות לכל קטגוריה.

הרצה:  python agent.py
פלט:   data/news.json + news-data.js (נטען ע"י index.html, עובד גם בפתיחה ישירה של הקובץ)

אם ב-config.json מוגדר "use_claude": true וקיים משתנה הסביבה ANTHROPIC_API_KEY, Claude בוחר את הידיעות החשובות ומנסח
כותרת תמצית + סיכום קצר וקולע בעברית (כולל תרגום ידיעות מחו"ל). בלעדיו נעשה שימוש בתקציר מהמקור.
"""

import email.utils
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
ISRAEL = ZoneInfo("Asia/Jerusalem")
PER_CATEGORY = 10
MAX_AGE = timedelta(hours=36)
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")

# המקורות לפי סדר עדיפות. Google News משמש רק כגיבוי (התקצירים שלו ריקים).
SOURCES = {
    "il": [
        ("ynet", "https://www.ynet.co.il/Integration/StoryRss2.xml"),
        ("מעריב", "https://www.maariv.co.il/Rss/RssChadashot"),
        ("ישראל היום", "https://www.israelhayom.co.il/rss.xml"),
        ("וואלה", "https://rss.walla.co.il/feed/22"),
        ("Google News", "https://news.google.com/rss/headlines/section/topic/NATION?hl=he&gl=IL&ceid=IL:he"),
    ],
    "world": [
        ("ynet", "https://www.ynet.co.il/Integration/StoryRss192.xml"),
        ("mako N12", "https://rcs.mako.co.il/rss/news-world.xml"),
        ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ("The Guardian", "https://www.theguardian.com/world/rss"),
        ("Google News", "https://news.google.com/rss/headlines/section/topic/WORLD?hl=he&gl=IL&ceid=IL:he"),
    ],
    "gossip": [
        ("mako סלבס", "https://rcs.mako.co.il/rss/entertainment-celebs.xml"),
        ("וואלה סלבס", "https://rss.walla.co.il/feed/3601"),
        ("TMI מעריב", "https://www.maariv.co.il/Rss/RssFeedsTMI"),
        ("וואלה סלבס עולמי", "https://rss.walla.co.il/feed/3602"),
    ],
}

CATEGORY_NAMES = {"il": "חדשות בארץ (ישראל)", "world": "חדשות בעולם", "gossip": "רכילות, סלבס ובידור"}
FALLBACK_ICONS = {
    "il": ["🏛️", "🛡️", "💼", "⚖️", "🏙️", "🚓", "🏥", "🎓", "🚧", "📢"],
    "world": ["🌐", "🗳️", "✈️", "💹", "🕊️", "🏛️", "⚡", "🌍", "🛰️", "📰"],
    "gossip": ["✨", "🎬", "🎤", "💃", "📸", "💍", "📺", "🎶", "👗", "🌟"],
}

SPORTS = re.compile(
    r"ספורט|כדורגל|כדורסל|טניס|פורמולה|ליגת|מונדיאל|אולימפי|שחקן הרכש|מכבי ת\"א|הפועל|בית\"ר|"
    r"\b(?:sports?|football|soccer|basketball|tennis|nba|nfl|f1|premier league|olympic)\b",
    re.IGNORECASE,
)
HEBREW = re.compile("[א-ת]")
SPORTS_LINK = re.compile(r"/sports?/|sport5|one\.co\.il|/sport\b", re.IGNORECASE)


def log(*parts):
    print(datetime.now(ISRAEL).strftime("%H:%M:%S"), *parts, flush=True)


def clean(value):
    text = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def short_summary(text, limit=240):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    return cut[: end + 1] if end > 80 else cut.rsplit(" ", 1)[0] + "…"


def parse_date(value):
    try:
        date = email.utils.parsedate_to_datetime(value)
        return date if date.tzinfo else date.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def fetch_feed(source, url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 DailyNewsAgent"})
    with urllib.request.urlopen(request, timeout=20) as response:
        root = ET.fromstring(response.read())

    # וואלה מסמנים את השעה כ-GMT אבל בפועל זו שעון ישראל
    local_time = "walla.co.il" in url
    items = []
    for item in root.iter("item"):
        title = clean(item.findtext("title"))
        link = (item.findtext("link") or "").strip()
        summary = clean(item.findtext("description"))
        item_source = source
        if source == "Google News":
            match = re.search(r"\s[-–]\s([^–-]+)$", title)
            if match:
                title, item_source = title[: match.start()].strip(), match.group(1).strip()
            summary = ""  # התקציר של Google News הוא רק רשימת קישורים
        if summary.startswith(title):
            summary = summary[len(title):].strip(" .:-")
        if not title or not link.startswith("http"):
            continue
        date = parse_date(item.findtext("pubDate"))
        if date and local_time:
            date = date.replace(tzinfo=ISRAEL)
        items.append({
            "title": title,
            "summary": summary,
            "link": link,
            "source": item_source,
            "date": date,
        })
    return items


def words(title):
    return set(re.findall(r"\w{3,}", title.lower()))


def is_duplicate(item, chosen):
    mine = words(item["title"])
    for other in chosen:
        theirs = words(other["title"])
        if mine and theirs and len(mine & theirs) / len(mine | theirs) > 0.45:
            return True
    return False


def collect(category, seen_links):
    feeds = SOURCES[category]
    with ThreadPoolExecutor(len(feeds)) as pool:
        futures = [(name, pool.submit(fetch_feed, name, url)) for name, url in feeds]

    now = datetime.now(timezone.utc)
    per_feed = []
    for name, future in futures:
        try:
            items = future.result()
        except Exception as error:  # מקור אחד שנופל לא מפיל את כל הקטגוריה
            log(f"  ⚠ {name}: {error}")
            continue
        items = [
            i for i in items
            if i["link"] not in seen_links
            and not SPORTS.search(f"{i['title']} {i['summary']}") and not SPORTS_LINK.search(i["link"])
            and (i["date"] is None or now - i["date"] <= MAX_AGE)
        ]
        items.sort(key=lambda i: i["date"] or now, reverse=True)
        log(f"  {name}: {len(items)} ידיעות")
        per_feed.append(items)

    # שזירה בין המקורות לגיוון, עם סינון כפילויות
    candidates = []
    for rank in range(max((len(f) for f in per_feed), default=0)):
        for items in per_feed:
            if rank < len(items) and not is_duplicate(items[rank], candidates):
                candidates.append(items[rank])
    return candidates


def to_story(item, icon):
    return {
        "icon": icon,
        "headline": item["title"],
        "summary": short_summary(item["summary"]) or "לפרטים המלאים לחצו על הקישור לכתבה.",
        "source": item["source"],
        "link": item["link"],
        "published": item["date"].isoformat() if item["date"] else None,
    }


def summarize_with_claude(category, candidates, api_key):
    listing = "\n".join(
        f"[{n}] ({c['source']}) {c['title']} — {c['summary'][:400]}" for n, c in enumerate(candidates)
    )
    prompt = (
        f"להלן ידיעות מהיממה האחרונה בקטגוריה: {CATEGORY_NAMES[category]}.\n"
        f"בחר את {PER_CATEGORY} הידיעות החשובות והמעניינות ביותר, בלי כפילויות ובלי ספורט.\n"
        "לכל ידיעה כתוב בעברית: headline — תמצית הידיעה במשפט אחד חד (עד 12 מילים); "
        "summary — סיכום קצר וקולע של 1–2 משפטים, עובדתי, רק על סמך הטקסט שסופק; "
        "icon — אימוג'י צבעוני אחד שמתאים לנושא.\n"
        'החזר JSON בלבד בפורמט: {"stories":[{"index":0,"icon":"🏛️","headline":"...","summary":"..."}]}\n\n'
        + listing
    )
    body = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 5000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        reply = json.loads(response.read())
    text = "".join(block.get("text", "") for block in reply["content"])
    picks = json.loads(text[text.index("{"): text.rindex("}") + 1])["stories"]

    stories = []
    for pick in picks[:PER_CATEGORY]:
        item = candidates[int(pick["index"])]
        story = to_story(item, pick.get("icon") or FALLBACK_ICONS[category][len(stories)])
        story["headline"] = pick["headline"].strip()
        story["summary"] = pick["summary"].strip()
        stories.append(story)
    return stories


CONFIG_FILE = ROOT / "config.json"


# --- אנשים בכותרות הרכילות: זיהוי דרך ויקיפדיה העברית + Wikidata (רק ערכים של בני אדם) ---

WIKI_API = "https://he.wikipedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKI_HEADERS = {"User-Agent": "DailyNewsAgent/1.0 (https://github.com/kleinda/Daily-News)"}
PREFIXES = set("והלבמשכ")
STRIP = "\"“”„«»:,.!?()[]–—-|"


def wiki_get(url, params):
    query = urllib.parse.urlencode({**params, "format": "json"})
    request = urllib.request.Request(f"{url}?{query}", headers=WIKI_HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read())


def name_candidates(headline):
    """רצפים של 1–3 מילים מהכותרת, כולל גרסה בלי אותיות שימוש (וג'ניפר ← ג'ניפר)."""
    tokens = [w.strip(STRIP).replace("׳", "'") for w in headline.split()]
    found = set()
    for i in range(len(tokens)):
        first = tokens[i]
        variants = {first}
        if len(first) > 3 and first[0] in PREFIXES:
            variants.add(first[1:])
            if first[1] in PREFIXES:
                variants.add(first[2:])
        for n in (1, 2, 3):
            rest = tokens[i + 1:i + n]
            if len(rest) != n - 1 or not all(rest):
                continue
            for v in variants:
                name = " ".join([v, *rest])
                if len(name) >= 3 and (n > 1 or len(v) >= 4):
                    found.add(name)
    return found


def find_people(headlines):
    candidates = {c: h for h in headlines for c in name_candidates(h)}
    pages = {}  # שם בכותרת -> (כותרת הערך, מזהה Wikidata)
    names = sorted(candidates)
    for start in range(0, len(names), 50):
        query = wiki_get(WIKI_API, {"action": "query", "redirects": 1, "titles": "|".join(names[start:start + 50]),
                                    "prop": "pageprops", "ppprop": "wikibase_item|disambiguation"})["query"]
        aliases = {}
        for step in query.get("normalized", []) + query.get("redirects", []):
            aliases[step["to"]] = aliases.get(step["from"], step["from"])
        for page in query.get("pages", {}).values():
            props = page.get("pageprops", {})
            if "missing" in page or "disambiguation" in props or "wikibase_item" not in props:
                continue
            pages[aliases.get(page["title"], page["title"])] = (page["title"], props["wikibase_item"])
    if not pages:
        return {}

    qids = sorted({qid for _, qid in pages.values()})
    entities = {}
    for start in range(0, len(qids), 50):
        entities.update(wiki_get(WIKIDATA_API, {"action": "wbgetentities", "ids": "|".join(qids[start:start + 50]),
                                                "props": "claims|descriptions", "languages": "he"})["entities"])
    humans = {}
    for name, (title, qid) in pages.items():
        entity = entities.get(qid, {})
        kinds = [c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for c in entity.get("claims", {}).get("P31", [])]
        if "Q5" in kinds:
            humans[name] = (title, entity.get("descriptions", {}).get("he", {}).get("value", ""))
    if not humans:
        return {}

    titles = sorted({title for title, _ in humans.values()})
    details = {}
    for start in range(0, len(titles), 20):
        query = wiki_get(WIKI_API, {"action": "query", "titles": "|".join(titles[start:start + 20]),
                                    "prop": "extracts|pageimages", "exintro": 1, "explaintext": 1,
                                    "exsentences": 3, "piprop": "thumbnail", "pithumbsize": 400})["query"]
        for page in query.get("pages", {}).values():
            details[page["title"]] = page
    people = {}
    for name, (title, description) in humans.items():
        page = details.get(title, {})
        people[name] = {
            "match": name,
            "name": title,
            "description": description,
            "extract": re.sub(r"\s*\([^()]*\)", "", page.get("extract", "")).strip(),
            "image": page.get("thumbnail", {}).get("source"),
            "url": "https://he.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
        }
    return people


def add_people(stories):
    try:
        people = find_people([s["headline"] for s in stories])
    except Exception as error:  # ויקיפדיה לא זמינה – הכותרות יוצגו בלי קישורים
        log(f"  ⚠ זיהוי אנשים נכשל: {error}")
        return
    for story in stories:
        # השם הארוך ביותר קודם, בלי חפיפות ("קיילי ג'נר" ולא גם "ג'נר")
        taken, matched = [], []
        for name in sorted(people, key=len, reverse=True):
            at = story["headline"].find(name)
            if at >= 0 and all(at + len(name) <= a or at >= b for a, b in taken):
                taken.append((at, at + len(name)))
                matched.append(people[name])
        story["people"] = matched
    log(f"  ✓ זוהו {len(people)} אנשים בכותרות")


def load_config():
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}


def save_config(config):
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_api_key():
    # גם מפתח שהוגדר ב-setx אחרי שהשרת עלה נקרא ישירות מהגדרות המשתמש ב-Windows
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key and sys.platform == "win32":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as env:
                key = winreg.QueryValueEx(env, "ANTHROPIC_API_KEY")[0]
        except OSError:
            pass
    return key or None


def build():
    api_key = get_api_key() if load_config().get("use_claude") else None
    result = {"generated": datetime.now(ISRAEL).isoformat(timespec="seconds"),
              "engine": "claude" if api_key else "rss", "categories": {}}
    seen_links = set()  # אותה ידיעה לא תופיע בשתי קטגוריות

    for category in SOURCES:
        log(f"קטגוריה: {CATEGORY_NAMES[category]}")
        candidates = collect(category, seen_links)
        stories = None
        if api_key and candidates:
            try:
                stories = summarize_with_claude(category, candidates[:30], api_key)
            except Exception as error:
                log(f"  ⚠ סיכום Claude נכשל, משתמש בתקצירי המקור: {error}")
        if stories is None:
            # בלי Claude: קודם ידיעות בעברית עם תקציר אמיתי מהמקור, ואנגלית רק כהשלמה
            ranked = sorted(candidates, key=lambda c: (not HEBREW.search(c["title"]), not c["summary"]))
            stories = [to_story(c, FALLBACK_ICONS[category][n]) for n, c in enumerate(ranked[:PER_CATEGORY])]
        if category == "gossip":
            add_people(stories)
        result["categories"][category] = stories
        seen_links.update(s["link"] for s in stories)
        log(f"  ✓ נבחרו {len(stories)} ידיעות")

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "news.json").write_text(payload, encoding="utf-8")
    (ROOT / "news-data.js").write_text(f"window.NEWS_DATA = {payload};\n", encoding="utf-8")
    log("העדכון נשמר.")
    return result


if __name__ == "__main__":
    if sys.stdout:  # ב-pythonw (משימה מתוזמנת) אין קונסול
        sys.stdout.reconfigure(encoding="utf-8")
    build()

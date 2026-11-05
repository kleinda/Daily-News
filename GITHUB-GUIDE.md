# העברת "התקציר היומי" למחשב העבודה דרך GitHub

המדריך בנוי משלושה חלקים:
- **חלק א'** – במחשב הבית: מעלים את הפרויקט ל־GitHub (פעם אחת).
- **חלק ב'** – במחשב העבודה: מורידים ומפעילים.
- **חלק ג'** – עדכונים שוטפים בין המחשבים.
- **חלק ד'** – האתר ברשת (GitHub Pages).

> 🔒 **מפתח ה־API לא עולה ל־GitHub.** הוא שמור רק בהגדרות Windows של כל מחשב, ולא בשום קובץ בפרויקט.
> גם קבצי הנתונים (`news-data.js`, תיקיית `data`) וקובץ ההגדרות `config.json` לא עולים –
> כל מחשב מייצר אותם לעצמו (ראו `.gitignore`).

---

## חלק א' – במחשב הבית: העלאה ל־GitHub

### 1. יצירת חשבון (אם אין)
נכנסים ל־https://github.com ← **Sign up**, ונרשמים.

### 2. יצירת מאגר (Repository) חדש
1. נכנסים ל־https://github.com/new (מחוברים לחשבון).
2. **Repository name:** `Daily-News`
3. בוחרים **Public** – כדי שבהמשך אפשר יהיה לפרסם את האתר ברשת.
   אין בפרויקט סיסמאות או מפתחות, כך שאין סיכון בחשיפת הקוד.
4. **לא** לסמן "Add a README file", ולא להוסיף ‎.gitignore או License – הם כבר קיימים בפרויקט.
5. לוחצים **Create repository**.
6. כתובת המאגר: `https://github.com/kleinda/Daily-News.git`

### 3. הסתרת כתובת המייל (חשוב במאגר ציבורי)
כל שמירת גרסה (commit) מציגה את כתובת המייל של מי ששמר. כדי שהמייל האישי לא ייחשף:
1. נכנסים ל־https://github.com/settings/emails
2. מסמנים ✅ **Keep my email addresses private**.
3. בפרויקט משתמשים בכתובת החלופית של GitHub (מופיעה בפקודות בשלב הבא):
   `212429119+kleinda@users.noreply.github.com`

### 4. העלאת הקבצים
פותחים **PowerShell** (כפתור Start ← מקלידים `PowerShell` ← Enter) ומריצים את הפקודות לפי הסדר:

```powershell
cd C:\CHAT_GPT_PROJECTS\DailyNews
git init
git config user.email "212429119+kleinda@users.noreply.github.com"
git add .
git commit -m "Daily news agent"
git branch -M main
git remote add origin https://github.com/kleinda/Daily-News.git
git push -u origin main
```

**מה כל פקודה עושה:**

| פקודה | פעולה |
|---|---|
| `cd ...` | נכנסת לתיקיית הפרויקט |
| `git init` | הופכת את התיקייה למאגר Git |
| `git config user.email ...` | קובעת שבפרויקט הזה יוצג המייל החלופי של GitHub ולא המייל האישי |
| `git add .` | מסמנת את כל הקבצים להעלאה, חוץ ממה שמוחרג ב־`.gitignore` |
| `git commit -m "..."` | שומרת "גרסה" של הקבצים, עם תיאור |
| `git branch -M main` | קוראת לענף הראשי `main` |
| `git remote add origin ...` | מקשרת את התיקייה למאגר שיצרת ב־GitHub |
| `git push -u origin main` | מעלה את הקבצים ל־GitHub |

**התחברות בפעם הראשונה:** ב־`git push` ייפתח חלון **Connect to GitHub**:
1. לוחצים **Sign in with your browser**.
2. בדפדפן לוחצים **Authorize git-ecosystem** (ואם מתבקשים – מתחברים עם סיסמה וקוד מהטלפון).
3. חוזרים ל־PowerShell; ההעלאה מסתיימת בשורה `branch 'main' set up to track 'origin/main'`.

ההתחברות נשמרת ב־Windows, ולא תצטרך לחזור עליה במחשב הזה.

### 5. בדיקה
נכנסים ל־https://github.com/kleinda/Daily-News. אמורים להופיע 9 קבצים:
`agent.py`, `server.py`, `index.html`, `start-news.bat`, `install-schedule.ps1`, `README.md`, `GITHUB-GUIDE.md`, `.gitignore`, `news-digest-2026-11-05.html`.

---

## חלק ב' – במחשב העבודה: הורדה והפעלה

### 1. התקנת Python (אם לא מותקן)
בודקים ב־PowerShell:
```powershell
python --version
```
אם מופיעה גרסה 3.9 ומעלה – מדלגים לשלב 2.

אחרת:
1. מורידים מ־https://www.python.org/downloads ← **Download Python**.
2. בהתקנה **חובה לסמן ✅ "Add python.exe to PATH"** בתחתית החלון.
3. אם אין הרשאות מנהל – ההתקנה הרגילה ("Install Now") מתקינה למשתמש בלבד ולא דורשת הרשאות.
   חלופה: מתקינים **Python 3.13** מ־Microsoft Store.
4. סוגרים ופותחים מחדש את PowerShell, ובודקים שוב `python --version`.

### 2. הורדת הפרויקט – בוחרים אחת משתי הדרכים

**דרך 1 – עם Git (מומלץ, מאפשר עדכונים קלים)**

בודקים אם Git מותקן: `git --version`. אם לא – מורידים מ־https://git-scm.com/download/win ומתקינים עם ברירות המחדל.

```powershell
mkdir C:\Projects -Force
cd C:\Projects
git clone https://github.com/kleinda/Daily-News.git DailyNews
cd DailyNews
```
המאגר ציבורי, כך שההורדה לא דורשת התחברות.

**דרך 2 – בלי Git (הורדת ZIP)**
1. נכנסים ל־https://github.com/kleinda/Daily-News
2. לוחצים על הכפתור הירוק **Code** ← **Download ZIP**.
3. קליק ימני על הקובץ שירד ← **Extract All** ← לחלץ ל־`C:\Projects\DailyNews`.
4. ⚠ בדרך זו עדכונים מחייבים להוריד ZIP חדש בכל פעם.

### 3. הפעלה
לחיצה כפולה על **`start-news.bat`** בתיקיית הפרויקט.
- בהפעלה הראשונה הסוכן אוסף ידיעות (כמה שניות), והאתר נפתח בדפדפן: http://localhost:8000
- להשאיר את החלון השחור פתוח; סגירתו עוצרת את האתר.

אם Windows מציג **"Windows protected your PC"** ← **More info** ← **Run anyway**.

### 4. רענון אוטומטי ב־08:00 (לא חובה)
כדי שהאתר יעלה ברקע בכל כניסה ל־Windows והסוכן ירוץ כל יום ב־08:00:
```powershell
cd C:\Projects\DailyNews
powershell -ExecutionPolicy Bypass -File install-schedule.ps1
```
במחשב ארגוני ייתכן שיצירת משימות מתוזמנות חסומה – במקרה כזה פשוט מפעילים את `start-news.bat` בתחילת היום.

### 5. סיכומי Claude (לא חובה)
המתג "✨ סיכומי Claude" באתר כבוי כברירת מחדל. כדי שיהיה זמין במחשב העבודה, מגדירים בו את המפתח פעם אחת:
```powershell
setx ANTHROPIC_API_KEY "sk-ant-..."
```
ואז מפעילים מחדש את `start-news.bat`.
⚠ במחשב עבודה – לוודא שמדיניות הארגון מתירה שמירת מפתחות אישיים.

---

## חלק ג' – עדכונים שוטפים

**אחרי שינוי בקוד במחשב הבית:**
```powershell
cd C:\CHAT_GPT_PROJECTS\DailyNews
git add .
git commit -m "תיאור קצר של השינוי"
git push
```

**במחשב העבודה (אם הורדת עם Git):**
```powershell
cd C:\Projects\DailyNews
git pull
```
ואז סוגרים ומפעילים מחדש את `start-news.bat`.

---

## פתרון תקלות במחשב העבודה

| תקלה | פתרון |
|---|---|
| `python` לא מזוהה | Python לא הותקן עם "Add to PATH". מתקינים מחדש ומסמנים, או פותחים PowerShell חדש |
| לשונית ריקה / "⚠" ליד מקור בחלון השחור | רשת הארגון (Firewall / Proxy) חוסמת את אתר החדשות. לבדוק בדפדפן שהאתר נפתח; אם חסום – לפנות ל־IT |
| `Address already in use` / האתר לא עולה | האתר כבר רץ ברקע – פשוט לפתוח http://localhost:8000 |
| `git push` נכשל עם `rejected` | קודם `git pull`, ואז שוב `git push` |
| המתג "סיכומי Claude" אפור | לא הוגדר מפתח במחשב הזה (חלק ב', שלב 5), או שהאתר נפתח ישירות מהקובץ ולא דרך `start-news.bat` |

---

## חלק ד' – האתר ברשת (GitHub Pages)

כתובת האתר: **https://kleinda.github.io/Daily-News/**

GitHub מריץ את הסוכן **פעמיים בשעה (בדקה 07 ובדקה 37) בין 06:00 ל־23:00** (שעון ישראל) ומפרסם את האתר – בלי שהמחשב שלך דולק.
התקציר של הבוקר הוא ההרצה של 08:07. בלילה (00:00–05:00) אין עדכונים.
(לא בשעה עגולה בדיוק – GitHub נוטה לדחות או לדלג על הרצות שמתוזמנות ל־:00.)
ההרצה מוגדרת בקובץ `.github/workflows/daily-news.yml`.

### הפעלה חד־פעמית
1. נכנסים ל־https://github.com/kleinda/Daily-News/settings/pages
2. תחת **Build and deployment** ← **Source** בוחרים **GitHub Actions**.
3. נכנסים ל־https://github.com/kleinda/Daily-News/actions/workflows/daily-news.yml
4. לוחצים **Run workflow** ← **Run workflow** (הכפתור הירוק).
5. אחרי כדקה, כשמופיע ✅ ירוק, האתר זמין בכתובת למעלה.

### עדכון ידני של האתר ברשת
באתר ברשת כפתור "רענון חדשות" טוען את העדכון האחרון שפורסם – בדרך כלל בן פחות מחצי שעה
(אין שם שרת שמריץ את הסוכן). דף פתוח בודק לבד כל 10 דקות אם הגיע עדכון.
לעדכון מיידי מהמקורות – חוזרים על שלבים 3–4 למעלה. כל `git push` מעדכן את האתר גם הוא.

### סיכומי Claude באתר ברשת (לא חובה, בתשלום)
המתג לא מוצג לגולשים, כדי שזרים לא יוכלו להפעיל חיובים.
⚠ כש־Claude מופעל, הוא רץ בכל עדכון שעתי – כ־36 פעמים ביום (3 בקשות בכל פעם). להפעלה:
1. https://github.com/kleinda/Daily-News/settings/secrets/actions ← **New repository secret**
   ← Name: `ANTHROPIC_API_KEY`, Secret: המפתח ← **Add secret** (נשמר מוצפן, לא גלוי לאף אחד).
2. https://github.com/kleinda/Daily-News/settings/variables/actions ← **New repository variable**
   ← Name: `USE_CLAUDE`, Value: `true` ← **Add variable**.
לכיבוי – משנים את `USE_CLAUDE` ל־`false`.

### שים לב
- שעון ההרצות של GitHub עלול להתעכב בכמה דקות ועד כחצי שעה בשעות עומס.
- אם לשונית מופיעה ריקה – ייתכן שאתר מקור חוסם גישה משרתי GitHub (בחו"ל). ניתן לראות זאת בלוג ההרצה תחת Actions.

# העברת "התקציר היומי" למחשב העבודה דרך GitHub

המדריך בנוי משלושה חלקים:
- **חלק א'** – במחשב הבית: מעלים את הפרויקט ל־GitHub (פעם אחת).
- **חלק ב'** – במחשב העבודה: מורידים ומפעילים.
- **חלק ג'** – עדכונים שוטפים בין המחשבים.

> 🔒 **מפתח ה־API לא עולה ל־GitHub.** הוא שמור רק בהגדרות Windows של כל מחשב, ולא בשום קובץ בפרויקט.
> גם קבצי הנתונים (`news-data.js`, תיקיית `data`) וקובץ ההגדרות `config.json` לא עולים –
> כל מחשב מייצר אותם לעצמו (ראו `.gitignore`).

---

## חלק א' – במחשב הבית: העלאה ל־GitHub

### 1. יצירת חשבון (אם אין)
נכנסים ל־https://github.com ← **Sign up**, ונרשמים.

### 2. יצירת מאגר (Repository) חדש
1. מחוברים ל־GitHub, לוחצים על **+** למעלה מימין ← **New repository**.
2. **Repository name:** `DailyNews`
3. בוחרים **Private** (מומלץ – רק אתה תראה את הקוד).
4. **לא** לסמן "Add a README file", ולא להוסיף ‎.gitignore או License – הם כבר קיימים בפרויקט.
5. לוחצים **Create repository**.
6. מעתיקים את הכתובת שמופיעה בעמוד, בצורה:
   `https://github.com/<שם-המשתמש>/DailyNews.git`

### 3. העלאת הקבצים
פותחים **PowerShell** ומריצים שורה אחרי שורה
(במקום `<שם-המשתמש>` – שם המשתמש שלך ב־GitHub):

```powershell
cd C:\CHAT_GPT_PROJECTS\DailyNews
git init
git add .
git commit -m "Daily news agent"
git branch -M main
git remote add origin https://github.com/<שם-המשתמש>/DailyNews.git
git push -u origin main
```

בפעם הראשונה ב־`git push` ייפתח חלון התחברות של GitHub ← **Sign in with your browser** ← מאשרים.
ההתחברות נשמרת, ולא תצטרך לחזור עליה.

### 4. בדיקה
מרעננים את עמוד המאגר ב־GitHub. אמורים להופיע:
`agent.py`, `server.py`, `index.html`, `start-news.bat`, `install-schedule.ps1`, `README.md`, `GITHUB-GUIDE.md`, `.gitignore`.

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
git clone https://github.com/<שם-המשתמש>/DailyNews.git
cd DailyNews
```
כיוון שהמאגר פרטי, ייפתח חלון התחברות ל־GitHub – מתחברים כמו במחשב הבית.

**דרך 2 – בלי Git (הורדת ZIP)**
1. נכנסים לעמוד המאגר ב־GitHub (מחוברים לחשבון).
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
| המתג "סיכומי Claude" אפור | לא הוגדר מפתח במחשב הזה (שלב ב'5), או שהאתר נפתח ישירות מהקובץ ולא דרך `start-news.bat` |

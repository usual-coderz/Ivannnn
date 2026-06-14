# 🚀 Quick Start Guide - ID-FREEZER Bot

## ⚡ 30 Second Setup (For Testing)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run with test credentials (UNSAFE FOR PRODUCTION)
set ALLOW_DEFAULTS=1
python main.py
```

**⚠️ WARNING**: This uses test credentials. Only for local development!

---

## 🔐 Production Setup

### Step 1: Get Telegram Credentials
1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Click "API development tools"
4. Create an app and note down:
   - **API_ID** (numeric)
   - **API_HASH** (long string)
5. Create a bot via [@BotFather](https://t.me/BotFather) and note down:
   - **BOT_TOKEN** (format: `123456:ABC-DEF...`)

### Step 2: Get MongoDB URI
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Get connection string (looks like `mongodb+srv://user:pass@cluster.mongodb.net/?appName=BotName`)

### Step 3: Create .env File
Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
API_ID=YOUR_API_ID
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
OWNER_IDS=YOUR_USER_ID
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=BotName
DB_NAME=preban_db
```

### Step 4: Run the Bot
```bash
# Option A: With .env file (recommended)
python main.py

# Option B: With environment variables
export API_ID=31495607
export API_HASH=your_api_hash
export BOT_TOKEN=your_token
export OWNER_IDS=123456789
export MONGO_URI=mongodb+srv://...
python main.py

# Option C: On Windows PowerShell
$env:API_ID = '31495607'
$env:API_HASH = 'your_api_hash'
# ... set other vars
python main.py
```

---

## 📋 Required Environment Variables

| Variable | Format | Example | Required |
|----------|--------|---------|----------|
| API_ID | Integer | 31495607 | ✅ |
| API_HASH | String | 4402573... | ✅ |
| BOT_TOKEN | String | 8070754...:AAF-7yd6... | ✅ |
| OWNER_IDS | Comma-separated IDs | 123456789,987654321 | ✅ |
| MONGO_URI | MongoDB Connection String | mongodb+srv://... | ✅ |
| DB_NAME | String | preban_db | ❌ (default: preban_db) |
| PREBAN_WORKERS | Integer | 2 | ❌ (default: 2) |
| SESSION_CONCURRENCY | Integer | 3 | ❌ (default: 3) |
| ALLOW_DEFAULTS | 0 or 1 | 1 | ❌ (default: 0 - use test creds if 1) |

---

## 🐛 Troubleshooting

### Error: "Configuration invalid"
- Make sure all required environment variables are set
- OR set `ALLOW_DEFAULTS=1` for testing

### Error: "MongoDB URI is not configured"
- Check your `MONGO_URI` environment variable
- Bot will fall back to in-memory database (data lost on restart)

### Error: "Connection refused"
- Make sure MongoDB is running
- Check MongoDB URI is correct
- Firewall may be blocking MongoDB

### Bot not responding to commands
- Check if bot is actually running (`LOGGER: Bot is running.` message)
- Make sure you have the correct BOT_TOKEN
- Check bot permissions in Telegram

---

## 🧪 Test Commands

Once bot is running:

```
/start      - Show home screen
/help       - Show help
/ping       - Health check
/health     - System health (owner only)
```

---

## 📚 Production Checklist

- [ ] Set unique `API_ID` and `API_HASH` (not test values)
- [ ] Create bot via @BotFather
- [ ] Setup MongoDB Atlas cluster
- [ ] Create `.env` file with real credentials
- [ ] Set `ALLOW_DEFAULTS=0` (default)
- [ ] Remove `.env` from git (add to `.gitignore`)
- [ ] Test bot commands before deployment
- [ ] Deploy on Heroku / VPS / Cloud Run

---

## 🚀 Deploy to Heroku

```bash
heroku login
heroku create your-app-name
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set API_ID=31495607
heroku config:set API_HASH=your_hash
heroku config:set BOT_TOKEN=your_token
# ... set all required vars

git push heroku main
heroku logs --tail
```

---

## 💡 Tips

- Use `python -m tools.selfcheck` to validate imports
- Use in-memory DB for testing only (data persists only in current session)
- For production, always use MongoDB Atlas
- Keep `.env` file secure - never commit to git
- Rotate credentials regularly

---

**Need help?** Check [README.md](README.md) for more details.

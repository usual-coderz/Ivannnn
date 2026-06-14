# 📝 Session Management Guide

## What is a Session String?

A **session string** is a long encrypted text that represents a logged-in Telegram account. It contains:
- Account authentication data
- API keys
- User credentials
- Access tokens

**Format example:**
```
AgE87yXG9A3bX7yM2kL9pQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKl...
(very long base64-like string, 200+ characters)
```

---

## ⚠️ Session String Errors & Fixes

### Error: `struct.error: unpack requires a buffer of 271 bytes`

**Cause:** Session string is corrupted, incomplete, or invalid.

**Fixes:**

#### ✅ Fix 1: Paste Complete Session String
Make sure you're copying the **entire** session string:
```
❌ WRONG: AgE87yXG9A3b... (incomplete)
✅ RIGHT: AgE87yXG9A3bX7yM2kL9pQrStUvWxYzAbCdEfGhIjKl... (complete)
```

#### ✅ Fix 2: Get Session String Correctly

**Using Pyrogram Script:**
```python
from pyrogram import Client

async def get_session():
    async with Client("my_account", api_id=123456, api_hash="...") as app:
        print(app.export_session_string())

# Run it:
# python get_session.py
```

**Using Telethon:**
```python
from telethon.client import TelegramClient

client = TelegramClient('session_name', api_id, api_hash)
client.start()
session_string = client.session.export()
print(session_string)
```

#### ✅ Fix 3: Check Session String Length

Session strings should be:
- **Minimum:** 200 characters
- **Typical:** 500-1000 characters
- **Maximum:** 2000+ characters

```
❌ TOO SHORT: AgE87yXG9A (only 10 chars)
✅ GOOD: AgE87yXG9A3bX7yM2kL9pQrStUvWxYzAbCdEfGhIj... (500+ chars)
```

---

## 🚀 How to Add Sessions

### Method 1: Paste in Session Group (Recommended)

```
1. Go to Session Manager Group (already set via /set_session)
2. Paste the session string directly
3. Bot will validate automatically
4. ✅ Session added successfully!
```

### Method 2: Use /addsession Command (Backup)

```
1. DM the bot owner
2. Type: /addsession <session_string>
3. Bot validates and stores
4. ✅ Session added!
```

---

## ✅ How to Verify Sessions

### Check Active Sessions:
```
Owner: /manage
Bot shows: 
- List of active accounts
- Phone numbers / usernames
- Option to remove
```

### Test Single Session:
```
Bot logs: Session added for John Doe (phone: +1234567890)
```

---

## 🛑 Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `struct.error: unpack requires 271 bytes` | Incomplete session string | Copy **entire** string, not just part of it |
| `❌ Session invalid, corrupted, or expired` | Session expired (30+ days inactive) | Get a fresh session string |
| `⚠️ Session validated but failed to save` | Database offline | Wait and retry, or check MongoDB |
| No response from bot | Session group not set | Run `/set_session` in the group first |

---

## 📋 Session Lifecycle

```
Session String → Bot Validates → Database Stores → Available for Pre-ban

        ↓
   Inactive 30+ days
        ↓
   Expires automatically
        ↓
   Must re-add new session
```

---

## 🔒 Security Notes

⚠️ **IMPORTANT:**
- Never share session strings publicly
- Session strings = full account access
- Don't post them in public chats
- Only paste in **Session Manager Group**
- Keep them private and secure

---

## 💡 Tips

1. **Keep Multiple Sessions:** Add 3-5 backup sessions in case one expires
2. **Refresh Monthly:** Re-add sessions before 30-day expiry
3. **Test Before Adding:** Validate session outside group first
4. **Check Logs:** Use `python -m tools.selfcheck` to validate
5. **Use /manage:** Check active sessions regularly

---

## 📞 Troubleshooting Steps

```
1. Session string too short?
   → Copy entire string (check for line breaks)
   
2. Still getting struct.error?
   → Try /addsession in DM instead
   
3. Session expired?
   → Get fresh session, re-add it
   
4. Database error?
   → Check MongoDB connection
   → Or wait for database to come online
```

---

## 🎯 Summary

| Task | Command | Location |
|------|---------|----------|
| Set session group | `/set_session` | **In group** |
| Add session | Paste string | **Session group** |
| Add session (backup) | `/addsession <string>` | **DM with owner** |
| View sessions | `/manage` | **DM with owner** |
| Remove session | Click button | **From /manage** |

---

**Need help?** Check logs with `/health` or `/manage` commands!

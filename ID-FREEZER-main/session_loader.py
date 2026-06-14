from __future__ import annotations

import logging
import uuid

from pyrogram import Client, enums, filters, types
from pyrogram.errors import RPCError
from pyrogram.handlers import MessageHandler

from config import Config
from db import add_session

LOGGER = logging.getLogger(__name__)


def _normalize_chat_id(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


async def validate_session(session_string: str) -> bool:
    """Validate a Pyrogram session string by calling get_me()."""
    try:
        async with Client(
            name=f"session_check_{uuid.uuid4().hex}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=session_string,
        ) as app:
            await app.get_me()
        return True
    except RPCError:
        return False


async def save_session(session_string: str) -> bool | None:
    """Validate and upsert a session as active."""
    me = None
    
    # Validate session string format
    if not session_string or len(session_string) < 10:
        LOGGER.warning("Session string too short or empty: %s chars", len(session_string))
        return False
    
    try:
        async with Client(
            name=f"session_save_{uuid.uuid4().hex}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=session_string,
        ) as app:
            me = await app.get_me()
        try:
            await add_session(session_string, me.first_name, me.phone_number or str(me.id))
        except Exception:
            LOGGER.exception("Failed to store session in DB. The database may be unavailable.")
            return None
        LOGGER.info("Session added for %s.", me.first_name)
        return True
    except RPCError as rpc_err:
        identifier = None
        if me:
            identifier = me.phone_number or str(me.id)
        LOGGER.error("RPC error while saving session for %s: %s", identifier or "unknown user", rpc_err)
        return False
    except ValueError as ve:
        LOGGER.warning("Invalid session string format: %s", str(ve)[:100])
        return False
    except Exception as ex:
        # Catch struct.error and other format errors
        error_name = type(ex).__name__
        if error_name in ("struct.error", "IndexError", "KeyError"):
            LOGGER.warning("Session string format error (%s): session appears corrupted or invalid", error_name)
        else:
            LOGGER.warning("Failed to save session: %s", error_name)
        return False


async def test_all_sessions() -> None:
    """Validate existing sessions and deactivate invalid ones."""
    from db import deactivate_session, get_active_sessions

    try:
        sessions = await get_active_sessions()
    except Exception:
        LOGGER.exception("Failed to load sessions for validation.")
        return
    if not sessions:
        LOGGER.warning("⚠️ No sessions loaded yet.")
        return
    for row in sessions:
        session_string = row.get("string")
        phone = row.get("phone") or row.get("name") or "unknown"
        if not session_string:
            LOGGER.warning("Session missing string for %s.", phone)
            continue
        try:
            ok = await validate_session(session_string)
        except Exception:
            LOGGER.exception("Session validation failed for %s.", phone)
            continue
        if not ok:
            LOGGER.warning("Deactivating invalid session for %s.", phone)
            try:
                await deactivate_session(phone)
            except Exception:
                LOGGER.exception("Failed to deactivate invalid session for %s.", phone)


async def _auto_session_val(client: Client, message: types.Message) -> None:
    """Auto-validate session strings posted in the configured session group."""
    try:
        if not message.from_user or not message.text:
            return
        from db import get_active_sessions, get_settings

        conf = await get_settings()
        session_group = _normalize_chat_id(conf.get("session_group"))
        if not session_group or message.chat.id != session_group:
            return
        
        session_text = message.text.strip()
        
        # Skip if message is a command
        if session_text.startswith("/"):
            return
        
        # Skip if message is too short
        if len(session_text) < 10:
            await message.reply("❌ Session string too short. Make sure you're posting a complete session string.")
            return
            
        result = await save_session(session_text)
        if result is True:
            active_sessions = await get_active_sessions()
            await message.reply(
                "✅ Session added successfully.\n"
                f"📊 Active Sessions: {len(active_sessions)}",
            )
        elif result is None:
            await message.reply(
                "⚠️ Session validated but failed to save. The database may be down.\n"
                "Try again later.",
            )
        else:
            await message.reply(
                "❌ Session invalid, corrupted, or expired.\n\n"
                "📝 Make sure you're pasting a complete session string.\n"
                "💡 Use /addsession in DM if having issues."
            )
    except RPCError as rpc_err:
        await message.reply(f"❌ Telegram error: {str(rpc_err)[:50]}")
    except Exception as ex:
        LOGGER.exception("Auto session validation failed.")
        await message.reply("❌ Error validating session. Try again later.")


async def _auto_session_doc_val(client: Client, message: types.Message) -> None:
    """Auto-validate session strings from a document file."""
    try:
        from db import get_active_sessions, get_settings
        
        # Check permissions: if in group, must be the session group. If private, must be owner.
        is_private = message.chat.type == enums.ChatType.PRIVATE
        if is_private:
            if not message.from_user or message.from_user.id not in Config.OWNERS:
                return
        else:
            conf = await get_settings()
            session_group = _normalize_chat_id(conf.get("session_group"))
            if not session_group or message.chat.id != session_group:
                return
                
        # Must be a document and not too large
        if not message.document or message.document.file_size > 5 * 1024 * 1024:
            return  # Skip files larger than 5MB
            
        status_msg = await message.reply("⏳ Downloading and checking session(s)...")
        
        file_path = await message.download()
        if not file_path:
            await status_msg.edit_text("❌ Failed to download file.")
            return
            
        file_name = message.document.file_name or ""
        import os
        
        # Handle SQLite .session files directly
        if file_name.endswith(".session"):
            try:
                import sqlite3
                import struct
                import base64
                
                conn = sqlite3.connect(file_path)
                c = conn.cursor()
                c.execute("PRAGMA table_info(sessions)")
                columns = [row[1] for row in c.fetchall()]
                
                string_session = None
                
                # Check for Pyrogram format
                if "api_id" in columns:
                    c.execute("SELECT dc_id, api_id, test_mode, auth_key, user_id, is_bot FROM sessions")
                    row = c.fetchone()
                    if row:
                        dc_id, api_id, test_mode, auth_key, user_id, is_bot = row
                        packed = struct.pack(">BI?256sQ?", dc_id, api_id, test_mode, auth_key, user_id, is_bot)
                        string_session = base64.urlsafe_b64encode(packed).decode().rstrip("=")
                
                # Check for Telethon format
                elif "server_address" in columns:
                    c.execute("SELECT dc_id, auth_key FROM sessions")
                    row = c.fetchone()
                    if row:
                        dc_id, auth_key = row
                        api_id = Config.API_ID
                        packed = struct.pack(">BI?256sQ?", dc_id, api_id, False, auth_key, 9999, False)
                        string_session = base64.urlsafe_b64encode(packed).decode().rstrip("=")
                
                conn.close()
                
                if not string_session:
                    await status_msg.edit_text(f"❌ Unrecognized or empty .session format in `{file_name}`.")
                    if os.path.exists(file_path): os.remove(file_path)
                    return
                
                res = await save_session(string_session)
                active_sessions = await get_active_sessions()
                if res is True:
                    await status_msg.edit_text(
                        f"✅ Universal Session `{file_name}` imported successfully!\n"
                        f"📊 Total Active Sessions: {len(active_sessions)}"
                    )
                else:
                    await status_msg.edit_text(f"❌ Session `{file_name}` is invalid, banned, or could not be saved.")
            except Exception as e:
                LOGGER.exception("Failed to process .session file")
                await status_msg.edit_text(f"❌ Failed to read .session file.\nError: {e}")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
            return

        # Otherwise, assume it's a .txt file with bulk string sessions
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
            
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if not lines:
            await status_msg.edit_text("❌ No sessions found in the file.")
            return
            
        await status_msg.edit_text(f"⏳ Found {len(lines)} sessions. Validating...")
        
        success = 0
        failed = 0
        
        for session_str in lines:
            if len(session_str) < 10:
                failed += 1
                continue
            res = await save_session(session_str)
            if res is True:
                success += 1
            else:
                failed += 1
                
        active_sessions = await get_active_sessions()
        await status_msg.edit_text(
            f"✅ Bulk Session Import Complete\n\n"
            f"🟢 Saved: {success}\n"
            f"🔴 Failed: {failed}\n"
            f"📊 Total Active Sessions: {len(active_sessions)}"
        )
        
    except Exception:
        LOGGER.exception("Bulk session import failed.")
        try:
            await message.reply("❌ Error processing the session file.")
        except Exception:
            pass


def register_session_ingest(app: Client) -> None:
    LOGGER.info("Registering session ingestion handlers.")
    app.add_handler(MessageHandler(_auto_session_val, filters.text & filters.group), group=4)
    app.add_handler(MessageHandler(_auto_session_doc_val, filters.document & (filters.group | filters.private)), group=4)


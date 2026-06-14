import os
import asyncio
import glob
from pyrogram import Client
from config import Config

# Ensure you have your API_ID and API_HASH set in your .env or config
API_ID = Config.API_ID
API_HASH = Config.API_HASH

async def main():
    print("🔍 Scanning for .session files in the current folder...")
    session_files = glob.glob("*.session")
    
    # Ignore the bot's own session
    if "PreBanBot.session" in session_files:
        session_files.remove("PreBanBot.session")

    if not session_files:
        print("❌ No .session files found in this directory.")
        return

    print(f"📦 Found {len(session_files)} session files. Starting conversion to String Sessions...")
    
    with open("bulk_sessions_ready.txt", "w", encoding="utf-8") as f:
        success = 0
        for session_file in session_files:
            # Pyrogram expects the session name without the .session extension
            session_name = session_file.replace(".session", "")
            
            try:
                # We start the client using the .session file
                app = Client(session_name, api_id=API_ID, api_hash=API_HASH)
                await app.start()
                
                # Export it as a String Session
                string_session = await app.export_session_string()
                f.write(string_session + "\n")
                
                await app.stop()
                success += 1
                print(f"✅ Converted: {session_file}")
            except Exception as e:
                print(f"❌ Failed to convert {session_file}: {e}")

    print("-" * 40)
    print(f"🎉 Conversion Complete! {success}/{len(session_files)} converted successfully.")
    print("👉 Send the 'bulk_sessions_ready.txt' file to your bot to add them all at once!")

if __name__ == "__main__":
    asyncio.run(main())

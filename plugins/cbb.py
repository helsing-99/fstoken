import asyncio
import logging
from pyrogram import Client
from bot import Bot
from config import *
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import *
from database.verify_db import *

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close')]
            ])
        )

    elif data == "start":
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'),
                 InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')]
            ])
        )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data == "shortener_settings":
        try:
            await query.answer("💫 Fetching Shortener details...")

            shortener_url = await db.get_shortener_url() or "Not set"
            shortener_api = await db.get_shortener_api() or "Not set"
            verified_time = await db.get_verified_time()
            tut_video = await db.get_tut_video()

            status = "Active ✅" if shortener_url != "Not set" and shortener_api != "Not set" else "Inactive ❌"
            verified_time_display = f"{verified_time} seconds" if verified_time else "Not set"
            tut_video_display = f"[Tutorial Video]({tut_video})" if tut_video else "Not set"

            response_text = (
                f"🔗 Shortener Details\n"
                f"• Site: {shortener_url}\n"
                f"• API Token: {shortener_api}\n"
                f"• Status: {status}\n\n"
                f"• Verified Time: {verified_time_display}\n"
                f"• Tutorial Video: {tut_video_display}"
            )

            await query.message.edit_text(
                text=response_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('Back', callback_data='set_shortener')]
                ]),
                disable_web_page_preview=True
            )

        except Exception as e:
            logging.error(f"Error fetching shortener settings: {e}")
            await query.message.reply_text(
                "⚠️ Error occurred while fetching shortener settings. Try again later.",
                reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Back', callback_data='set_shortener')],
                [InlineKeyboardButton('Close ✖️', callback_data='close')]
            ])
        )


    elif data == "chng_shortener":
        shortener_details = await db.get_shortener()
        if shortener_details:
            await db.set_shortener("", "")
            await query.answer("Shortener Disabled ❌", show_alert=True)
        else:
            await query.answer("Shortener Enabled ✅. Please provide the Shortener URL and API Key.", show_alert=True)
            await query.message.reply("Send the Shortener URL and API Key in the format:\n`<shortener_url> <api_key>`")

    elif data == "set_shortener":
        try:
            shortener_url = await db.get_shortener_url()
            shortener_api = await db.get_shortener_api()

            shortener_status = "Enabled ✅" if shortener_url and shortener_api else "Disabled ❌"
            mode_button = InlineKeyboardButton(
                'Disable Shortener ❌' if shortener_status == "Enabled ✅" else 'Enable Shortener ✅',
                callback_data='disable_shortener' if shortener_status == "Enabled ✅" else 'set_shortener_details'
            )

            await query.message.edit_text(
                text=f"Shortener Status: {shortener_status}",
                reply_markup=InlineKeyboardMarkup([
                    [mode_button],
                    [InlineKeyboardButton('Settings ⚙️', callback_data='shortener_settings')],
                    [InlineKeyboardButton('Set Verified Time ⏱', callback_data='set_verify_time'),
                     InlineKeyboardButton('Set Tutorial Video 🎥', callback_data='set_tut_video')],
                    [InlineKeyboardButton('Close ✖️', callback_data='close')]
                ])
            )
        except Exception as e:
            logging.error(f"Error setting shortener: {e}")
            await query.message.reply_text(f"⚠️ Error occurred: {e}")

    elif data == 'set_shortener_details':
        try:
            # Step 1: Prompt for the shortener URL with a timeout of 1 minute
            await query.answer("Please send the shortener URL within 1 minute...")
            set_msg_url = await query.message.reply(
                    "⏳ Please provide the Shortener site URL (e.g., https://example.com) within 1 minute.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data='set_shortener')]])
                )
            site_msg = await client.ask(
                chat_id=query.from_user.id,
                text="⏳ Enter Shortener site URL:",
                timeout=60
            )

            shortener_url = site_msg.text.strip()


            # Confirm the shortener site URL
            await site_msg.reply(f"Shortener site URL set to: {shortener_url}\nNow please send the API key.")

            # Step 3: Prompt for API key
            set_msg_api = await query.message.reply(
                    "⏳ Please provide the API key for the shortener within 1 minute.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data='set_shortener')]])
                )

            api_msg = await client.ask(
                chat_id=query.from_user.id,
                text="⏳ Enter API key for the shortener:",
                timeout=60
            )

            api_key = api_msg.text.strip()

            # Step 4: Save the shortener details in the database
            await db.set_shortener_url(shortener_url)
            await db.set_shortener_api(api_key)

            # Confirmation message
            await api_msg.reply(
                    "✅ Shortener details have been successfully set!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('◈ Disable Shortener ❌', callback_data='disable_shortener')],
                    [InlineKeyboardButton('Back', callback_data='set_shortener')]
                ])
            )
        except asyncio.TimeoutError:
            await query.message.reply(
                    "⚠️ You did not provide the details in time. Please try again.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data='set_shortener')]])
                )
        except Exception as e:
            logging.error(f"Error setting shortener details: {e}")  # This now works correctly
            await query.message.reply(
                f"⚠️ Error occurred: {e}",
reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Back', callback_data='set_shortener')]])
    )


    elif data == "set_verify_time":
        try:
            current_verify_time = await db.get_verified_time() or "Not set"

            set_msg = await client.ask(
                chat_id=query.from_user.id,
                text=f"⏱ Current Timer: {current_verify_time}\n\nSend a valid time in seconds (e.g., 300, 600).",
                timeout=60
            )

            verify_time = set_msg.text.strip()
            if verify_time.isdigit():
                await db.set_verified_time(int(verify_time))
                await set_msg.reply(f"✅ Timer updated to {verify_time} seconds.")
            else:
                await set_msg.reply("⚠️ Invalid input. Please enter a valid number in seconds.")

        except asyncio.TimeoutError:
            await query.message.reply_text("⚠️ Timeout! You didn't respond in time.")

    elif data == "set_tut_video":
        try:
            current_video_url = await db.get_tut_video() or "Not set"

            set_msg = await client.ask(
                chat_id=query.from_user.id,
                text=f"📹 Current Tutorial Video: {current_video_url}\n\nSend a new valid video URL.",
                timeout=60
            )

            video_url = set_msg.text.strip()
            if video_url.startswith("http"):
                await db.set_tut_video(video_url)
                await set_msg.reply(f"✅ Tutorial Video URL updated: {video_url}")
            else:
                await set_msg.reply("⚠️ Invalid URL. Please send a valid video link.")

        except asyncio.TimeoutError:
            await query.message.reply_text("⚠️ Timeout! You didn't respond in time.")

    elif data == "enable_shortener":
        try:
            shortener_url = await db.get_shortener_url()
            shortener_api = await db.get_shortener_api()

            if shortener_url and shortener_api:
                await db.set_shortener_url(shortener_url)
                await db.set_shortener_api(shortener_api)

                await query.message.edit_text(
                    "✅ Shortener has been enabled!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('Disable Shortener ❌', callback_data='disable_shortener')],
                        [InlineKeyboardButton('Close ✖️', callback_data='close')]
                    ])
                )
            else:
                await query.message.edit_text(
                    "⚠️ No shortener details found. Please set the details first.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('Set Shortener Details', callback_data='set_shortener_details')],
                        [InlineKeyboardButton('Close ✖️', callback_data='close')]
                    ])
                )
        except Exception as e:
            logging.error(f"Error enabling shortener: {e}")
            await query.message.reply_text("⚠️ An error occurred while enabling the shortener.")

    elif data == "disable_shortener":
        await query.answer()

    # Deactivate the shortener
        success = await db.deactivate_shortener()
        if success:
            await query.edit_message_caption(
                caption="Shortener has been disabled ❌",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('Enable Shortener ✅', callback_data='enable_shortener')],
                    [InlineKeyboardButton('Close ✖️', callback_data='close')]
                ])
            )
        else:
            await query.message.reply("Failed to disable the shortener. Please try again.")
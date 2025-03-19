
import time
import pymongo, os
import motor
from config import DB_URI, DB_NAME
from bot import Bot
import logging
from datetime import datetime, timedelta

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

logging.basicConfig(level=logging.INFO)

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }



class Rohit:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.dbclient[DB_NAME]
        self.shortener_data = self.database['shortener']
        self.settings_data = self.database['settings']

    # Shortener Token
    async def set_shortener_url(self, url):
        try:
        # Check if an active shortener exists
            existing = await self.shortener_data.find_one({"active": True})
            if existing:
            # Update the URL of the existing active shortener
                await self.shortener_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"shortener_url": url, "updated_at": datetime.utcnow()}}
                )
            else:
            # Insert a new active shortener with the given URL
                await self.shortener_data.insert_one({
                    "shortener_url": url,
                    "api_key": None,
                    "active": True,
                    "created_at": datetime.utcnow()
                })
            return True
        except Exception as e:
            logging.error(f"Error setting shortener URL: {e}")
            return False

    async def set_shortener_api(self, api):
        try:
        # Check if an active shortener exists
            existing = await self.shortener_data.find_one({"active": True})
            if existing:
            # Update the API key of the existing active shortener
                await self.shortener_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"api_key": api, "updated_at": datetime.utcnow()}}
                )
            else:
            # Insert a new active shortener with the given API key
                await self.shortener_data.insert_one({
                    "shortener_url": None,
                    "api_key": api,
                    "active": True,
                    "created_at": datetime.utcnow()
                })
            return True
        except Exception as e:
            logging.error(f"Error setting shortener API key: {e}")
            return False

    async def get_shortener_url(self):
        try:
        # Retrieve the shortener URL of the active shortener
            shortener = await self.shortener_data.find_one({"active": True}, {"_id": 0, "shortener_url": 1})
            return shortener.get("shortener_url") if shortener else None
        except Exception as e:
            logging.error(f"Error fetching shortener URL: {e}")
            return None

    async def get_shortener_api(self):
        try:
        # Retrieve the API key of the active shortener
            shortener = await self.shortener_data.find_one({"active": True}, {"_id": 0, "api_key": 1})
            return shortener.get("api_key") if shortener else None
        except Exception as e:
            logging.error(f"Error fetching shortener API key: {e}")
            return None


    async def deactivate_shortener(self):
        try:
            # Deactivate all active shorteners
            await self.shortener_data.update_many({"active": True}, {"$set": {"active": False}})
            return True
        except Exception as e:
            logging.error(f"Error deactivating shorteners: {e}")
            return False

    async def set_verified_time(self, verified_time: int):
        try:
            # Update the verified time in the database
            result = await self.settings_data.update_one(
                {"_id": "verified_time"},  # Assuming there's an entry with this ID for settings
                {"$set": {"verified_time": verified_time}},
                upsert=True  # Create the document if it doesn't exist
            )
            return result.modified_count > 0  # Return True if the update was successful
        except Exception as e:
            logging.error(f"Error updating verified time: {e}")
            return False

    async def get_verified_time(self):
        try:
            # Retrieve the verified time from the database
            settings = await self.settings_data.find_one({"_id": "verified_time"})
            return settings.get("verified_time", None) if settings else None
        except Exception as e:
            logging.error(f"Error fetching verified time: {e}")
            return None

    async def set_tut_video(self, video_url: str):
        try:
            # Update the tutorial video URL in the database
            result = await self.settings_data.update_one(
                {"_id": "tutorial_video"},  # Assuming there's an entry with this ID for settings
                {"$set": {"tutorial_video_url": video_url}},
                upsert=True  # Create the document if it doesn't exist
            )
            return result.modified_count > 0  # Return True if the update was successful
        except Exception as e:
            logging.error(f"Error updating tutorial video URL: {e}")
            return False

    async def get_tut_video(self):
        try:
            # Retrieve the tutorial video URL from the database
            settings = await self.settings_data.find_one({"_id": "tutorial_video"})
            return settings.get("tutorial_video_url", None) if settings else None
        except Exception as e:
            logging.error(f"Error fetching tutorial video URL: {e}")
            return None

db = Rohit(DB_URI, DB_NAME)
      
          

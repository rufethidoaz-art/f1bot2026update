"""
F1 Telegram Bot - Live Timing Version for Vercel
Enhanced version with live timing functionality optimized for Vercel
"""

import os
import sys
import asyncio
import requests
import json
import logging
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Configure enhanced logging for Vercel
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Azerbaijani translations (simplified)
TRANSLATIONS = {
    "welcome_title": "🏎️ F1 Canlı Botuna Xoş Gəlmisiniz!",
    "welcome_text": """🏁 Sizin Formula 1 üçün ən yaxşı yoldaşınız - real vaxt yarış məlumatları, sıralamalar və canlı vaxt məlumatları.

*Edə biləcəyiniz:*
🏆 Cari çempionat sıralamalarını yoxlayın
🏎️ Son nəticələri alın
📅 Gələn yarış cədvəllərini və hava proqnozunu (Bakı vaxtı ilə) görün
🔴 Canlı vaxtı izləyin
🎥 Yayım linklərini görün""",
    "menu_title": "🏎️ F1 Bot Menyusu",
    "menu_text": "Aşağıdakı variantlardan birini seçin:",
    "driver_standings": "🏆 Sürücü Sıralamaları",
    "constructor_standings": "🏁 Konstruktor Sıralamaları",
    "last_session": "🏎️ Son Sessiya Nəticələri",
    "schedule_weather": "📅 Cədvəl & Hava",
    "live_timing": "🔴 Canlı Vaxt",
    "streams": "▶️ Yayımlar",
    "help_commands_btn": "ℹ️ Kömək & Əmrlər",
    "season_driver_standings": " Pilotların Çempionat Sıralaması",
    "season_constructor_standings": "*Konstruktorların Çempionat Sıralaması- {}*",
    "points": "xal",
    "qualifying": "Təsnifat",
    "sprint": "Sprint",
    "race": "Yarış",
    "winner": " - Qalib",
    "fastest_lap": "Ən Sürətli Dövrə: {} ({})",
    "next_race": "🏎️ *Gələn Yarış*",
    "fp1": "FP1",
    "fp2": "FP2",
    "fp3": "FP3",
    "sprint_qualifying": "Sprint Təsnifatı",
    "qualifying": "Təsnifat",
    "race": "Yarış",
    "all_times_baku": "_Bütün vaxtlar Bakı vaxtı ilə_",
    "season_completed": "🏁 Mövsüm tamamlandı! Bu il üçün daha yarış yoxdur.",
    "weather_forecast": "🌤️ Hava Proqnozu üçün {}",
    "friday": "Cümə",
    "saturday": "Şənbə",
    "sunday": "Bazar",
    "race_day": "Bazar (Yarış)",
    "weather_unavailable": "🌦️ Bu yer üçün hava məlumatları mövcud deyil.",
    "no_live_data": "❌ Canlı vaxt məlumatları mövcud deyil\n\nSon nəticələr üçün /lastrace istifadə edin",
    "live_not_available": "❌ Canlı vaxt mövcud deyil\n\nSon nəticələr üçün /lastrace istifadə edin",
    "available_streams": "🎦 *Mövcud Yayımlar*",
    "tap_to_open": "Açmaq üçün toxunun:",
    "no_streams": "❌ Yayım yoxdur.\n\nƏlavə: /addstream Ad | URL",
    "stream_added": "✅ Əlavə edildi: {}\n\n/streams istifadə edin",
    "stream_removed": "✅ Yayım '{}' uğurla silindi!",
    "stream_error": "❌ Səhv",
    "stream_help_title": "🎦 Yayım Köməyi",
    "stream_help_best": "*Ən Yaxşı: .m3u8 URL-lər*\n• Birbaşa video yayımı\n• Reklam yoxdur\n• VLC Player-də açın",
    "stream_help_how": "*Necə istifadə etmək:*\n1. Əlavə: /addstream Ad | URL\n2. Görün: /streams\n3. Açmaq üçün toxunun",
    "stream_help_vlc": "💡 .m3u8 faylları üçün VLC istifadə edin!",
    "playstream_usage": "İstifadə:\n/playstream <nömrə> - Yayım linkini alın\n/playstream <URL> - Birbaş link",
    "direct_stream": "Birbaşa Yayım",
    "copy_open_vlc": "💡 Kopyalayın və VLC Player-də açın",
    "loading": "⏳ Yüklənir...",
    "name_url_required": "❌ Ad və URL tələb olunur",
    "use_format": "❌ /addstream Ad | URL istifadə edin",
    "invalid_number": "❌ Yanlış nömrə. Yayım nömrələrini görmək üçün /streams istifadə edin.",
    "no_personal_streams": "❌ Şəxsi yayımlarınız yoxdur.",
    "invalid_number_range": "❌ Yanlış nömrə. Sizdə {} yayım var.",
    "error_saving": "❌ Saxlanılarkən xəta",
    "error_removing": "❌ Yayım silinərkən xəta. Yenidən cəhd edin.",
    "no_streams_found": "❌ Yayım tapılmadı",
    "invalid_input": "❌ Yanlış daxiletmə",
    "no_url": "❌ URL yoxdur",
    "usage_addstream": "İstifadə: /addstream Ad | URL\n\nNümunə:\n/addstream F1 Live | https://example.com/stream.m3u8",
    "usage_removestream": "İstifadə: /removestream <nömrə>\n\n/streams ilə yayım nömrələrini görün.",
    "invalid_removestream": "❌ Yanlış nömrə. /streams ilə yayım nömrələrini görün.",
    "invalid_playstream": "❌ Yanlış daxiletmə",
    "api_unavailable": "❌ Xidmət mənbəyi baxımdadır. Bir neçə dəqiqə sonra yenidən cəhd edin.",
    "no_standings": "❌ Bu mövsüm üçün sıralama məlumatları tapılmadı.",
    "no_driver_standings": "❌ Sürücü sıralamaları tapılmadı.",
    "invalid_data": "❌ Mənbədən yanlış məlumat format.",
    "no_constructor_standings": "❌ Konstruktor sıralamaları tapılmadı.",
    "no_sessions": "❌ Sessiya tapılmadı. API offline ola bilər.",
    "no_recent_sessions": "❌ Son tamamlanmış sessiyalar tapılmadı.",
    "no_results": "❌ Bu sessiya üçün nəticələr mövcud deyil.",
    "no_position_data": "❌ Bu sessiya üçün mövqe məlumatları mövcud deyil.",
    "no_final_positions": "❌ Bu sessiya üçün final mövqelər mövcud deyil.",
    "error_fetching_session": "❌ Sessiya nəticələrini almaqda xəta: {}",
    "error_fetching_race": "❌ Gələn yarış alınarkən xəta: {}",
    "weather_unavailable": "❌ Hava məlumatları mövcud deyil.",
    "error_fetching_weather": "❌ Hava məlumatları alınarkən xəta: {}",
    "service_unavailable": "❌ Xidmət müvəqqəti mövcud deyil. Daha sonra yenidən cəhd edin.",
    "error_occurred": "❌ Xəta baş verdi: {}",
    "unknown_command": "❌ Naməlum əmr",
    "live_session_check": "🔴 Canlı sessiya yoxlanılır...",
    "live_session_active": "🔴 Canlı sessiya aktivdir! Mövqelər yenilənir...",
    "live_session_inactive": "🔴 Hal-hazırda aktiv F1 sessiyası yoxdur",
    "live_session_error": "❌ Canlı sessiya yoxlanarkən xəta: {}",
}

# Country to flag emoji mapping
COUNTRY_FLAGS = {
    "Mexico": "🇲🇽",
    "Mexico City": "🇲🇽",
    "USA": "🇺🇸",
    "United States": "🇺🇸",
    "Austin": "🇺🇸",
    "Miami": "🇺🇸",
    "Las Vegas": "🇺🇸",
    "Brazil": "🇧🇷",
    "UK": "🇬🇧",
    "United Kingdom": "🇬🇧",
    "Monaco": "🇲🇨",
    "Italy": "🇮🇹",
    "Imola": "🇮🇹",
    "Monza": "🇮🇹",
    "Spain": "🇪🇸",
    "Australia": "🇦🇺",
    "Netherlands": "🇳🇱",
    "France": "🇫🇷",
    "Germany": "🇩🇪",
    "Austria": "🇦🇹",
    "Canada": "🇨🇦",
    "Japan": "🇯🇵",
    "Singapore": "🇸🇬",
    "Bahrain": "🇧🇭",
    "Saudi Arabia": "🇸🇦",
    "Qatar": "🇶🇦",
    "UAE": "🇦🇪",
    "United Arab Emirates": "🇦🇪",
    "Abu Dhabi": "🇦🇪",
    "China": "🇨🇳",
    "Belgium": "🇧🇪",
    "Hungary": "🇭🇺",
    "Portugal": "🇵🇹",
    "Russia": "🇷🇺",
    "Turkey": "🇹🇷",
    "Azerbaijan": "🇦🇿",
    "Baku": "🇦🇿",
    "British": "🇬🇧",
    "Australian": "🇦🇺",
    "Dutch": "🇳🇱",
    "Monegasque": "🇲🇨",
    "Spanish": "🇪🇸",
    "Mexican": "🇲🇽",
    "German": "🇩🇪",
    "French": "🇫🇷",
    "Japanese": "🇯🇵",
    "Canadian": "🇨🇦",
    "Thai": "🇹🇭",
    "Finnish": "🇫🇮",
    "Chinese": "🇨🇳",
    "Danish": "🇩🇰",
    "American": "🇺🇸",
    "Austrian": "🇦🇹",
    "Italian": "🇮🇹",
    "Brazilian": "🇧🇷",
    "New Zealander": "🇳🇿",
    "Polish": "🇵🇱",
    "Swiss": "🇨🇭",
    "South African": "🇿🇦",
    "Venezuelan": "🇻🇪",
    "Indonesian": "🇮🇩",
    "Argentine": "🇦🇷",
    # Country codes (for OpenF1 API) - IOC codes
    "NED": "🇳🇱",
    "GBR": "🇬🇧",
    "AUS": "🇦🇺",
    "MCO": "🇲🇨",
    "ESP": "🇪🇸",
    "MEX": "🇲🇽",
    "GER": "🇩🇪",
    "FRA": "🇫🇷",
    "JPN": "🇯🇵",
    "CAN": "🇨🇦",
    "THA": "🇹🇭",
    "FIN": "🇫🇮",
    "CHN": "🇨🇳",
    "DEN": "🇩🇰",
    "USA": "🇺🇸",
    "AUT": "🇦🇹",
    "ITA": "🇮🇹",
    "BRA": "🇧🇷",
    "NZL": "🇳🇿",
    "RUS": "🇷🇺",
    "POL": "🇵🇱",
    "CHE": "🇨🇭",
    "ZAF": "🇿🇦",
    "VEN": "🇻🇪",
    "IDN": "🇮🇩",
    "ARG": "🇦🇷",
}

# Driver number to nationality mapping (2025 season)
DRIVER_NATIONALITIES = {
    1: "NED",  # Max Verstappen
    4: "GBR",  # Lando Norris
    5: "BRA",  # Gabriel Bortoleto
    6: "FRA",  # Isack Hadjar
    10: "FRA",  # Pierre Gasly
    12: "ITA",  # Kimi Antonelli
    14: "ESP",  # Fernando Alonso
    16: "MCO",  # Charles Leclerc
    18: "CAN",  # Lance Stroll
    22: "JPN",  # Yuki Tsunoda
    23: "THA",  # Alexander Albon
    27: "GER",  # Nico Hulkenberg
    30: "NZL",  # Liam Lawson
    31: "FRA",  # Esteban Ocon
    43: "ARG",  # Franco Colapinto
    44: "GBR",  # Lewis Hamilton
    55: "ESP",  # Carlos Sainz
    63: "GBR",  # George Russell
    81: "AUS",  # Oscar Piastri
    87: "GBR",  # Oliver Bearman
}

# Comprehensive F1 circuit coordinates for weather API
CIRCUIT_COORDS = {
    # Current F1 Circuits (2024-2025) - Official names
    "Bahrain International Circuit": (26.0325, 50.5106),
    "Jeddah Corniche Circuit": (21.6319, 39.1044),
    "Albert Park Circuit": (-37.8497, 144.9680),
    "Suzuka Circuit": (34.8431, 136.5410),
    "Shanghai International Circuit": (31.3389, 121.2197),
    "Miami International Autodrome": (25.9581, -80.2389),
    "Autodromo Enzo e Dino Ferrari": (44.3439, 11.7167),
    "Circuit de Monaco": (43.7347, 7.4206),
    "Circuit de Barcelona-Catalunya": (41.5699, 2.2570),
    "Circuit Gilles Villeneuve": (45.5000, -73.5228),
    "Red Bull Ring": (47.2197, 14.7647),
    "Silverstone Circuit": (52.0720, -1.0170),
    "Hungaroring": (47.5789, 19.2486),
    "Circuit de Spa-Francorchamps": (50.4372, 5.9714),
    "Circuit Zandvoort": (52.3888, 4.5409),
    "Autodromo Nazionale di Monza": (45.6190, 9.2816),
    "Marina Bay Street Circuit": (1.2914, 103.8632),
    "Baku City Circuit": (40.4093, 49.8671),
    "Circuit of the Americas": (30.1328, -97.6411),
    "Autodromo Hermanos Rodriguez": (19.4042, -99.0907),
    "Autodromo Jose Carlos Pace": (-23.7036, -46.6997),
    "Las Vegas Street Circuit": (36.1147, -115.1739),
    "Lusail International Circuit": (25.4888, 51.4543),
    "Yas Marina Circuit": (24.4672, 54.6031),
    # Alternative/common names for matching
    "Sakhir": (26.0325, 50.5106),
    "Jeddah": (21.6319, 39.1044),
    "Melbourne": (-37.8497, 144.9680),
    "Suzuka": (34.8431, 136.5410),
    "Shanghai": (31.3389, 121.2197),
    "Miami": (25.9581, -80.2389),
    "Imola": (44.3439, 11.7167),
    "Monaco": (43.7347, 7.4206),
    "Barcelona": (41.5699, 2.2570),
    "Montreal": (45.5000, -73.5228),
    "Spielberg": (47.2197, 14.7647),
    "Silverstone": (52.0720, -1.0170),
    "Budapest": (47.5789, 19.2486),
    "Spa": (50.4372, 5.9714),
    "Zandvoort": (52.3888, 4.5409),
    "Monza": (45.6190, 9.2816),
    "Singapore": (1.2914, 103.8632),
    "Baku": (40.4093, 49.8671),
    "Austin": (30.1328, -97.6411),
    "Mexico City": (19.4042, -99.0907),
    "Sao Paulo": (-23.7036, -46.6997),
    "Interlagos": (-23.7036, -46.6997),
    "Las Vegas": (36.1147, -115.1739),
    "Lusail": (25.4888, 51.4543),
    "Abu Dhabi": (24.4672, 54.6031),
}


def get_country_flag(nationality):
    """Get flag emoji for a nationality"""
    if not nationality:
        return "🏳️"

    nationality = nationality.strip()

    # Direct lookup (handles exact matches including 3-letter codes)
    if nationality in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[nationality]

    # Try uppercase (for country codes like NED, GBR)
    if nationality.upper() in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[nationality.upper()]

    # Try lowercase
    if nationality.lower() in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[nationality.lower()]

    # Try title case
    if nationality.title() in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[nationality.title()]

    # Partial match
    nationality_lower = nationality.lower()
    for key, flag in COUNTRY_FLAGS.items():
        if key.lower() in nationality_lower or nationality_lower in key.lower():
            return flag

    return "🏳️"


def to_baku(d, t):
    """Convert UTC time to Baku time"""
    if not t or t == "TBA":
        return f"{d} (TBA)"
    try:
        # strip trailing Z if present
        tzinfo = ZoneInfo("UTC")
        if t.endswith("Z"):
            t2 = t[:-1]
        else:
            t2 = t
        dt = datetime.fromisoformat(d + "T" + t2)
        # assume dt is UTC if naive
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tzinfo)
        baku = dt.astimezone(ZoneInfo("Asia/Baku"))
        date_str = baku.strftime("%d %b")
        time_str = baku.strftime("%H:%M")
        return f"{date_str} {time_str}"
    except Exception:
        return f"{d} {t}"


def get_circuit_coordinates(location_name):
    """Get coordinates for a circuit with fuzzy matching"""
    # Direct match first
    if location_name in CIRCUIT_COORDS:
        return CIRCUIT_COORDS[location_name]

    # Fuzzy matching for partial names
    location_lower = location_name.lower()
    for circuit_name, coords in CIRCUIT_COORDS.items():
        if (
            location_lower in circuit_name.lower()
            or circuit_name.lower() in location_lower
        ):
            return coords

    # Geocoding fallback
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_name}&count=1"
        response = requests.get(geo_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                result = data["results"][0]
                return (result["latitude"], result["longitude"])
    except Exception:
        pass

    return None


def check_active_f1_session():
    """Check if there's currently an active F1 session using OpenF1 API"""
    try:
        logger.info(TRANSLATIONS["live_session_check"])
        now = datetime.now(ZoneInfo("UTC"))
        current_year = now.year

        # Check current and next year for sessions
        years_to_check = [current_year]
        if now.month >= 11:
            years_to_check.append(current_year + 1)

        sessions = []
        for year in years_to_check:
            try:
                sessions_url = f"https://api.openf1.org/v1/sessions?year={year}"
                sessions_response = requests.get(sessions_url, timeout=10)
                if sessions_response.status_code == 200:
                    sessions.extend(sessions_response.json())
            except Exception as e:
                logger.error(f"Error fetching sessions for year {year}: {e}")
                continue

        if not sessions:
            logger.warning("No sessions found")
            return False

        # Check if any session is currently active (within the last 2 hours and next 4 hours)
        for session in sessions:
            session_start = session.get("date_start")
            session_end = session.get("date_end")

            if session_start:
                try:
                    start_dt = datetime.fromisoformat(
                        session_start.replace("Z", "+00:00")
                    )
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.replace(tzinfo=ZoneInfo("UTC"))

                    # Check if session is currently running or will start soon
                    time_diff_start = (start_dt - now).total_seconds() / 3600  # hours
                    time_diff_end = 0

                    if session_end:
                        end_dt = datetime.fromisoformat(
                            session_end.replace("Z", "+00:00")
                        )
                        if end_dt.tzinfo is None:
                            end_dt = end_dt.replace(tzinfo=ZoneInfo("UTC"))
                        time_diff_end = (end_dt - now).total_seconds() / 3600  # hours

                        # Session is active if it started within last 2 hours and hasn't ended + 1 hour grace period
                        if (
                            -2 <= time_diff_start <= 0 and time_diff_end > -1
                        ):  # Allow 1 hour after session ends
                            logger.info(
                                f"Active session found: {session.get('session_name', 'Unknown')}"
                            )
                            return True
                    else:
                        # If no end time, check if session started recently (within 2 hours)
                        if (
                            -2 <= time_diff_start <= 1
                        ):  # Allow 1 hour future for upcoming sessions
                            logger.info(
                                f"Upcoming session found: {session.get('session_name', 'Unknown')}"
                            )
                            return True

                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing session times: {e}")
                    continue

        logger.info(TRANSLATIONS["live_session_inactive"])
        return False

    except Exception as e:
        logger.error(f"{TRANSLATIONS['live_session_error'].format(str(e))}")
        return False


def get_current_standings():
    """Get current F1 driver standings"""
    try:
        logger.info("Fetching current standings")
        now = datetime.now()
        season = now.year if now.month > 3 else now.year - 1

        # Try multiple APIs with better error handling
        apis = [
            f"https://api.jolpi.ca/ergast/f1/{season}/driverStandings.json",
        ]

        data = None
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    break
            except Exception as e:
                logger.error(f"Error fetching standings from {api_url}: {e}")
                continue

        if not data:
            return TRANSLATIONS["api_unavailable"]

        try:
            standings_list = (
                data.get("MRData", {})
                .get("StandingsTable", {})
                .get("StandingsLists", [])
            )
            if not standings_list:
                return TRANSLATIONS["no_standings"]

            standings = standings_list[0].get("DriverStandings", [])
            if not standings:
                return TRANSLATIONS["no_driver_standings"]

            actual_season = standings_list[0].get("season", season)
        except Exception as e:
            logger.error(f"Error parsing standings data: {e}")
            return TRANSLATIONS["invalid_data"]

        message = f"🏆 {actual_season} {TRANSLATIONS['season_driver_standings']}\n\n"

        for driver in standings:
            try:
                pos = driver.get("position", "?")
                driver_info = driver.get("Driver", {})
                given_name = driver_info.get("givenName", "Unknown")
                family_name = driver_info.get("familyName", "Driver")
                full_name = f"{given_name} {family_name.upper()}"
                nationality = driver_info.get("nationality", "")
                flag = get_country_flag(nationality)
                points = driver.get("points", "0")

                message += (
                    f"{pos}. {flag} {full_name} ({points} {TRANSLATIONS['points']})\n"
                )
            except Exception as e:
                logger.error(f"Error processing driver data: {e}")
                continue

        return message
    except Exception as e:
        logger.error(f"Error in get_current_standings: {e}")
        return TRANSLATIONS["service_unavailable"]


def get_constructor_standings():
    """Get constructor standings"""
    try:
        logger.info("Fetching constructor standings")
        now = datetime.now()
        season = now.year if now.month > 3 else now.year - 1

        # Try multiple APIs
        apis = [
            f"https://api.jolpi.ca/ergast/f1/{season}/constructorStandings.json",
        ]

        data = None
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    break
            except Exception as e:
                logger.error(
                    f"Error fetching constructor standings from {api_url}: {e}"
                )
                continue

        if not data:
            return TRANSLATIONS["api_unavailable"]

        try:
            standings_list = (
                data.get("MRData", {})
                .get("StandingsTable", {})
                .get("StandingsLists", [])
            )
            if not standings_list:
                return TRANSLATIONS["no_constructor_standings"]

            standings = standings_list[0].get("ConstructorStandings", [])
            if not standings:
                return TRANSLATIONS["no_constructor_standings"]

            actual_season = standings_list[0].get("season", season)
        except Exception as e:
            logger.error(f"Error parsing constructor standings data: {e}")
            return TRANSLATIONS["invalid_data"]

        # Team flags
        team_flags = {
            "Red Bull": "🇦🇹",
            "Ferrari": "🇮🇹",
            "Mercedes": "🇩🇪",
            "McLaren": "🇬🇧",
            "Aston Martin": "🇬🇧",
            "Alpine": "🇫🇷",
            "Williams": "🇬🇧",
            "AlphaTauri": "🇮🇹",
            "RB": "🇮🇹",
            "Alfa Romeo": "🇨🇭",
            "Sauber": "🇨🇭",
            "Haas": "🇺🇸",
        }

        message = f"🏆 *{TRANSLATIONS['season_constructor_standings'].format(actual_season)}*\n\n"

        for pos, team in enumerate(standings, 1):
            try:
                constructor = team.get("Constructor", {})
                team_name = constructor.get("name", "Unknown Team")
                points = team.get("points", "0")

                flag = ""
                for key, emoji in team_flags.items():
                    if key in team_name:
                        flag = emoji + " "
                        break

                message += (
                    f"{pos}. {flag}*{team_name}* - {points} {TRANSLATIONS['points']}\n"
                )
            except Exception as e:
                logger.error(f"Error processing team data: {e}")
                continue

        return message
    except Exception as e:
        logger.error(f"Error in get_constructor_standings: {e}")
        return TRANSLATIONS["service_unavailable"]


def get_last_session_results():
    """Get last session results using OpenF1 API with enhanced data"""
    try:
        logger.info("Fetching last session results")
        now = datetime.now(ZoneInfo("UTC"))
        current_year = now.year

        years_to_check = [current_year]
        if now.month <= 3:
            years_to_check.insert(0, current_year - 1)

        sessions = []
        for year in years_to_check:
            try:
                sessions_url = f"https://api.openf1.org/v1/sessions?year={year}"
                sessions_response = requests.get(sessions_url, timeout=10)
                if sessions_response.status_code == 200:
                    sessions.extend(sessions_response.json())
            except Exception as e:
                logger.error(f"Error fetching sessions for year {year}: {e}")
                continue

        if not sessions:
            return TRANSLATIONS["no_sessions"]

        latest_session = None
        for session in reversed(sessions):
            session_start = session.get("date_start")
            session_type = session.get("session_type")

            if session_start and session_type in ["Qualifying", "Sprint", "Race"]:
                try:
                    start_dt = datetime.fromisoformat(
                        session_start.replace("Z", "+00:00")
                    )
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.replace(tzinfo=ZoneInfo("UTC"))

                    if start_dt < (now - timedelta(hours=2)):
                        latest_session = session
                        break
                except Exception as e:
                    logger.error(f"Error parsing session start time: {e}")
                    continue

        if not latest_session:
            return TRANSLATIONS["no_recent_sessions"]

        session_key = latest_session.get("session_key")
        session_type = latest_session.get("session_type")
        meeting_name = latest_session.get("meeting_name", "Grand Prix")
        country_name = latest_session.get("country_name", "")
        flag = get_country_flag(country_name)

        # Get positions
        results_url = f"https://api.openf1.org/v1/position?session_key={session_key}"
        results_response = requests.get(results_url, timeout=10)
        if results_response.status_code != 200:
            return TRANSLATIONS["no_results"].format(session_type)

        positions_data = results_response.json()
        if not positions_data:
            return TRANSLATIONS["no_position_data"].format(session_type)

        final_positions = {}
        for pos_entry in positions_data:
            driver_number = pos_entry.get("driver_number")
            position = pos_entry.get("position")
            date = pos_entry.get("date")

            if driver_number and position and date:
                if (
                    driver_number not in final_positions
                    or date > final_positions[driver_number]["date"]
                ):
                    final_positions[driver_number] = {
                        "position": position,
                        "date": date,
                    }

        # Get driver info
        drivers_url = f"https://api.openf1.org/v1/drivers?session_key={session_key}"
        drivers_response = requests.get(drivers_url, timeout=10)
        drivers_info = {}
        if drivers_response.status_code == 200:
            for driver in drivers_response.json():
                driver_number = driver.get("driver_number")
                if driver_number:
                    driver_name = f"{driver.get('first_name', '')} {driver.get('last_name', '')}".strip()
                    country_code = driver.get(
                        "country_code"
                    ) or DRIVER_NATIONALITIES.get(driver_number, "")

                    drivers_info[driver_number] = {
                        "name": driver_name,
                        "country": country_code,
                        "team": driver.get("team_name", ""),
                    }

        sorted_positions = sorted(
            final_positions.items(), key=lambda x: x[1]["position"]
        )
        if not sorted_positions:
            return TRANSLATIONS["no_final_positions"].format(session_type)

        emoji = (
            "🏁"
            if session_type == "Sprint"
            else "⏱️" if session_type == "Qualifying" else "🏆"
        )
        session_type_az = TRANSLATIONS.get(session_type.lower(), session_type)
        message = f"{emoji} {flag} *{meeting_name} {session_type_az}*\n\n"

        for driver_number, pos_data in sorted_positions[:20]:
            position = pos_data["position"]
            driver_info = drivers_info.get(driver_number, {})
            driver_name = driver_info.get("name", f"Driver {driver_number}")
            driver_country = driver_info.get("country", "")
            driver_flag = get_country_flag(driver_country)
            team_name = driver_info.get("team", "")

            line = f"{position}. {driver_flag} {driver_name}"

            if session_type in ["Race", "Sprint"] and team_name:
                line += f" ({team_name})"

            if position == 1:
                line += f" - {TRANSLATIONS['winner']}"

            message += line + "\n"

        return message

    except Exception as e:
        logger.error(f"Error in get_last_session_results: {e}")
        return TRANSLATIONS["error_fetching_session"].format(str(e))


def get_f1_season_calendar():
    """Fetch and display the current F1 season's race schedule"""
    try:
        logger.info("Fetching F1 season calendar")
        now = datetime.now(ZoneInfo("UTC"))
        season = now.year if now.month > 3 else now.year - 1

        # Try multiple APIs
        apis = [
            f"https://api.jolpi.ca/ergast/f1/{season}.json",
        ]

        data = None
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    break
            except Exception as e:
                logger.error(f"Error fetching calendar from {api_url}: {e}")
                continue

        if not data:
            return TRANSLATIONS["api_unavailable"]

        try:
            races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            if not races:
                return TRANSLATIONS["no_race_schedule"]
        except Exception as e:
            logger.error(f"Error parsing calendar data: {e}")
            return TRANSLATIONS["invalid_data"]

        message = f"🏎️ *{season} F1 Mövsüm Cədvəli*\n\n"

        for race in races:
            try:
                race_name = race.get("raceName", "Grand Prix")
                circuit = race.get("Circuit", {})
                location = circuit.get("Location", {})
                locality = location.get("locality", "")
                country = location.get("country", "")
                race_date = race.get("date")
                race_time = race.get("time", "TBA")

                flag = get_country_flag(country)

                # Convert to Baku time
                baku_time = to_baku(race_date, race_time)

                # Determine race status
                race_dt_str = f"{race_date}T{race_time.replace('Z', '')}"
                race_dt = datetime.fromisoformat(race_dt_str)
                if race_dt.tzinfo is None:
                    race_dt = race_dt.replace(tzinfo=ZoneInfo("UTC"))

                if race_dt < now:
                    status = "🏁 Tamamlandı"
                elif race_dt > (now + timedelta(days=7)):
                    status = "📅 Gələcək"
                else:
                    status = "🔴 Cari"

                message += f"{flag} *{race_name}*\n"
                message += f"📍 {locality}, {country}\n"
                message += f"📅 {baku_time} ({status})\n\n"

            except Exception as e:
                logger.error(f"Error processing race data: {e}")
                continue

        return message
    except Exception as e:
        logger.error(f"Error in get_f1_season_calendar: {e}")
        return TRANSLATIONS["error_fetching_race"].format(str(e))


def get_next_race():
    """Get next race schedule using Jolpica API"""
    try:
        logger.info("Fetching next race schedule")
        now = datetime.now(ZoneInfo("UTC"))
        season = now.year if now.month > 3 else now.year - 1

        # Try multiple APIs
        apis = [
            f"https://api.jolpi.ca/ergast/f1/{season}.json",
        ]

        data = None
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    break
            except Exception as e:
                logger.error(f"Error fetching race schedule from {api_url}: {e}")
                continue

        if not data:
            return TRANSLATIONS["api_unavailable"]

        try:
            races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            if not races:
                return TRANSLATIONS["no_race_schedule"]
        except Exception as e:
            logger.error(f"Error parsing race data: {e}")
            return TRANSLATIONS["invalid_data"]

        # Find next race
        next_race = None
        for race in races:
            try:
                race_date = race.get("date")
                race_time = race.get("time", "00:00")

                if race_date:
                    race_dt_str = f"{race_date}T{race_time.replace('Z', '')}"
                    race_dt = datetime.fromisoformat(race_dt_str)
                    if race_dt.tzinfo is None:
                        race_dt = race_dt.replace(tzinfo=ZoneInfo("UTC"))

                    if race_dt >= now:
                        next_race = race
                        break
            except Exception as e:
                logger.error(f"Error parsing race date/time: {e}")
                continue

        if not next_race:
            return TRANSLATIONS["season_completed"]

        # Extract race info
        race_name = next_race.get("raceName", "Grand Prix")
        circuit = next_race.get("Circuit", {})
        location = circuit.get("Location", {})
        locality = location.get("locality", "")
        country = location.get("country", "")

        flag = get_country_flag(country)

        message = f"{TRANSLATIONS['next_race']}\n"
        message += f"{flag} *{race_name}*\n\n"

        # Collect all sessions with times
        sessions = []

        # FP1
        fp1 = next_race.get("FirstPractice", {})
        fp1_date = fp1.get("date")
        fp1_time = fp1.get("time", "TBA")
        if fp1_date and fp1_time != "TBA":
            sessions.append((fp1_date, fp1_time, TRANSLATIONS["fp1"]))

        # FP2
        fp2 = next_race.get("SecondPractice", {})
        fp2_date = fp2.get("date")
        fp2_time = fp2.get("time", "TBA")
        if fp2_date and fp2_time != "TBA":
            sessions.append((fp2_date, fp2_time, TRANSLATIONS["fp2"]))

        # FP3
        fp3 = next_race.get("ThirdPractice", {})
        fp3_date = fp3.get("date")
        fp3_time = fp3.get("time", "TBA")
        if fp3_date and fp3_time != "TBA":
            sessions.append((fp3_date, fp3_time, TRANSLATIONS["fp3"]))

        # Sprint Qualifying
        sprint_quali = next_race.get("SprintQualifying", {})
        sq_date = sprint_quali.get("date")
        sq_time = sprint_quali.get("time", "TBA")
        if sq_date and sq_time != "TBA":
            sessions.append((sq_date, sq_time, TRANSLATIONS["sprint_qualifying"]))

        # Sprint
        sprint = next_race.get("Sprint", {})
        sprint_date = sprint.get("date")
        sprint_time = sprint.get("time", "TBA")
        if sprint_date and sprint_time != "TBA":
            sessions.append((sprint_date, sprint_time, TRANSLATIONS["sprint"]))

        # Qualifying
        quali = next_race.get("Qualifying", {})
        quali_date = quali.get("date")
        quali_time = quali.get("time", "TBA")
        if quali_date and quali_time != "TBA":
            sessions.append((quali_date, quali_time, TRANSLATIONS["qualifying"]))

        # Race
        race_date = next_race.get("date")
        race_time = next_race.get("time", "TBA")
        if race_date and race_time != "TBA":
            sessions.append((race_date, race_time, TRANSLATIONS["race"]))

        # Sort sessions by date and time
        sessions.sort(key=lambda x: (x[0], x[1]))

        # Display sessions in chronological order
        for session_date, session_time, session_name in sessions:
            baku_time = to_baku(session_date, session_time)
            message += f"*{session_name}:* {baku_time}\n"

        message += f"\n_{TRANSLATIONS['all_times_baku']}_\n"

        # Add weather forecast
        try:
            coords = get_circuit_coordinates(locality)
            if coords and race_date:
                race_date_obj = datetime.fromisoformat(race_date)
                friday = race_date_obj - timedelta(days=2)
                saturday = race_date_obj - timedelta(days=1)
                sunday = race_date_obj

                meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&daily=temperature_2m_max,precipitation_probability_max,wind_speed_10m_max&start_date={friday.date()}&end_date={sunday.date()}"
                weather_response = requests.get(meteo_url, timeout=15)

                if weather_response.status_code == 200:
                    weather_data = weather_response.json()
                    daily = weather_data.get("daily", {})
                    temps = daily.get("temperature_2m_max", [])
                    rain_probs = daily.get("precipitation_probability_max", [])
                    wind_speeds = daily.get("wind_speed_10m_max", [])

                    if temps and len(temps) >= 3:
                        message += "\n🌤️ *Hava proqnozu:*\n"
                        days = [
                            TRANSLATIONS["friday"],
                            TRANSLATIONS["saturday"],
                            TRANSLATIONS["sunday"],
                        ]
                        for i, day in enumerate(days):
                            if i < len(temps):
                                temp = temps[i]
                                rain = rain_probs[i] if i < len(rain_probs) else 0
                                wind = wind_speeds[i] if i < len(wind_speeds) else 0
                                rain_icon = (
                                    "🌧️" if rain >= 60 else "⛅" if rain >= 30 else "☀️"
                                )
                                message += f"{day}: {temp:.1f}°C {rain_icon} {int(rain)}% 💨{wind:.1f}km/h\n"
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            pass

        return message
    except Exception as e:
        logger.error(f"Error in get_next_race: {e}")
        return TRANSLATIONS["error_fetching_race"].format(str(e))


def load_user_streams():
    """Load user streams from JSON file"""
    if not os.path.exists("user_streams.json"):
        return {}
    try:
        with open("user_streams.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading user streams: {e}")
        return {}


def save_user_streams(data):
    """Save user streams to JSON file"""
    try:
        with open("user_streams.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving user streams: {e}")
        return False


def get_streams(user_id=None):
    """Read stream links and return message with keyboard"""
    try:
        all_streams = []

        # Load global streams
        if os.path.exists("streams.txt"):
            with open("streams.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "|" in line:
                            parts = line.split("|", 1)
                            all_streams.append(
                                {"name": parts[0].strip(), "url": parts[1].strip()}
                            )

        # Load user streams
        user_streams_data = load_user_streams()
        if user_id and str(user_id) in user_streams_data:
            for stream in user_streams_data[str(user_id)]:
                all_streams.append(
                    {"name": stream.get("name"), "url": stream.get("url")}
                )

        if not all_streams:
            return TRANSLATIONS["no_streams"], None

        keyboard = []
        for idx, stream in enumerate(all_streams, 1):
            keyboard.append(
                [InlineKeyboardButton(f"🎦 {stream['name']}", url=stream["url"])]
            )
        keyboard = InlineKeyboardMarkup(keyboard)
        message = (
            f"{TRANSLATIONS['available_streams']}\n\n{TRANSLATIONS['tap_to_open']}"
        )

        return message, keyboard
    except Exception as e:
        logger.error(f"Error getting streams: {e}")
        return f"❌ Error: {str(e)}", None


# Global cache for calendar data
CALENDAR_CACHE = {
    "data": None,
    "timestamp": None,
    "expiry": 3600,  # 1 hour cache expiry
}


def get_cached_calendar():
    """Retrieve cached calendar data if available and not expired"""
    if CALENDAR_CACHE["data"] and CALENDAR_CACHE["timestamp"]:
        now = datetime.now(ZoneInfo("UTC")).timestamp()
        if now - CALENDAR_CACHE["timestamp"] < CALENDAR_CACHE["expiry"]:
            return CALENDAR_CACHE["data"]
    return None


def set_cached_calendar(data):
    """Cache calendar data with current timestamp"""
    CALENDAR_CACHE["data"] = data
    CALENDAR_CACHE["timestamp"] = datetime.now(ZoneInfo("UTC")).timestamp()


# ==================== TELEGRAM BOT HANDLERS ====================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with comprehensive inline keyboard"""
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} started the bot")
    else:
        logger.info("User started the bot (unknown user)")
    keyboard = [
        [
            InlineKeyboardButton(
                TRANSLATIONS["driver_standings"], callback_data="standings"
            ),
            InlineKeyboardButton(
                TRANSLATIONS["constructor_standings"], callback_data="constructors"
            ),
        ],
        [
            InlineKeyboardButton(
                TRANSLATIONS["last_session"], callback_data="lastrace"
            ),
            InlineKeyboardButton(
                TRANSLATIONS["schedule_weather"], callback_data="nextrace"
            ),
        ],
        [
            InlineKeyboardButton(TRANSLATIONS["live_timing"], callback_data="live"),
            InlineKeyboardButton("📅 Mövsüm Cədvəli", callback_data="calendar"),
        ],
        [
            InlineKeyboardButton(TRANSLATIONS["streams"], callback_data="streams"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = f"""{TRANSLATIONS["welcome_title"]}
    
{TRANSLATIONS["welcome_text"]}"""

    if isinstance(update.message, Message):
        await update.message.reply_text(
            welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
        )


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show menu buttons"""
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested menu")
    else:
        logger.info("User requested menu (unknown user)")
    keyboard = [
        [
            InlineKeyboardButton(
                TRANSLATIONS["driver_standings"], callback_data="standings"
            ),
            InlineKeyboardButton(
                TRANSLATIONS["constructor_standings"], callback_data="constructors"
            ),
        ],
        [
            InlineKeyboardButton(
                TRANSLATIONS["last_session"], callback_data="lastrace"
            ),
            InlineKeyboardButton(
                TRANSLATIONS["schedule_weather"], callback_data="nextrace"
            ),
        ],
        [
            InlineKeyboardButton(TRANSLATIONS["live_timing"], callback_data="live"),
            InlineKeyboardButton("📅 Mövsüm Cədvəli", callback_data="calendar"),
        ],
        [
            InlineKeyboardButton(
                TRANSLATIONS["help_commands_btn"], callback_data="help"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if isinstance(update.message, Message):
        await update.message.reply_text(
            f"{TRANSLATIONS['menu_title']}\n\n{TRANSLATIONS['menu_text']}",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    if query is None:
        return
    
    await query.answer()
    logger.info(f"User {query.from_user.id} clicked button: {query.data}")

    try:
        if query.data == "standings":
            message = get_current_standings()
        elif query.data == "constructors":
            message = get_constructor_standings()
        elif query.data == "lastrace":
            message = get_last_session_results()
        elif query.data == "nextrace":
            message = get_next_race()
        elif query.data == "calendar":
            # Fetch and display the F1 season calendar
            cached_data = get_cached_calendar()
            if cached_data:
                message = cached_data
            else:
                message = get_f1_season_calendar()
                set_cached_calendar(message)
        elif query.data == "live":
            # Check if there's an active F1 session before starting live updates
            if not check_active_f1_session():
                message = "❌ Hal-hazırda aktiv F1 sessiyası yoxdur\n\n🔴 Canlı vaxt yalnız F1 yarış həftəsonlarında, sessiya gedərkən mövcuddur.\n\n⏰ Canlı vaxt sessiyadan 2 saat əvvəl başlayır və sessiyadan 1 saat sonra dayanır.\n\n📊 Canlı vaxt göstərir:\n• Sürücülərin mövqeləri\n• Dövrə vaxtları\n• Interval vaxtları\n• Təkər məlumatları\n• Hər 30 saniyədə avtomatik yeniləmə\n\nAlternativlər:\n• /nextrace - Gələn yarış və hava proqnozu\n• /lastrace - Son sessiya nəticələri"
            else:
                message = "🔴 Canlı sessiya aktivdir! Mövqelər yenilənir...\n\n⏳ Zəhmət olmasa gözləyin, canlı məlumatlar hazırlanır..."
        elif query.data == "streams":
            user_id = query.from_user.id if query.from_user else None
            message, keyboard = get_streams(user_id)
            if isinstance(query.message, Message):
                if keyboard:
                    await query.message.reply_text(
                        message, parse_mode="Markdown", reply_markup=keyboard
                    )
                else:
                    await query.message.reply_text(message, parse_mode="Markdown")
            return
        elif query.data == "help":
            message = f"""{TRANSLATIONS["stream_help_title"]}

{TRANSLATIONS["stream_help_best"]}

{TRANSLATIONS["stream_help_how"]}

{TRANSLATIONS["stream_help_vlc"]}"""
        else:
            message = TRANSLATIONS["unknown_command"]
    except Exception as e:
        logger.error(f"Error in button_handler: {e}")
        message = TRANSLATIONS["error_occurred"].format(str(e))

    # Send result
    if isinstance(query.message, Message):
        await query.message.reply_text(message, parse_mode="Markdown")


# Command handlers
async def standings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested standings")
    else:
        logger.info("User requested standings (unknown user)")
    if isinstance(update.message, Message):
        await update.message.reply_text(TRANSLATIONS["loading"])
        message = get_current_standings()
        await update.message.reply_text(message, parse_mode="Markdown")


async def constructors_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested constructor standings")
    else:
        logger.info("User requested constructor standings (unknown user)")
    if isinstance(update.message, Message):
        await update.message.reply_text(TRANSLATIONS["loading"])
        message = get_constructor_standings()
        await update.message.reply_text(message, parse_mode="Markdown")


async def lastrace_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested last race results")
    else:
        logger.info("User requested last race results (unknown user)")
    if isinstance(update.message, Message):
        await update.message.reply_text(TRANSLATIONS["loading"])
        message = get_last_session_results()
        await update.message.reply_text(message, parse_mode="Markdown")


async def nextrace_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested next race")
    else:
        logger.info("User requested next race (unknown user)")
    if isinstance(update.message, Message):
        await update.message.reply_text(TRANSLATIONS["loading"])
        message = get_next_race()
        await update.message.reply_text(message, parse_mode="Markdown")


async def live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Live timing with session checking"""
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested live timing")
    else:
        logger.info("User requested live timing (unknown user)")
    if isinstance(update.message, Message):
        loading_msg = await update.message.reply_text(
            TRANSLATIONS["live_session_check"]
        )

        # Check if there's an active F1 session
        if not check_active_f1_session():
            await loading_msg.edit_text(
                "❌ Hal-hazırda aktiv F1 sessiyası yoxdur\n\n🔴 Canlı vaxt yalnız F1 yarış həftəsonlarında, sessiya gedərkən mövcuddur.\n\n⏰ Canlı vaxt sessiyadan 2 saat əvvəl başlayır və sessiyadan 1 saat sonra dayanır.\n\n📊 Canlı vaxt göstərir:\n• Sürücülərin mövqeləri\n• Dövrə vaxtları\n• Interval vaxtları\n• Təkər məlumatları\n• Hər 30 saniyədə avtomatik yeniləmə\n\nAlternativlər:\n• /nextrace - Gələn yarış və hava proqnozu\n• /lastrace - Son sessiya nəticələri"
            )
            return

        await loading_msg.edit_text(
            "🔴 Canlı sessiya aktivdir! Mövqelər yenilənir...\n\n⏳ Zəhmət olmasa gözləyin, canlı məlumatlar hazırlanır..."
        )

        # For now, show a placeholder message since we don't have live timing implementation
        # In a full implementation, this would fetch live data from OpenF1 API
        live_message = """🔴 *Canlı Vaxt Mövcuddur!*

🏁 Mövcud sessiya: *Təsnifat* (Bakı vaxtı ilə)
🕐 Başlama vaxtı: 20:00
📍 Məkan: Baku City Circuit

📊 Mövcud məlumatlar:
• Sürücülərin cari mövqeləri
• Dövrə vaxtları
• Interval vaxtları
• Təkər məlumatları

🔄 Məlumatlar hər 30 saniyədə yenilənir

ℹ️ *Qeyd: Bu funksiya F1 sessiyaları zamanı aktiv olur. Canlı məlumatlar OpenF1 API-dən əldə olunur.*"""

        await loading_msg.edit_text(live_message, parse_mode="Markdown")


async def streams_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get available streams"""
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested streams")
    else:
        logger.info("User requested streams (unknown user)")
    if isinstance(update.message, Message):
        user_id = update.message.from_user.id if update.message.from_user else None
        message, keyboard = get_streams(user_id)
        if keyboard:
            await update.message.reply_text(
                message, parse_mode="Markdown", reply_markup=keyboard
            )
        else:
            await update.message.reply_text(message, parse_mode="Markdown")


async def addstream_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a personal stream"""
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested to add stream")
    else:
        logger.info("User requested to add stream (unknown user)")
    if not isinstance(update.message, Message) or update.message.from_user is None:
        return

    user_id = str(update.message.from_user.id)
    args = context.args

    if not args:
        await update.message.reply_text(TRANSLATIONS["usage_addstream"])
        return

    full_text = " ".join(args)
    if "|" not in full_text:
        await update.message.reply_text(TRANSLATIONS["use_format"])
        return

    name, url = full_text.split("|", 1)
    name = name.strip()
    url = url.strip()

    if not name or not url:
        await update.message.reply_text(TRANSLATIONS["name_url_required"])
        return

    user_streams = load_user_streams()
    if user_id not in user_streams:
        user_streams[user_id] = []

    user_streams[user_id].append({"name": name, "url": url})

    if save_user_streams(user_streams):
        await update.message.reply_text(TRANSLATIONS["stream_added"].format(name))
    else:
        await update.message.reply_text(TRANSLATIONS["stream_error"])


async def removestream_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a personal stream"""
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested to remove stream")
    else:
        logger.info("User requested to remove stream (unknown user)")
    if not isinstance(update.message, Message) or update.message.from_user is None:
        return

    user_id = str(update.message.from_user.id)
    args = context.args

    if not args:
        await update.message.reply_text(TRANSLATIONS["usage_removestream"])
        return

    try:
        index = int(args[0]) - 1
    except ValueError:
        await update.message.reply_text(TRANSLATIONS["invalid_removestream"])
        return

    user_streams = load_user_streams()
    if user_id not in user_streams or not user_streams[user_id]:
        await update.message.reply_text(TRANSLATIONS["no_personal_streams"])
        return

    if index < 0 or index >= len(user_streams[user_id]):
        await update.message.reply_text(
            TRANSLATIONS["invalid_number_range"].format(len(user_streams[user_id]))
        )
        return

    removed = user_streams[user_id].pop(index)

    if save_user_streams(user_streams):
        await update.message.reply_text(
            TRANSLATIONS["stream_removed"].format(removed["name"])
        )
    else:
        await update.message.reply_text(TRANSLATIONS["error_removing"])


async def streamhelp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show stream help"""
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested stream help")
    else:
        logger.info("User requested stream help (unknown user)")
    if not isinstance(update.message, Message):
        return

    help_text = f"""{TRANSLATIONS["stream_help_title"]}

{TRANSLATIONS["stream_help_best"]}

{TRANSLATIONS["stream_help_how"]}

{TRANSLATIONS["stream_help_vlc"]}"""

    await update.message.reply_text(help_text, parse_mode="Markdown")


async def playstream_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send stream link"""
    if update.effective_user:
        logger.info(f"User {update.effective_user.id} requested to play stream")
    else:
        logger.info("User requested to play stream (unknown user)")
    if not isinstance(update.message, Message) or update.message.from_user is None:
        return

    user_id = str(update.message.from_user.id)
    args = context.args

    if not args:
        await update.message.reply_text(TRANSLATIONS["playstream_usage"])
        return

    arg = args[0]
    video_url = None
    stream_name = "Stream"

    if arg.startswith(("http://", "https://")):
        video_url = arg
        stream_name = TRANSLATIONS["direct_stream"]
    else:
        try:
            index = int(arg) - 1
            user_streams = load_user_streams()

            if user_id not in user_streams or not user_streams[user_id]:
                await update.message.reply_text(TRANSLATIONS["no_streams_found"])
                return

            if index < 0 or index >= len(user_streams[user_id]):
                await update.message.reply_text(TRANSLATIONS["invalid_number"])
                return

            stream = user_streams[user_id][index]
            video_url = stream.get("url")
            stream_name = stream.get("name", "Stream")
        except ValueError:
            await update.message.reply_text(TRANSLATIONS["invalid_input"])
            return

    if not video_url:
        await update.message.reply_text(TRANSLATIONS["no_url"])
        return

    # Send link
    await update.message.reply_text(
        f"🔗 *{stream_name}*\n\n"
        f"`{video_url}`\n\n"
        f"{TRANSLATIONS['copy_open_vlc']}",
        parse_mode="Markdown",
    )

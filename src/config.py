from persiantools.jdatetime import JalaliDate

# File paths
DB_FILE = 'market_data.db'
EVENTS_FILE = 'events.csv'

# Date scope
START_DATE = JalaliDate(1395, 1, 1)
END_DATE = JalaliDate(1410, 1, 1)

# Market name mappings (English -> Persian)
MARKET_NAMES = {
    "Sandoghe-Aiar": "عیار-مفید",
    "Bourse": "بورس",
    "Fara-Bourse": "فرابورس",
    "Gold": "طلا",
    "Dollar": "دلار",
    "Coin": "سکه امامی",
    "Nim-Coin": "نیم سکه",
    "Coin-Gerami": "سکه گرمی",
    "Bitcoin": "بیت کوین",
    "Rob-Coin": "ربع سکه",
    "Bourse-Khodro": "بورس خودرو",
    "Khesapa": "خساپا",
    "Khodro": "خودرو",
    "Silver": "نقره",
    "Salam": "صندوق سلام",
    "Synergy": "سینرژی",
    "Energy": "انرژی",
}

# Weekday mappings (English -> Persian)
WEEKDAYS = {
    "Shanbeh": "شنبه",
    "Yekshanbeh": "یکشنبه",
    "Doshanbeh": "دوشنبه",
    "Seshanbeh": "سه شنبه",
    "Chaharshanbeh": "چهارشنبه",
    "Panjshanbeh": "پنجشنبه",
    "Jomeh": "جمعه",
}

# Chart colors for each market (Persian names)
COLORS = {
    "بیت کوین": "violet",
    "طلا": "gold",
    "دلار": "green",
    "سکه امامی": "blue",
    "نیم سکه": "purple",
    "ربع سکه": "cyan",
    "سکه گرمی": "pink",
    "بورس": "lime",
    "فرابورس": "salmon",
    "بورس خودرو": "gray",
    "خساپا": "red",
    "خودرو": "pink",
    "عیار-مفید": "black",
    "نقره": "orange",
    "سینرژی": "black",
    "صندوق سلام": "brown",
    "انرژی": "teal",
}

# Season definitions
JALALI_SEASONS = ["بهار", "تابستان", "پاییز", "زمستان"]
GREGORIAN_SEASONS = ["spring", "summer", "autumn", "winter"]


def get_market_persian_name(english_name: str) -> str:
    """Get Persian name for a market, returns 'Unknown' if not found."""
    return MARKET_NAMES.get(str(english_name), "Unknown")


def get_weekday_persian_name(english_name: str) -> str:
    """Get Persian name for a weekday, returns 'Unknown' if not found."""
    return WEEKDAYS.get(str(english_name), "Unknown")

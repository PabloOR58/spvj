"""
Utilidades para procesamiento de precios y conversión de monedas
"""
import re
import pandas as pd
from utils.config import CURRENCY_CONFIG


def convert_to_usd_numeric(price_str):
    """Convierte un string de precio a valor numérico en USD"""
    if pd.isna(price_str) or str(price_str).lower() == "nan":
        return 0.0
    
    p = str(price_str).upper()
    if re.search(r"\b(GRATIS|FREE)\b", p):
        return 0.0
    
    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(',', '.'))
        if not nums:
            return 0.0
        
        val = float(nums[0])
        if val == 0.0:
            return 0.0
        
        rates = {
            "€": 1.08, "฿": 0.028, "РУБ": 0.011, "AED": 0.27,
            "CLP": 0.0011, "CDN$": 0.74, "¥": 0.0067
        }
        for s, r in rates.items():
            if s in p:
                return val * r
        return val
    except:
        return 0.0


def format_local_price(price_str, lang):
    """Formatea un precio según el idioma/moneda"""
    val_usd = convert_to_usd_numeric(price_str)
    
    if val_usd == 0.0:
        from utils.translations import get_translations
        return get_translations(lang)["free_to_play"]
    
    cfg = CURRENCY_CONFIG.get(lang, CURRENCY_CONFIG["en"])
    amount = val_usd * cfg["rate"]
    return f"{cfg['symbol']}{amount:,.2f}"


def format_usd(price_str):
    """Formatea un precio en USD"""
    val = convert_to_usd_numeric(price_str)
    return "Free to Play" if val == 0.0 else f"${round(val, 2)}"

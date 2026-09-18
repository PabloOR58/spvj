"""
Utilidades para procesamiento de datos generales
"""
import pandas as pd
import os
import base64
from utils.config import DATA_FILES, USERS_FILE, FAV_FILE


def init_user_files():
    """Inicializa archivos de usuarios y favoritos si no existen"""
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["username", "password"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(FAV_FILE):
        pd.DataFrame(columns=["username", "appid"]).to_csv(FAV_FILE, index=False)


def fix_nan(val, default="-"):
    """Reemplaza valores NaN con un valor por defecto"""
    if pd.isna(val) or str(val).lower() == "nan" or str(val).strip() == "":
        return default
    return str(val)


def encrypt_password(password):
    """Encripta una contraseña usando base64"""
    if not password:
        return ""
    try:
        password_bytes = password.encode('utf-8')
        encoded_bytes = base64.b64encode(password_bytes)
        return encoded_bytes.decode('utf-8')
    except:
        return password


def decrypt_password(encrypted_password):
    """Desencripta una contraseña desde base64"""
    if not encrypted_password:
        return ""
    try:
        encrypted_bytes = encrypted_password.encode('utf-8')
        decoded_bytes = base64.b64decode(encrypted_bytes)
        return decoded_bytes.decode('utf-8')
    except:
        return encrypted_password


def safe_appid(value):
    """Convierte un valor a AppID de forma segura"""
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return int(float(value))
    except Exception:
        return None


def parse_date_safe(value):
    """Parsea una fecha de forma segura"""
    try:
        if pd.isna(value):
            return pd.NaT
        parsed = pd.to_datetime(value, dayfirst=True, errors='coerce')
        if pd.isna(parsed):
            parsed = pd.to_datetime(value, dayfirst=False, errors='coerce')
        return parsed
    except Exception:
        return pd.NaT


def load_data():
    """Carga todos los dataframes de datos CSV"""
    try:
        df_l = pd.read_csv(DATA_FILES["listado"])
        df_i = pd.read_csv(DATA_FILES["info"])
        df_d = pd.read_csv(DATA_FILES["detalles"], on_bad_lines="skip")
        df_p = pd.read_csv(DATA_FILES["plataformas"])
        
        for df in [df_l, df_i, df_d, df_p]:
            if not df.empty and 'AppID' in df.columns:
                df['AppID'] = pd.to_numeric(df['AppID'], errors='coerce').fillna(0).astype(int)
        
        return df_l, df_i, df_d, df_p
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

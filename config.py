VERSION = "5.0"

# Kendi GitHub repo'nuzun raw versiyon dosyasının URL'sini buraya girin
# Örnek: "https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/refs/heads/main/verison"
VERSION_CHECK_URL = ""

STEAM_APP_LIST_CACHE_FILE = "steam_app_list_cache.json"
STEAM_APP_LIST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}

STEAM_APP_LIST_GITHUB_SOURCES = [
    {
        "name": "github_games",
        "url": "https://raw.githubusercontent.com/jsnli/steamappidlist/refs/heads/master/data/games_appid.json",
        "name_suffix": "",
    },
    {
        "name": "github_dlc",
        "url": "https://raw.githubusercontent.com/jsnli/steamappidlist/refs/heads/master/data/dlc_appid.json",
        "name_suffix": " (DLC)",
    },
]

# Online Fix reponuzun bilgileri — kendi repo'nuzu buraya girin
ONLINEFIX_REPO_OWNER = ""
ONLINEFIX_REPO_NAME = ""
ONLINEFIX_BRANCH = "main"
ONLINEFIX_RAW_BASE = f"https://raw.githubusercontent.com/{ONLINEFIX_REPO_OWNER}/{ONLINEFIX_REPO_NAME}/{ONLINEFIX_BRANCH}" if ONLINEFIX_REPO_OWNER and ONLINEFIX_REPO_NAME else ""
ONLINEFIX_LIST_URL = f"{ONLINEFIX_RAW_BASE}/mevcut%20oyunlar.txt" if ONLINEFIX_RAW_BASE else ""
ONLINEFIX_DOWNLOAD_URL_TEMPLATE = f"{ONLINEFIX_RAW_BASE}/{'{game_id}'}.rar" if ONLINEFIX_RAW_BASE else ""

# ManifestHub repo'sunuzun codeload URL'si — kendi repo'nuzu buraya girin
# Örnek: "https://codeload.github.com/KULLANICI_ADI/REPO_ADI/zip/refs/heads/"
MANIFEST_HUB_BASE_URL = ""

# ManifestHub git refs URL'si (desteklenen oyunları filtrelemek için)
# Örnek: "https://github.com/KULLANICI_ADI/REPO_ADI.git/info/refs?service=git-upload-pack"
MANIFEST_HUB_REFS_URL = ""

# Hakkında sayfasındaki GitHub butonu için link
# Örnek: "https://github.com/KULLANICI_ADI/REPO_ADI"
PROJECT_GITHUB_URL = ""

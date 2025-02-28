from dotenv import load_dotenv, dotenv_values
from http.client import responses
from logging import (
    basicConfig,
    getLogger,
    ERROR,
    INFO,
)
from os import (
    environ,
    path,
    remove,
)
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from requests import get
from subprocess import run


basicConfig(
    format="{asctime} - [{levelname[0]}] {name} [{module}:{lineno}] - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=INFO,
)

LOGGER = getLogger("update")
getLogger("pymongo").setLevel(ERROR)

if path.exists("log.txt"):
    with open("log.txt", "r+") as f:
        f.truncate(0)

if path.exists("rlog.txt"):
    remove("rlog.txt")

if not path.exists("config.env"):
    if CONFIG_URL := environ.get("CONFIG_URL"):
        LOGGER.info("CONFIG_URL is found! Downloading CONFIG_URL...")
        
        req = get(
            url=CONFIG_URL,
            timeout=10,
            allow_redirects=True,
        )
        
        if req.ok:
            with open("config.env", "wb+") as file:
                file.write(req.content)
        
        else:
            LOGGER.error(f"[{req.status_code}] {responses[req.status_code]}")    
    
    else:
        LOGGER.warning("CONFIG_URL is not found! Using local config.env instead...")
            
load_dotenv("config.env", override=True)

if bool(environ.get("_____REMOVE_THIS_LINE_____")):
    LOGGER.error("The README.md file there to be read!")
    exit()

BOT_TOKEN = environ.get("BOT_TOKEN", "")
if len(BOT_TOKEN) == 0:
    LOGGER.error("BOT_TOKEN is not found!")
    exit(1)

BOT_ID = BOT_TOKEN.split(":", 1)[0]

DATABASE_URL = environ.get("DATABASE_URL", "")
if len(DATABASE_URL) == 0:
    DATABASE_URL = None
    LOGGER.warning("DATABASE_URL is not found!")

else:
    try:
        conn = MongoClient(
            DATABASE_URL,
            server_api=ServerApi("1"),
        )

        db = conn.mltb
        old_config = db.settings.deployConfig.find_one({"_id": BOT_ID})
        config_dict = db.settings.config.find_one({"_id": BOT_ID})
        if old_config is not None:
            del old_config["_id"]
        
        if (
            old_config is not None
            and old_config == dict(dotenv_values("config.env"))
            or old_config is None
        ) and config_dict is not None:
            environ["UPSTREAM_REPO"] = config_dict["UPSTREAM_REPO"]
            environ["UPSTREAM_BRANCH"] = config_dict["UPSTREAM_BRANCH"]
        
        conn.close()
    
    except Exception as e:
        LOGGER.error(f"DATABASE ERROR! ERROR: {e}")

UPSTREAM_REPO = environ.get("UPSTREAM_REPO", "")
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = None

else:
    if UPSTREAM_REPO.startswith("#"):
        UPSTREAM_REPO = None

UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH", "")
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = None

else:
    if UPSTREAM_BRANCH.startswith("#"):
        UPSTREAM_BRANCH = None
    
if (
    UPSTREAM_REPO
    and UPSTREAM_BRANCH
):
    if path.exists(".git"):
        run(["rm -rf .git"], shell=True)

    process = run([
        f"git init -q \
        && git config --global user.email kqruumi@gmail.com \
        && git config --global user.name KQRM \
        && git add . \
        && git commit -sm update -q \
        && git remote add origin {UPSTREAM_REPO} \
        && git fetch origin -q \
        && git reset --hard origin/{UPSTREAM_BRANCH} -q"
    ], shell=True)

    if process.returncode == 0:
        LOGGER.info("Successfully updated with latest commit from UPSTREAM_REPO!")
    
    else:
        LOGGER.error("Something wrong while updating! Check UPSTREAM_REPO if valid or not!")

else:
    LOGGER.warning("UPSTREAM_REPO is not found!")
    LOGGER.warning("UPSTREAM_BRANCH is not found!")
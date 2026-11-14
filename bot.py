import os
import threading
from flask import Flask
import re
import math
from datetime import datetime
import requests
import telebot
from telebot.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    KeyboardButton,
    MenuButtonWebApp,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬТЕ_СЮДА_ТОКЕН_ОТ_BOTFATHER")
WEB_APP_URL = os.getenv("WEB_APP_URL", "")
OPENDOTA_API = "https://api.opendota.com/api"
STEAM64_OFFSET = 76561197960265728

MEDALS_RU = {
    1: "Рекрут",
    2: "Страж",
    3: "Рыцарь",
    4: "Герой",
    5: "Легенда",
    6: "Властелин",
    7: "Божество",
    8: "Титан",
}
ROMAN_STARS = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}

HERO_ALIASES = {
    # Strength
    "абаддон": "Abaddon", "аба": "Abaddon", "абба": "Abaddon",
    "алхимик": "Alchemist", "алхим": "Alchemist", "химик": "Alchemist", "alch": "Alchemist",
    "акс": "Axe", "топор": "Axe",
    "бист": "Beastmaster", "бистмастер": "Beastmaster", "рекс": "Beastmaster", "bm": "Beastmaster",
    "брист": "Bristleback", "бристл": "Bristleback", "бристлбэк": "Bristleback", "ежик": "Bristleback", "bb": "Bristleback",
    "кентавр": "Centaur Warrunner", "кент": "Centaur Warrunner", "цент": "Centaur Warrunner",
    "цк": "Chaos Knight", "хаос": "Chaos Knight", "нессаж": "Chaos Knight", "ck": "Chaos Knight",
    "клок": "Clockwerk", "клокверк": "Clockwerk", "консерва": "Clockwerk",
    "дб": "Dawnbreaker", "даунбрейкер": "Dawnbreaker", "валора": "Dawnbreaker",
    "дум": "Doom", "люцифер": "Doom",
    "дк": "Dragon Knight", "дракон": "Dragon Knight", "дэвион": "Dragon Knight", "dk": "Dragon Knight",
    "земеля": "Earth Spirit", "земля": "Earth Spirit", "камень": "Earth Spirit", "kaolin": "Earth Spirit",
    "шейкер": "Earthshaker", "шэйкер": "Earthshaker", "ес": "Earthshaker", "es": "Earthshaker",
    "титан": "Elder Titan", "элдер": "Elder Titan", "ет": "Elder Titan", "et": "Elder Titan",
    "хускар": "Huskar", "хуск": "Huskar",
    "кунка": "Kunkka", "кункка": "Kunkka", "адмирал": "Kunkka", "капитан": "Kunkka",
    "лега": "Legion Commander", "легион": "Legion Commander", "легионка": "Legion Commander", "лк": "Legion Commander", "lc": "Legion Commander",
    "гуля": "Lifestealer", "найкс": "Lifestealer", "лайфстилер": "Lifestealer", "naix": "Lifestealer", "ls": "Lifestealer",
    "ликан": "Lycan", "волк": "Lycan", "люкан": "Lycan",
    "марс": "Mars",
    "нс": "Night Stalker", "баланар": "Night Stalker", "сталкер": "Night Stalker", "ns": "Night Stalker",
    "огр": "Ogre Magi", "огрик": "Ogre Magi", "ogre": "Ogre Magi",
    "омник": "Omniknight", "омни": "Omniknight", "паладин": "Omniknight", "omni": "Omniknight",
    "феникс": "Phoenix", "икар": "Phoenix",
    "праймал": "Primal Beast", "динозавр": "Primal Beast", "зверь": "Primal Beast", "pb": "Primal Beast",
    "пудж": "Pudge", "падж": "Pudge", "мясник": "Pudge", "буч": "Pudge",
    "слардар": "Slardar", "селедка": "Slardar", "селёдка": "Slardar", "рыба": "Slardar",
    "бара": "Spirit Breaker", "баратрум": "Spirit Breaker", "корова": "Spirit Breaker", "бычок": "Spirit Breaker", "sb": "Spirit Breaker",
    "свен": "Sven", "свена": "Sven",
    "тайд": "Tidehunter", "тайдхантер": "Tidehunter", "арбуз": "Tidehunter", "левиафан": "Tidehunter", "tide": "Tidehunter",
    "тимбер": "Timbersaw", "пила": "Timbersaw", "риззрак": "Timbersaw", "timber": "Timbersaw",
    "тини": "Tiny", "тоня": "Tiny",
    "трент": "Treant Protector", "дерево": "Treant Protector", "пень": "Treant Protector", "tree": "Treant Protector",
    "таск": "Tusk", "туск": "Tusk", "тускар": "Tusk", "морж": "Tusk",
    "андерлорд": "Underlord", "питлорд": "Underlord", "питка": "Underlord", "азгалор": "Underlord", "ul": "Underlord",
    "зомби": "Undying", "андаинг": "Undying", "дирж": "Undying",
    "вк": "Wraith King", "папич": "Wraith King", "леорик": "Wraith King", "скелет": "Wraith King", "wk": "Wraith King",
    # Agility
    "ам": "Anti-Mage", "антимаг": "Anti-Mage", "анти-маг": "Anti-Mage", "магина": "Anti-Mage", "am": "Anti-Mage",
    "арк": "Arc Warden", "варден": "Arc Warden", "зет": "Arc Warden", "aw": "Arc Warden",
    "бс": "Bloodseeker", "сикер": "Bloodseeker", "бладсикер": "Bloodseeker", "стригвир": "Bloodseeker", "bs": "Bloodseeker",
    "бх": "Bounty Hunter", "баунти": "Bounty Hunter", "гондар": "Bounty Hunter", "bh": "Bounty Hunter",
    "клинкз": "Clinkz", "боник": "Clinkz",
    "дровка": "Drow Ranger", "тракса": "Drow Ranger", "тракс": "Drow Ranger", "дров": "Drow Ranger", "traxa": "Drow Ranger", "dr": "Drow Ranger",
    "эмбер": "Ember Spirit", "ембер": "Ember Spirit", "ксин": "Ember Spirit",
    "войд": "Faceless Void", "безликий": "Faceless Void", "fv": "Faceless Void",
    "гиро": "Gyrocopter", "гирокоптер": "Gyrocopter", "вертолет": "Gyrocopter", "gyro": "Gyrocopter",
    "белка": "Hoodwink", "худвинк": "Hoodwink", "хв": "Hoodwink", "hw": "Hoodwink",
    "джага": "Juggernaut", "джагер": "Juggernaut", "джаггернаут": "Juggernaut", "юреро": "Juggernaut", "jugg": "Juggernaut",
    "кез": "Kez",
    "лд": "Lone Druid", "друид": "Lone Druid", "медведь": "Lone Druid", "силлабир": "Lone Druid", "ld": "Lone Druid",
    "луна": "Luna", "муна": "Luna",
    "медуза": "Medusa", "дуза": "Medusa", "горгона": "Medusa", "dusa": "Medusa",
    "мипо": "Meepo", "мипарь": "Meepo", "геомансер": "Meepo",
    "мирана": "Mirana", "потма": "Mirana", "potm": "Mirana",
    "мк": "Monkey King", "макака": "Monkey King", "обезьяна": "Monkey King", "mk": "Monkey King",
    "морф": "Morphling", "морфлинг": "Morphling", "вода": "Morphling", "morph": "Morphling",
    "нага": "Naga Siren", "сирена": "Naga Siren",
    "па": "Phantom Assassin", "фантомка": "Phantom Assassin", "мортра": "Phantom Assassin", "мортред": "Phantom Assassin", "pa": "Phantom Assassin",
    "пл": "Phantom Lancer", "лансер": "Phantom Lancer", "азвраф": "Phantom Lancer", "pl": "Phantom Lancer",
    "разор": "Razor", "рейзор": "Razor",
    "рики": "Riki", "рике": "Riki", "рикимару": "Riki",
    "сф": "Shadow Fiend", "финд": "Shadow Fiend", "невер": "Shadow Fiend", "невермор": "Shadow Fiend", "sf": "Shadow Fiend",
    "сларк": "Slark", "жаба": "Slark", "мурлок": "Slark",
    "снайпер": "Sniper", "кардел": "Sniper",
    "спектра": "Spectre", "меркуриал": "Spectre", "spec": "Spectre",
    "та": "Templar Assassin", "ланая": "Templar Assassin", "темпларка": "Templar Assassin", "ta": "Templar Assassin",
    "тб": "Terrorblade", "террор": "Terrorblade", "террорблейд": "Terrorblade", "иллидан": "Terrorblade", "tb": "Terrorblade",
    "тролль": "Troll Warlord", "троль": "Troll Warlord", "джаракал": "Troll Warlord", "troll": "Troll Warlord",
    "урса": "Ursa", "мишка": "Ursa", "ульфсаар": "Ursa",
    "венга": "Vengeful Spirit", "венджа": "Vengeful Spirit", "шендель": "Vengeful Spirit", "vs": "Vengeful Spirit",
    "вайпер": "Viper", "випер": "Viper", "змей": "Viper",
    "вивер": "Weaver", "жук": "Weaver", "таракан": "Weaver",
    # Intelligence
    "аа": "Ancient Apparition", "аппарат": "Ancient Apparition", "кальдр": "Ancient Apparition", "aa": "Ancient Apparition",
    "бэйн": "Bane", "бейн": "Bane",
    "бэт": "Batrider", "бэтрайдер": "Batrider", "bat": "Batrider",
    "чен": "Chen",
    "цм": "Crystal Maiden", "цмка": "Crystal Maiden", "рилай": "Crystal Maiden", "кристалка": "Crystal Maiden", "cm": "Crystal Maiden",
    "дс": "Dark Seer", "сир": "Dark Seer", "ds": "Dark Seer",
    "вилка": "Dark Willow", "виллоу": "Dark Willow", "фейка": "Dark Willow", "dw": "Dark Willow",
    "дазл": "Dazzle", "даззл": "Dazzle",
    "дп": "Death Prophet", "баньша": "Death Prophet", "кроба": "Death Prophet", "профетка": "Death Prophet", "dp": "Death Prophet",
    "дизраптор": "Disruptor", "тралл": "Disruptor", "диз": "Disruptor",
    "энча": "Enchantress", "коза": "Enchantress", "инча": "Enchantress", "ench": "Enchantress",
    "энигма": "Enigma", "енигма": "Enigma",
    "грим": "Grimstroke", "гримстрок": "Grimstroke",
    "инвокер": "Invoker", "вокер": "Invoker", "карл": "Invoker", "voker": "Invoker",
    "джакиро": "Jakiro", "тхд": "Jakiro", "драконы": "Jakiro", "thd": "Jakiro",
    "котл": "Keeper of the Light", "кипер": "Keeper of the Light", "эзалор": "Keeper of the Light", "kotl": "Keeper of the Light",
    "лешрак": "Leshrac", "леший": "Leshrac", "леш": "Leshrac",
    "лич": "Lich", "этриан": "Lich",
    "лина": "Lina",
    "лион": "Lion", "палец": "Lion",
    "муэрта": "Muerta", "муерта": "Muerta",
    "некр": "Necrophos", "некрофос": "Necrophos", "некролит": "Necrophos", "necro": "Necrophos",
    "оракл": "Oracle", "оракул": "Oracle",
    "од": "Outworld Destroyer", "дестр": "Outworld Destroyer", "аутворлд": "Outworld Destroyer", "харбингер": "Outworld Destroyer", "od": "Outworld Destroyer",
    "пак": "Puck", "бабочка": "Puck",
    "пугна": "Pugna",
    "квопа": "Queen of Pain", "акаша": "Queen of Pain", "королева": "Queen of Pain", "qop": "Queen of Pain",
    "рингмастер": "Ringmaster", "клоун": "Ringmaster", "циркач": "Ringmaster",
    "рубик": "Rubick",
    "шд": "Shadow Demon", "сд": "Shadow Demon", "sd": "Shadow Demon",
    "шаман": "Shadow Shaman", "раста": "Shadow Shaman", "рашта": "Shadow Shaman", "ss": "Shadow Shaman",
    "сало": "Silencer", "сайленсер": "Silencer", "нортром": "Silencer",
    "скай": "Skywrath Mage", "скаймаг": "Skywrath Mage", "петух": "Skywrath Mage", "sky": "Skywrath Mage",
    "шторм": "Storm Spirit", "райжин": "Storm Spirit", "storm": "Storm Spirit",
    "тинкер": "Tinker", "боуш": "Tinker", "буш": "Tinker",
    "варлок": "Warlock", "чернокнижник": "Warlock",
    "вд": "Witch Doctor", "доктор": "Witch Doctor", "вичка": "Witch Doctor", "wd": "Witch Doctor",
    "виверна": "Winter Wyvern", "вв": "Winter Wyvern", "ww": "Winter Wyvern",
    "зевс": "Zeus",
    # Universal
    "брю": "Brewmaster", "брюмастер": "Brewmaster", "пивовар": "Brewmaster", "панда": "Brewmaster", "brew": "Brewmaster",
    "бруда": "Broodmother", "паук": "Broodmother", "паучиха": "Broodmother",
    "висп": "Io", "ио": "Io", "шарик": "Io", "wisp": "Io",
    "магнус": "Magnus", "магнатавр": "Magnus",
    "марси": "Marci",
    "фура": "Nature's Prophet", "фурион": "Nature's Prophet", "профет": "Nature's Prophet", "np": "Nature's Prophet", "furion": "Nature's Prophet",
    "никс": "Nyx Assassin", "нюкс": "Nyx Assassin", "nyx": "Nyx Assassin",
    "панго": "Pangolier", "пангольер": "Pangolier", "броненосец": "Pangolier", "pango": "Pangolier",
    "ск": "Sand King", "песок": "Sand King", "скорпион": "Sand King", "sk": "Sand King",
    "бабка": "Snapfire", "снапа": "Snapfire", "снапфаер": "Snapfire",
    "течис": "Techies", "минер": "Techies", "минёр": "Techies", "бомбер": "Techies",
    "вено": "Venomancer", "веник": "Venomancer", "веномансер": "Venomancer",
    "визаж": "Visage", "птицы": "Visage",
    "войд спирит": "Void Spirit", "инай": "Void Spirit",
    "вр": "Windranger", "врка": "Windranger", "винда": "Windranger", "виндраннер": "Windranger", "wr": "Windranger",
}

ALIASES_BY_HERO = {}
for _al, _hero_en in HERO_ALIASES.items():
    ALIASES_BY_HERO.setdefault(_hero_en.lower(), []).append(_al)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
http = requests.Session()
http.headers.update({"User-Agent": "Dota2HeroRankerBot/3.0"})
_heroes_cache = None


def register_slash_commands():
    """Регистрирует список команд в Telegram и синюю кнопку Mini App в меню."""
    commands = [
        BotCommand("start", "Инструкция, Mini App и тестовые примеры"),
        BotCommand("commands", "Полный список всех команд бота"),
        BotCommand("app", "Открыть визуальное приложение (Mini App)"),
        BotCommand("profile", "Полное досье: MMR, WR, роли, Топ-8, контрпики"),
        BotCommand("matches", "Последние 10 матчей с GPM/XPM и уроном"),
        BotCommand("match", "Разбор матча 5x5 (Radiant vs Dire): /match <ID>"),
        BotCommand("records", "Личные рекорды и неудобные герои: /records <ID>"),
        BotCommand("compare", "Сравнение 2 игроков: /compare <ID1> <ID2>"),
        BotCommand("rank", "Место на герое и разбор очков: /rank <ID> <Герой>"),
        BotCommand("top", "Топ-15 игроков мира на герое: /top <Герой>"),
        BotCommand("meta", "Мета текущего патча (Божество/Титан + Про)"),
        BotCommand("hero", "Автоподбор героя по буквам: /hero <буквы>"),
        BotCommand("aliases", "Шпаргалка русских сленговых названий"),
        BotCommand("help", "Справка по командам и форматам ID"),
    ]
    bot.set_my_commands(commands)
    if WEB_APP_URL.startswith("https://"):
        bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                type="web_app",
                text="Карманный Dotabuff",
                web_app=WebAppInfo(url=WEB_APP_URL),
            )
        )


DIV = "━━━━━━━━━━━━━━━━━━━━"


def render_bar(percent: float, width: int = 8) -> str:
    clamped = max(0.0, min(100.0, float(percent)))
    filled = round((clamped / 100.0) * width)
    return "█" * filled + "░" * max(0, width - filled)


def format_clock(seconds: int) -> str:
    s = max(0, int(seconds or 0))
    return f"{s // 60}:{s % 60:02d}"


def get_heroes():
    global _heroes_cache
    if _heroes_cache is None:
        resp = http.get(f"{OPENDOTA_API}/heroStats", timeout=15)
        resp.raise_for_status()
        _heroes_cache = resp.json()
    return _heroes_cache


def get_aliases_for_hero(localized_name: str):
    return ALIASES_BY_HERO.get(localized_name.lower(), [])


def suggest_heroes(query: str, limit: int = 6):
    """Автоподбор подходящих героев по первым или ключевым буквам / аббревиатурам."""
    q = query.strip().lower()
    if not q:
        return []
    heroes = get_heroes()
    exact_alias = HERO_ALIASES.get(q, "").lower()
    scored = []
    for h in heroes:
        en = h["localized_name"].lower()
        slug = h["name"].replace("npc_dota_hero_", "").replace("_", " ").lower()
        aliases = get_aliases_for_hero(h["localized_name"])
        matched_al = [a for a in aliases if a == q or a.startswith(q) or q in a]
        score = 0
        if en == q or slug == q or exact_alias == en:
            score = 100
        elif en.startswith(q) or slug.startswith(q) or any(a.startswith(q) for a in aliases):
            score = 85
        else:
            words = [w for w in re.split(r"[\s'-]+", en) if w]
            initials = "".join(w[0] for w in words)
            if initials == q or any(w.startswith(q) for w in words):
                score = 72
            elif q in en or q in slug or matched_al:
                score = 55
            elif len(q) >= 3 and any(a in q for a in aliases):
                score = 45
        if score > 0:
            scored.append((score, h.get("pub_pick", 0), h, matched_al or aliases[:3]))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [(item[2], item[3]) for item in scored[:limit]]


def find_hero(query: str):
    q = query.strip().lower()
    heroes = get_heroes()
    target_name = HERO_ALIASES.get(q, q).lower()
    for h in heroes:
        if h["localized_name"].lower() == target_name:
            return h
    for h in heroes:
        if h["localized_name"].lower().startswith(target_name) or any(
            a.startswith(q) for a in get_aliases_for_hero(h["localized_name"])
        ):
            return h
    for h in heroes:
        if target_name in h["localized_name"].lower():
            return h
    for ru_key, en_name in HERO_ALIASES.items():
        if q in ru_key or (len(q) >= 3 and ru_key in q):
            for h in heroes:
                if h["localized_name"].lower() == en_name.lower():
                    return h
    return None


def parse_account_id(raw: str):
    """Извлекает 32-bit account_id из Friend ID, SteamID64 или ссылки Dotabuff/OpenDota/Stratz/Steam."""
    cleaned = raw.strip()
    url_match = re.search(
        r"(?:dotabuff|opendota|stratz)\.com/players/(\d+)|steamcommunity\.com/profiles/(\d{17})",
        cleaned,
        re.IGNORECASE,
    )
    if url_match:
        cleaned = url_match.group(1) or url_match.group(2)
    if not cleaned.isdigit():
        return None
    val = int(cleaned)
    return val - STEAM64_OFFSET if val >= STEAM64_OFFSET else val


def format_rank_tier(rank_tier, leaderboard_rank=None):
    if not rank_tier or rank_tier < 10:
        return "Без ранга", 2200
    medal = min(8, rank_tier // 10)
    star = min(5, max(1, rank_tier % 10))
    if medal == 8:
        label = f"Титан #{leaderboard_rank:,}".replace(",", " ") if leaderboard_rank else "Титан"
        mmr = max(6000, 9200 - leaderboard_rank * 2) if leaderboard_rank and leaderboard_rank <= 1000 else 6800
        return label, mmr
    base_mmr = [2200, 150, 850, 1600, 2350, 3100, 3850, 4650, 5800]
    approx_mmr = base_mmr[medal] + (star - 1) * 155
    return f"{MEDALS_RU.get(medal, '')} {ROMAN_STARS.get(star, '')}".strip(), approx_mmr


def build_profile_keyboard(account_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("OpenDota", url=f"https://www.opendota.com/players/{account_id}"),
        InlineKeyboardButton("Dotabuff", url=f"https://www.dotabuff.com/players/{account_id}"),
        InlineKeyboardButton("Steam", url=f"https://steamcommunity.com/profiles/{account_id + STEAM64_OFFSET}"),
    )
    return kb


def build_score_breakdown(final_score: float, games: int, wins: int, approx_mmr: int, rank_label: str, is_estimated: bool):
    if games == 0:
        mmr_pts = round(approx_mmr * 0.45, 1)
        return [(f"База от ранга ({rank_label})", mmr_pts, "Стартовая оценка без сыгранных матчей")]

    winrate = wins / games
    confidence = 1.0 - math.exp(-games / 22.0)
    mmr_pts = round(1900.0 + approx_mmr * 0.62, 1)
    wr_pts = round((winrate - 0.5) * 2600.0 * confidence, 1)
    vol_pts = round(min(1250.0, math.log10(games + 1) * 430.0), 1)

    items = [
        (f"База от ранга ({rank_label})", mmr_pts, f"опора ~{approx_mmr} MMR"),
        (f"Винрейт ({round(winrate * 100, 1)}%)", wr_pts, f"{wins}W–{games - wins}L"),
        (f"Опыт на герое ({games} игр)", vol_pts, "бонус за дистанцию"),
    ]
    delta = round(final_score - (mmr_pts + wr_pts + vol_pts), 1)
    if not is_estimated:
        items.append(("Калибровка OpenDota и лобби", delta, "уровень соперников, KDA и серии"))
    return items


def fetch_player_full_bundle(account_id: int, include_extended: bool = False):
    profile = http.get(f"{OPENDOTA_API}/players/{account_id}", timeout=15).json()
    if not profile or not profile.get("profile"):
        return None
    wl = http.get(f"{OPENDOTA_API}/players/{account_id}/wl", timeout=15).json()
    rankings = http.get(f"{OPENDOTA_API}/players/{account_id}/rankings", timeout=15).json()
    heroes = http.get(f"{OPENDOTA_API}/players/{account_id}/heroes", timeout=15).json()
    recent = http.get(f"{OPENDOTA_API}/players/{account_id}/recentMatches", timeout=15).json()

    totals = []
    counts = {}
    peers = []
    if include_extended:
        try:
            totals = http.get(f"{OPENDOTA_API}/players/{account_id}/totals", timeout=15).json()
        except Exception:
            totals = []
        try:
            counts = http.get(f"{OPENDOTA_API}/players/{account_id}/counts", timeout=15).json()
        except Exception:
            counts = {}
        try:
            peers = http.get(f"{OPENDOTA_API}/players/{account_id}/peers", timeout=15).json()
        except Exception:
            peers = []

    return {
        "profile": profile,
        "wl": wl if isinstance(wl, dict) else {},
        "rankings": rankings if isinstance(rankings, list) else [],
        "heroes": heroes if isinstance(heroes, list) else [],
        "recent": recent if isinstance(recent, list) else [],
        "totals": totals if isinstance(totals, list) else [],
        "counts": counts if isinstance(counts, dict) else {},
        "peers": peers if isinstance(peers, list) else [],
    }


def send_avatar_and_details(chat_id: int, avatar_url: str, caption: str, details: str, account_id: int):
    kb = build_profile_keyboard(account_id)
    if avatar_url:
        try:
            bot.send_photo(chat_id, avatar_url, caption=caption[:1024], reply_markup=kb)
            if details:
                bot.send_message(chat_id, details, disable_web_page_preview=True)
            return
        except Exception:
            pass
    bot.send_message(chat_id, f"{caption}\n\n{details}".strip(), reply_markup=kb, disable_web_page_preview=True)


# Нативное автозаполнение в Telegram при вводе '@имя_бота <буквы>'
@bot.inline_handler(lambda query: True)
def handle_inline_hero_autocomplete(inline_query):
    q = inline_query.query.strip()
    matches = suggest_heroes(q or "pudge", limit=8)
    results = []
    for idx, (hero, aliases) in enumerate(matches):
        al_text = f" ({', '.join(aliases[:4])})" if aliases else ""
        results.append(
            InlineQueryResultArticle(
                id=f"hero_{hero['id']}_{idx}",
                title=f"{hero['localized_name']}{al_text}",
                description=f"Топ-15 мира и команда /top {hero['localized_name']}",
                input_message_content=InputTextMessageContent(f"/top {hero['localized_name']}"),
            )
        )
    bot.answer_inline_query(inline_query.id, results, cache_time=60)


def build_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Постоянная нижняя клавиатура Telegram — работает даже когда кнопка меню занята Mini App."""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
    app_btn = (
        KeyboardButton("📱 Открыть Mini App", web_app=WebAppInfo(url=WEB_APP_URL))
        if WEB_APP_URL.startswith("https://")
        else KeyboardButton("📱 Открыть Mini App")
    )
    kb.row(KeyboardButton("📋 Список команд"), app_btn)
    kb.row(KeyboardButton("📊 Мета патча"), KeyboardButton("🎭 Сленг героев"), KeyboardButton("🚀 Старт"))
    return kb


def build_commands_text() -> str:
    return (
        "<b>Все команды бота (доступны в любое время)</b>\n"
        f"{DIV}\n"
        "Поскольку левая синяя кнопка меню открывает Mini App, используйте <code>/commands</code>, "
        "постоянную кнопку <b>«📋 Список команд»</b> под строкой ввода или ввод слэша <code>/</code>:\n\n"
        "<b>Профиль и матчи:</b>\n"
        "• <code>/app</code> — открыть графический Telegram Mini App\n"
        "• <code>/profile &lt;ID&gt;</code> — полное досье (аватар, MMR, WR, стороны, роли, KDA/GPM/XPM, Топ-8 героев, тиммейты)\n"
        "• <code>/matches &lt;ID&gt;</code> — последние 10 матчей + кнопки разбора 5×5\n"
        "• <code>/match &lt;Match_ID&gt;</code> — таблица всех 10 игроков (Radiant vs Dire)\n"
        "• <code>/records &lt;ID&gt;</code> — личные рекорды и неудобные герои против\n"
        "• <code>/compare &lt;ID1&gt; &lt;ID2&gt;</code> — сравнение 2 игроков лоб в лоб\n\n"
        "<b>Рейтинг и мета:</b>\n"
        "• <code>/rank &lt;ID&gt; &lt;Герой&gt;</code> — место в мире, разбор Hero Score и матчи\n"
        "• <code>/top &lt;Герой&gt;</code> — Топ-15 игроков мира · <code>/meta</code> — мета патча\n"
        "• <code>/hero &lt;буквы&gt;</code> — автоподбор (250+ сленговых названий) · <code>/aliases</code>\n\n"
        "<b>Служебные:</b>\n"
        "• <code>/start</code> — инструкция и стартовое меню · <code>/commands</code> — этот список"
    )


@bot.message_handler(commands=["commands", "menu"])
def handle_commands_list(message):
    kb = InlineKeyboardMarkup(row_width=1)
    if WEB_APP_URL.startswith("https://"):
        kb.add(InlineKeyboardButton("📱 Открыть Карманный Dotabuff (Mini App)", web_app=WebAppInfo(url=WEB_APP_URL)))
    kb.add(
        InlineKeyboardButton("🧪 Тест (пример): Досье Arteezy", callback_data="demo_profile:86745912"),
        InlineKeyboardButton("🧪 Тест (пример): Матчи Arteezy", callback_data="demo_matches:86745912"),
        InlineKeyboardButton("🧪 Тест (пример): Arteezy на Terrorblade", callback_data="demo_rank:86745912:109"),
        InlineKeyboardButton("📊 Мета текущего патча (/meta)", callback_data="demo_meta"),
        InlineKeyboardButton("🎭 Шпаргалка сленга (/aliases)", callback_data="demo_aliases"),
    )
    bot.send_message(message.chat.id, build_commands_text(), reply_markup=kb)


@bot.message_handler(commands=["app"])
def handle_app(message):
    if not WEB_APP_URL.startswith("https://"):
        bot.reply_to(
            message,
            "Чтобы кнопка Mini App открывалась в Telegram, запустите бота с HTTPS-ссылкой:\n"
            '<code>WEB_APP_URL="https://ваш-домен/?miniapp=1" python dota_rank_bot.py</code>',
        )
        return
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            "📱 Открыть Карманный Dotabuff (Mini App)",
            web_app=WebAppInfo(url=WEB_APP_URL),
        ),
        InlineKeyboardButton("📋 Показать список команд (/commands)", callback_data="demo_commands"),
    )
    bot.reply_to(
        message,
        "<b>Карманный Dotabuff Mini App</b>\nНажмите кнопку ниже, чтобы открыть графическое приложение прямо поверх чата:",
        reply_markup=kb,
    )


@bot.message_handler(content_types=["web_app_data"])
def handle_web_app_data(message):
    import json
    try:
        payload = json.loads(message.web_app_data.data)
        summary = payload.get("summary") or str(payload)
        bot.send_message(message.chat.id, f"<b>Сводка из Mini App:</b>\n{DIV}\n{summary}")
    except Exception:
        bot.send_message(message.chat.id, message.web_app_data.data)


@bot.message_handler(commands=["start", "help"])
def handle_start(message):
    text = (
        "<b>Карманный Dotabuff + Dota 2 Hero Ranker</b>\n"
        f"{DIV}\n"
        "Полная статистика игрока, разбор матчей 5×5, рекорды, сравнение профилей, мета патча и расчёт точного места по герою.\n\n"
        "<b>Инструкция по запуску:</b>\n"
        "1. Скопируйте свой <b>Friend ID</b> (8–10 цифр) в профиле Dota 2 или ссылку <b>Dotabuff / OpenDota / Stratz / Steam</b>.\n"
        "2. В настройках Dota 2 включите <i>«Общедоступная история матчей»</i>.\n"
        "3. Откройте Mini App кнопкой ниже или используйте команды (всегда доступны по кнопке <b>«📋 Список команд»</b> и команде <code>/commands</code>):\n\n"
        "<b>Основные команды:</b>\n"
        "• <code>/app</code> — графический Telegram Mini App\n"
        "• <code>/commands</code> — полный список всех команд и подсказок\n"
        "• <code>/profile &lt;ID&gt;</code> — полное досье (MMR, WR, роли, Топ-8, тиммейты)\n"
        "• <code>/matches &lt;ID&gt;</code> · <code>/match &lt;Match_ID&gt;</code> — матчи и разбор 5×5\n"
        "• <code>/rank &lt;ID&gt; &lt;Герой&gt;</code> · <code>/top &lt;Герой&gt;</code> — место на герое и Топ-15\n"
        "• <code>/records &lt;ID&gt;</code> · <code>/compare &lt;ID1&gt; &lt;ID2&gt;</code> · <code>/meta</code>\n"
        "• <code>/hero &lt;буквы&gt;</code> · <code>/aliases</code> — автоподбор по 250+ сленговым названиям\n\n"
        "<i>Внимание: кнопки ниже помечены как «🧪 Тест (пример)» — они открывают демо-данные публичных про-игроков для проверки бота.</i>"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    if WEB_APP_URL.startswith("https://"):
        kb.add(
            InlineKeyboardButton(
                "📱 Открыть Карманный Dotabuff (Mini App)",
                web_app=WebAppInfo(url=WEB_APP_URL),
            )
        )
    kb.add(
        InlineKeyboardButton("📋 Список всех команд (/commands)", callback_data="demo_commands"),
        InlineKeyboardButton("🧪 Тест (пример): Досье Arteezy", callback_data="demo_profile:86745912"),
        InlineKeyboardButton("🧪 Тест (пример): Матчи Arteezy", callback_data="demo_matches:86745912"),
        InlineKeyboardButton("🧪 Тест (пример): Arteezy на Terrorblade", callback_data="demo_rank:86745912:109"),
        InlineKeyboardButton("🧪 Тест (пример): Рекорды Arteezy", callback_data="demo_records:86745912"),
        InlineKeyboardButton("🧪 Тест (пример): Сравнить Arteezy и Miracle-", callback_data="demo_compare:86745912:105248644"),
        InlineKeyboardButton("📊 Мета текущего патча (/meta)", callback_data="demo_meta"),
    )
    # 1) Закрепляем постоянную нижнюю клавиатуру команд
    bot.send_message(
        message.chat.id,
        "Панель быстрого доступа к командам закреплена внизу экрана 👇",
        reply_markup=build_main_reply_keyboard(),
    )
    # 2) Отправляем приветственную карточку и тестовые кнопки
    bot.send_message(message.chat.id, text, reply_markup=kb)


@bot.message_handler(commands=["aliases"])
def handle_aliases(message):
    text = (
        "<b>Шпаргалка аналогов героев (поддерживается 250+ вариантов):</b>\n\n"
        "<b>Керри:</b>\n"
        "• Terrorblade — тб, террор, иллидан\n"
        "• Shadow Fiend — сф, финд, невер, sf\n"
        "• Drow Ranger — дровка, тракса, traxa\n"
        "• Phantom Assassin — па, фантомка, мортра\n"
        "• Anti-Mage — ам, антимаг, магина\n"
        "• Lifestealer — гуля, найкс, naix\n"
        "• Templar Assassin — та, ланая, темпларка\n\n"
        "<b>Силовики / Инициаторы:</b>\n"
        "• Pudge — пудж, падж, мясник, буч\n"
        "• Spirit Breaker — бара, баратрум, корова, бычок\n"
        "• Slardar — слардар, селедка, рыба\n"
        "• Wraith King — вк, папич, леорик\n"
        "• Timbersaw — тимбер, пила, риззрак\n\n"
        "<b>Маги / Саппорты:</b>\n"
        "• Invoker — инвокер, вокер, карл\n"
        "• Outworld Destroyer — од, дестр, харбингер\n"
        "• Keeper of the Light — котл, кипер, эзалор\n"
        "• Nature's Prophet — фура, фурион, пень\n"
        "• Silencer — сало, нортром · Hoodwink — белка · Snapfire — бабка\n\n"
        "Используйте <code>/hero &lt;буквы&gt;</code> для поиска или выбора кнопками!"
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=["hero", "heroes"])
def handle_hero_suggest(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Введите первые буквы героя: <code>/hero &lt;буквы&gt;</code>\nПример: <code>/hero тракс</code>")
        return
    send_hero_suggestions(message.chat.id, parts[1])


def send_hero_suggestions(chat_id: int, query: str, account_id: int = None):
    matches = suggest_heroes(query, limit=6)
    if not matches:
        bot.send_message(chat_id, f"По запросу «{query}» герои не найдены. Посмотрите <code>/aliases</code>.")
        return
    lines = [f"<b>Варианты автодополнения для «{query}»:</b>"]
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for hero, aliases in matches:
        al_str = f" ({', '.join(aliases[:3])})" if aliases else ""
        lines.append(f"• <b>{hero['localized_name']}</b>{al_str}")
        cb = f"pick_rank:{account_id}:{hero['id']}" if account_id else f"pick_top:{hero['id']}"
        buttons.append(InlineKeyboardButton(hero["localized_name"], callback_data=cb))
    kb.add(*buttons)
    bot.send_message(chat_id, "\n".join(lines), reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith(("demo_", "pick_")))
def handle_callbacks(call):
    bot.answer_callback_query(call.id)
    parts = call.data.split(":")
    action = parts[0]
    if action == "demo_commands":
        handle_commands_list(call.message)
    elif action == "demo_aliases":
        handle_aliases(call.message)
    elif action == "demo_meta":
        process_meta(call.message.chat.id)
    elif action == "demo_hero":
        send_hero_suggestions(call.message.chat.id, parts[1])
    elif action == "demo_profile":
        process_profile(call.message.chat.id, parts[1])
    elif action == "demo_matches":
        process_matches(call.message.chat.id, parts[1])
    elif action == "demo_match":
        process_match(call.message.chat.id, int(parts[1]))
    elif action == "demo_records":
        process_records(call.message.chat.id, parts[1])
    elif action == "demo_compare":
        process_compare(call.message.chat.id, parts[1], parts[2])
    elif action in ("demo_rank", "pick_rank"):
        heroes = {h["id"]: h for h in get_heroes()}
        hero = heroes.get(int(parts[2]))
        if hero:
            process_rank(call.message.chat.id, parts[1], hero["localized_name"])
    elif action == "pick_top":
        heroes = {h["id"]: h for h in get_heroes()}
        hero = heroes.get(int(parts[1]))
        if hero:
            process_top(call.message.chat.id, hero["localized_name"])


@bot.message_handler(commands=["profile"])
def handle_profile(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: <code>/profile &lt;Steam_ID_или_ссылка&gt;</code>\nПример: <code>/profile 86745912</code>")
        return
    process_profile(message.chat.id, parts[1])


def process_profile(chat_id: int, raw_id: str):
    account_id = parse_account_id(raw_id)
    if not account_id:
        bot.send_message(chat_id, "Не удалось распознать Steam ID или ссылку на профиль.")
        return

    bundle = fetch_player_full_bundle(account_id, include_extended=True)
    if not bundle:
        bot.send_message(chat_id, "Профиль не найден или скрыт настройками приватности Dota 2.")
        return

    prof = bundle["profile"]
    p_info = prof["profile"]
    name = p_info.get("personaname") or f"Player {account_id}"
    avatar = p_info.get("avatarfull") or ""
    steamid64 = p_info.get("steamid") or str(account_id + STEAM64_OFFSET)
    flags = [
        f for f in [
            p_info.get("loccountrycode"),
            "Dota Plus" if p_info.get("plus") else None,
            "OpenDota Contributor" if p_info.get("is_contributor") else None,
        ] if f
    ]

    rank_label, approx_mmr = format_rank_tier(prof.get("rank_tier"), prof.get("leaderboard_rank"))
    est_mmr = (prof.get("mmr_estimate") or {}).get("estimate") or approx_mmr

    total_win = bundle["wl"].get("win", 0)
    total_lose = bundle["wl"].get("lose", 0)
    total_games = total_win + total_lose
    total_wr = round((total_win / total_games) * 100, 1) if total_games > 0 else 0.0

    heroes_map = {h["id"]: h for h in get_heroes()}
    stat_map = {int(h["hero_id"]): h for h in bundle["heroes"]}

    caption = (
        f"<b>{name}</b>" + (f" ({' · '.join(flags)})" if flags else "") + "\n"
        f"Friend ID: <code>{account_id}</code> · SteamID64: <code>{steamid64}</code>\n"
        f"Ранг: <b>{rank_label}</b> · Оценка MMR: <b>~{est_mmr}</b>\n"
        f"Всего матчей: <b>{total_games:,}</b> ({total_win}W – {total_lose}L · {total_wr}%)"
    ).replace(",", " ")

    lines = []
    counts = bundle.get("counts") or {}
    if counts:
        ranked = (counts.get("lobby_type") or {}).get("7", {})
        rad = (counts.get("is_radiant") or {}).get("1", {})
        dire = (counts.get("is_radiant") or {}).get("0", {})
        parts_line = []
        if ranked.get("games", 0) > 0:
            r_wr = round((ranked["win"] / ranked["games"]) * 100, 1)
            parts_line.append(f"Рейтинг: <b>{ranked['games']}</b> игр ({r_wr}%)")
        if rad.get("games", 0) > 0 and dire.get("games", 0) > 0:
            rad_wr = round((rad["win"] / rad["games"]) * 100, 1)
            dire_wr = round((dire["win"] / dire["games"]) * 100, 1)
            parts_line.append(f"Свет: {rad_wr}% · Тьма: {dire_wr}%")
        if parts_line:
            lines.append(" | ".join(parts_line))

        lane_names = {"1": "Керри", "2": "Мид", "3": "Оффлейн", "4": "Лес"}
        lanes = [
            (k, v) for k, v in (counts.get("lane_role") or {}).items()
            if k in lane_names and v.get("games", 0) > 0
        ]
        lanes.sort(key=lambda kv: kv[1]["games"], reverse=True)
        if lanes:
            lane_str = " · ".join(
                f"{lane_names[k]} — {v['games']} игр ({round((v['win'] / v['games']) * 100)}%)"
                for k, v in lanes[:3]
            )
            lines.append(f"Роли: {lane_str}")

    totals_map = {
        t["field"]: (t["sum"] / t["n"])
        for t in bundle.get("totals", [])
        if t.get("n", 0) > 0
    }
    if totals_map:
        lines.append("\n<b>Средние показатели за карьеру:</b>")
        lines.append(
            f"• K/D/A: <b>{totals_map.get('kills', 0):.1f} / {totals_map.get('deaths', 0):.1f} / {totals_map.get('assists', 0):.1f}</b> "
            f"(KDA {totals_map.get('kda', 0):.2f}) · Длит.: {round(totals_map.get('duration', 0) / 60)} мин"
        )
        lines.append(
            f"• GPM / XPM: <b>{round(totals_map.get('gold_per_min', 0))} / {round(totals_map.get('xp_per_min', 0))}</b> · "
            f"Добивания: {round(totals_map.get('last_hits', 0))} · Урон: {round(totals_map.get('hero_damage', 0)):,}".replace(",", " ")
        )

    recent = bundle["recent"]
    if recent:
        s20 = recent[:20]
        rw = sum(1 for m in s20 if (m["player_slot"] < 128) == bool(m["radiant_win"]))
        first_won = (s20[0]["player_slot"] < 128) == bool(s20[0]["radiant_win"])
        streak = 0
        for m in s20:
            if ((m["player_slot"] < 128) == bool(m["radiant_win"])) == first_won:
                streak += 1
            else:
                break
        avg_rgpm = round(sum(m.get("gold_per_min", 0) for m in s20) / len(s20))
        lines.append(
            f"• Форма ({len(s20)} игр): <b>{rw}W–{len(s20) - rw}L</b> ({round((rw / len(s20)) * 100)}%) · "
            f"Серия: {streak} {'побед' if first_won else 'пораж.'} подряд · Ср. GPM {avg_rgpm}"
        )

    top_heroes = sorted(bundle["rankings"], key=lambda x: x["percent_rank"], reverse=True)[:8]
    lines.append("\n<b>Топ-8 героев аккаунта:</b>")
    for idx, r in enumerate(top_heroes, 1):
        h_obj = heroes_map.get(r["hero_id"], {})
        h_name = h_obj.get("localized_name", f"Hero #{r['hero_id']}")
        pool = max(65000, min(1800000, int((h_obj.get("pub_pick") or 80000) * 4.15)))
        est_rank = max(1, int(round((1.0 - r["percent_rank"]) * pool)))
        top_pct = max(0.001, round((1.0 - r["percent_rank"]) * 100, 2))
        st = stat_map.get(r["hero_id"], {})
        g, w = st.get("games", 0), st.get("win", 0)
        wr = round((w / g) * 100, 1) if g > 0 else 0.0
        lines.append(
            f"{idx}. <b>{h_name}</b> — ~#{est_rank:,} (Топ {top_pct}%) · {round(r['score'], 1)} pts · {g} игр ({wr}%)".replace(",", " ")
        )

    peers = [p for p in bundle.get("peers", []) if p.get("with_games", 0) > 0 and p.get("personaname")][:4]
    if peers:
        lines.append("\n<b>Частые тиммейты:</b>")
        for peer in peers:
            pwr = round((peer["with_win"] / peer["with_games"]) * 100, 1)
            lines.append(f"• {peer['personaname']}: {peer['with_games']} игр вместе ({peer['with_win']} побед · {pwr}%)")

    if recent:
        lines.append("\n<b>Последние 6 матчей:</b>")
        for m in recent[:6]:
            h_name = heroes_map.get(m["hero_id"], {}).get("localized_name", f"#{m['hero_id']}")
            won = (m["player_slot"] < 128) == bool(m["radiant_win"])
            dmg_k = f" · {m.get('hero_damage', 0) / 1000:.1f}k урона" if m.get("hero_damage") else ""
            lines.append(
                f"• {'Победа' if won else 'Поражение'} на <b>{h_name}</b> — {m['kills']}/{m['deaths']}/{m['assists']} · "
                f"GPM {m.get('gold_per_min', 0)} / XPM {m.get('xp_per_min', 0)}{dmg_k} ({round(m['duration'] / 60)} мин)"
            )

    send_avatar_and_details(chat_id, avatar, caption, "\n".join(lines), account_id)


@bot.message_handler(commands=["rank"])
def handle_rank(message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(
            message,
            "Формат: <code>/rank &lt;Steam_ID_или_ссылка&gt; &lt;Герой&gt;</code>\n"
            "Пример: <code>/rank 86745912 Terrorblade</code> или <code>/rank 86745912 тб</code>",
        )
        return
    process_rank(message.chat.id, parts[1], parts[2])


def process_rank(chat_id: int, raw_id: str, hero_query: str):
    account_id = parse_account_id(raw_id)
    if not account_id:
        bot.send_message(chat_id, "Не удалось распознать Steam ID или ссылку на профиль.")
        return

    hero = find_hero(hero_query)
    if not hero:
        send_hero_suggestions(chat_id, hero_query, account_id=account_id)
        return

    bundle = fetch_player_full_bundle(account_id)
    if not bundle:
        bot.send_message(chat_id, "Профиль не найден или скрыт настройками приватности Dota 2.")
        return

    hero_id = hero["id"]
    lb_res = http.get(f"{OPENDOTA_API}/rankings?hero_id={hero_id}", timeout=15).json()
    leaderboard = sorted(lb_res.get("rankings", []), key=lambda x: x["score"], reverse=True)
    top1_score = leaderboard[0]["score"] if leaderboard else 8500.0
    top10_score = leaderboard[min(9, len(leaderboard) - 1)]["score"] if leaderboard else 8150.0
    top100_score = leaderboard[-1]["score"] if leaderboard else 7600.0
    total_pool = max(65000, min(1800000, int((hero.get("pub_pick") or 80000) * 4.15)))

    prof = bundle["profile"]
    p_info = prof["profile"]
    name = p_info.get("personaname") or f"ID {account_id}"
    avatar = p_info.get("avatarfull") or ""
    rank_label, approx_mmr = format_rank_tier(prof.get("rank_tier"), prof.get("leaderboard_rank"))

    exact_idx = next((i for i, e in enumerate(leaderboard) if e["account_id"] == account_id), -1)
    p_rank_entry = next((r for r in bundle["rankings"] if r["hero_id"] == hero_id), None)
    p_hero_stat = next((h for h in bundle["heroes"] if int(h["hero_id"]) == hero_id), None)

    games = p_hero_stat["games"] if p_hero_stat else 0
    wins = p_hero_stat["win"] if p_hero_stat else 0
    winrate = round((wins / games) * 100, 1) if games > 0 else 0.0

    is_estimated = False
    if exact_idx != -1:
        rank = exact_idx + 1
        score = leaderboard[exact_idx]["score"]
        percent_rank = 1.0 - (rank / total_pool)
        status = f"Подтверждён в официальном Топ-100 OpenDota (#{rank})"
    elif p_rank_entry:
        score = p_rank_entry["score"]
        percent_rank = p_rank_entry["percent_rank"]
        rank = max(101, int(round((1.0 - percent_rank) * total_pool)))
        status = "Расчёт по живому Hero Score и процентилю OpenDota"
    else:
        is_estimated = True
        wr_ratio = (wins / games) if games > 0 else 0.5
        conf = 1.0 - math.exp(-games / 22.0) if games > 0 else 0.0
        score = round(1900.0 + approx_mmr * 0.62 + (wr_ratio - 0.5) * 2600.0 * conf + (min(1250.0, math.log10(games + 1) * 430.0) if games > 0 else 0.0), 1)
        percent_rank = min(0.9997, max(0.01, 1.0 / (1.0 + math.exp(-0.00145 * (score - top100_score * 0.52)))))
        rank = max(101, int(round((1.0 - percent_rank) * total_pool)))
        status = "Оценочный расчёт (менее 10 рейтинговых игр на герое в индексе OpenDota)"

    top_percent = max(0.001, round((1.0 - percent_rank) * 100, 3))
    deficit = max(0.0, round(top100_score - score, 1))
    wins_needed = math.ceil(deficit / 38) if deficit > 0 else 0
    breakdown = build_score_breakdown(round(score, 1), games, wins, approx_mmr, rank_label, is_estimated)

    total_win = bundle["wl"].get("win", 0)
    total_lose = bundle["wl"].get("lose", 0)
    last_played = p_hero_stat.get("last_played") if p_hero_stat else None
    last_played_str = datetime.fromtimestamp(last_played).strftime("%d.%m.%Y") if last_played else "—"
    pub_wr = round((hero.get("pub_win", 0) / hero.get("pub_pick", 1)) * 100, 1)
    aliases = get_aliases_for_hero(hero["localized_name"])

    caption = (
        f"<b>{name}</b> ({rank_label}) — <b>{hero['localized_name']}</b>\n"
        f"Место в мире: <b>#{rank:,}</b> из ~{total_pool:,} (<b>Топ {top_percent}%</b>)\n"
        f"Hero Score: <b>{round(score, 1)} pts</b> · Топ-1: {round(top1_score, 1)} · Топ-10: {round(top10_score, 1)} · Порог Топ-100: {round(top100_score, 1)}\n"
        f"Матчи на герое: <b>{games}</b> ({wins}W – {games - wins}L · {winrate}%) · Посл. игра: {last_played_str}"
    ).replace(",", " ")

    detail_lines = [
        f"<b>Разбор Hero Score (за что начислены {round(score, 1)} pts):</b>",
    ]
    for label, pts, note in breakdown:
        sign = "+" if pts >= 0 else ""
        detail_lines.append(f"• {label}: <b>{sign}{pts} pts</b> <i>({note})</i>")

    detail_lines.append("")
    if deficit > 0:
        detail_lines.append(f"До входа в Топ-100: <b>+{deficit} pts</b> (~{wins_needed} чистых побед на герое)")
    else:
        to_first = max(0.0, round(top1_score - score, 1))
        detail_lines.append(f"Игрок уже в Топ-100! До 1 места в мире: +{to_first} pts")

    detail_lines.append(
        f"Мета героя за 30 дн.: {hero.get('pub_pick', 0):,} пиков · WR {pub_wr}%".replace(",", " ")
        + (f" · Аналоги: {', '.join(aliases[:4])}" if aliases else "")
    )
    if total_win + total_lose > 0:
        acc_wr = round((total_win / (total_win + total_lose)) * 100, 1)
        detail_lines.append(f"Аккаунт всего: {total_win + total_lose:,} матчей ({total_win}W – {total_lose}L · {acc_wr}%)".replace(",", " "))

    hero_recent = [m for m in bundle["recent"] if m.get("hero_id") == hero_id][:5]
    if hero_recent:
        detail_lines.append(f"\n<b>Последние матчи на {hero['localized_name']}:</b>")
        for m in hero_recent:
            won = (m["player_slot"] < 128) == bool(m["radiant_win"])
            dmg_k = f" · {m.get('hero_damage', 0) / 1000:.1f}k урона" if m.get("hero_damage") else ""
            detail_lines.append(
                f"• {'Победа' if won else 'Поражение'} — {m['kills']}/{m['deaths']}/{m['assists']} · "
                f"GPM {m.get('gold_per_min', 0)} / XPM {m.get('xp_per_min', 0)}{dmg_k} ({round(m['duration'] / 60)} мин)"
            )

    detail_lines.append(f"\n<i>{status}</i>")
    send_avatar_and_details(chat_id, avatar, caption, "\n".join(detail_lines), account_id)


@bot.message_handler(commands=["meta"])
def handle_meta(message):
    process_meta(message.chat.id)


def process_meta(chat_id: int):
    heroes = get_heroes()
    high_rank = sorted(
        [h for h in heroes if (h.get("8_pick", 0) + h.get("7_pick", 0)) > 100],
        key=lambda h: (h.get("8_win", 0) + h.get("7_win", 0)) / max(1, h.get("8_pick", 0) + h.get("7_pick", 0)),
        reverse=True,
    )[:6]
    most_picked = sorted(heroes, key=lambda h: h.get("pub_pick", 0), reverse=True)[:5]
    lines = ["<b>Мета текущего патча Dota 2</b>", DIV, "<b>Топ винрейта (Божество / Титан):</b>"]
    for idx, h in enumerate(high_rank, 1):
        hp = h.get("8_pick", 0) + h.get("7_pick", 0)
        hw = h.get("8_win", 0) + h.get("7_win", 0)
        wr = round((hw / max(1, hp)) * 100, 1)
        lines.append(f"{idx}. <b>{h['localized_name']}</b> — {wr}% <code>{render_bar(wr, 8)}</code> ({hp:,} игр)".replace(",", " "))
    lines.append("\n<b>Самые популярные (30 дн.):</b>")
    for idx, h in enumerate(most_picked, 1):
        wr = round((h.get("pub_win", 0) / max(1, h.get("pub_pick", 1))) * 100, 1)
        lines.append(f"{idx}. <b>{h['localized_name']}</b> — {h.get('pub_pick', 0):,} пиков · WR {wr}%".replace(",", " "))
    bot.send_message(chat_id, "\n".join(lines))


@bot.message_handler(commands=["matches"])
def handle_matches(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: <code>/matches &lt;ID_или_ссылка&gt;</code>\nПример (тест): <code>/matches 86745912</code>")
        return
    process_matches(message.chat.id, parts[1])


def process_matches(chat_id: int, raw_id: str):
    account_id = parse_account_id(raw_id)
    if not account_id:
        bot.send_message(chat_id, "Некорректный Steam ID или ссылка.")
        return
    bundle = fetch_player_full_bundle(account_id)
    if not bundle:
        bot.send_message(chat_id, "Профиль скрыт или не найден.")
        return
    heroes_map = {h["id"]: h["localized_name"] for h in get_heroes()}
    name = bundle["profile"]["profile"].get("personaname") or f"ID {account_id}"
    recent = bundle["recent"][:10]
    lines = [f"<b>Последние {len(recent)} матчей — {name}</b>", DIV]
    kb = InlineKeyboardMarkup(row_width=1)
    for idx, m in enumerate(recent, 1):
        won = (m["player_slot"] < 128) == bool(m["radiant_win"])
        h_name = heroes_map.get(m["hero_id"], f"#{m['hero_id']}")
        dmg = f"{m.get('hero_damage', 0) / 1000:.1f}k"
        lines.append(
            f"{idx}. {'✅ Победа' if won else '❌ Поражение'} — <b>{h_name}</b> ({format_clock(m['duration'])})\n"
            f"   <code>{m['kills']}/{m['deaths']}/{m['assists']}</code> · GPM {m.get('gold_per_min', 0)} / XPM {m.get('xp_per_min', 0)} · {dmg} урона · ID <code>{m['match_id']}</code>"
        )
        if idx <= 3:
            kb.add(InlineKeyboardButton(f"🔍 Разбор 5×5: {h_name} (#{m['match_id']})", callback_data=f"demo_match:{m['match_id']}"))
    bot.send_message(chat_id, "\n".join(lines), reply_markup=kb)


@bot.message_handler(commands=["match"])
def handle_match(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not re.sub(r"\D", "", parts[1]):
        bot.reply_to(message, "Формат: <code>/match &lt;Match_ID&gt;</code>")
        return
    process_match(message.chat.id, int(re.sub(r"\D", "", parts[1])))


def process_match(chat_id: int, match_id: int):
    m = http.get(f"{OPENDOTA_API}/matches/{match_id}", timeout=15).json()
    if not m or "players" not in m:
        bot.send_message(chat_id, f"Матч #{match_id} не найден.")
        return
    heroes_map = {h["id"]: h["localized_name"] for h in get_heroes()}
    winner = "Силы Света (Radiant)" if m.get("radiant_win") else "Силы Тьмы (Dire)"
    lines = [
        f"<b>Разбор матча #{match_id}</b>",
        DIV,
        f"Победитель: <b>{winner}</b> · Счёт: <b>{m.get('radiant_score', 0)}:{m.get('dire_score', 0)}</b> · {format_clock(m.get('duration', 0))}",
        "",
        "<b>Radiant:</b>",
    ]
    for p in [x for x in m["players"] if x.get("player_slot", 0) < 128]:
        h_name = heroes_map.get(p.get("hero_id"), f"#{p.get('hero_id')}")
        lines.append(f"• <b>{h_name}</b> ({p.get('personaname') or 'Аноним'}) — {p.get('kills', 0)}/{p.get('deaths', 0)}/{p.get('assists', 0)} · GPM {p.get('gold_per_min', 0)} · {p.get('hero_damage', 0) / 1000:.1f}k")
    lines.append("\n<b>Dire:</b>")
    for p in [x for x in m["players"] if x.get("player_slot", 0) >= 128]:
        h_name = heroes_map.get(p.get("hero_id"), f"#{p.get('hero_id')}")
        lines.append(f"• <b>{h_name}</b> ({p.get('personaname') or 'Аноним'}) — {p.get('kills', 0)}/{p.get('deaths', 0)}/{p.get('assists', 0)} · GPM {p.get('gold_per_min', 0)} · {p.get('hero_damage', 0) / 1000:.1f}k")
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("OpenDota ↗", url=f"https://www.opendota.com/matches/{match_id}"),
        InlineKeyboardButton("Dotabuff ↗", url=f"https://www.dotabuff.com/matches/{match_id}"),
    )
    bot.send_message(chat_id, "\n".join(lines), reply_markup=kb)


@bot.message_handler(commands=["records"])
def handle_records(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: <code>/records &lt;ID&gt;</code>\nПример (тест): <code>/records 86745912</code>")
        return
    process_records(message.chat.id, parts[1])


def process_records(chat_id: int, raw_id: str):
    account_id = parse_account_id(raw_id)
    if not account_id:
        bot.send_message(chat_id, "Некорректный Steam ID или ссылка.")
        return
    bundle = fetch_player_full_bundle(account_id)
    if not bundle:
        bot.send_message(chat_id, "Профиль скрыт или не найден.")
        return
    heroes_map = {h["id"]: h["localized_name"] for h in get_heroes()}
    name = bundle["profile"]["profile"].get("personaname") or f"ID {account_id}"
    recent = bundle["recent"]
    lines = [f"<b>Личные рекорды и контрпики — {name}</b>", DIV]
    if recent:
        metrics = [
            ("Макс. убийств", lambda x: x.get("kills", 0), lambda v: f"{v} киллов"),
            ("Рекорд GPM", lambda x: x.get("gold_per_min", 0), lambda v: f"{v} зол/мин"),
            ("Макс. урон по героям", lambda x: x.get("hero_damage", 0), lambda v: f"{v:,}".replace(",", " ")),
            ("Макс. урон по башням", lambda x: x.get("tower_damage", 0), lambda v: f"{v:,}".replace(",", " ")),
            ("Самый долгий матч", lambda x: x.get("duration", 0), format_clock),
        ]
        lines.append("<b>Рекорды (по 20 последним матчам):</b>")
        for label, sel, fmt in metrics:
            best = max(recent, key=sel)
            val = sel(best)
            if val > 0:
                lines.append(f"• {label}: <b>{fmt(val)}</b> на {heroes_map.get(best['hero_id'], '#')} (ID <code>{best['match_id']}</code>)")
    min_ag = 20 if any(h.get("against_games", 0) >= 20 for h in bundle["heroes"]) else 5
    hardest = sorted(
        [h for h in bundle["heroes"] if h.get("against_games", 0) >= min_ag],
        key=lambda h: h.get("against_win", 0) / max(1, h.get("against_games", 1)),
    )[:5]
    if hardest:
        lines.append("\n<b>Самые неудобные герои против:</b>")
        for hm in hardest:
            ag = hm.get("against_games", 1)
            aw = hm.get("against_win", 0)
            wr = round((aw / ag) * 100, 1)
            lines.append(f"• Против <b>{heroes_map.get(int(hm['hero_id']), '#')}</b>: {wr}% WR <code>{render_bar(wr, 8)}</code> ({aw}/{ag})")
    bot.send_message(chat_id, "\n".join(lines), reply_markup=build_profile_keyboard(account_id))


@bot.message_handler(commands=["compare"])
def handle_compare(message):
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Формат: <code>/compare &lt;ID1&gt; &lt;ID2&gt;</code>\nПример (тест): <code>/compare 86745912 105248644</code>")
        return
    process_compare(message.chat.id, parts[1], parts[2])


def process_compare(chat_id: int, raw1: str, raw2: str):
    id1, id2 = parse_account_id(raw1), parse_account_id(raw2)
    if not id1 or not id2:
        bot.send_message(chat_id, "Укажите корректные ID обоих игроков.")
        return
    b1 = fetch_player_full_bundle(id1, include_extended=True)
    b2 = fetch_player_full_bundle(id2, include_extended=True)
    if not b1 or not b2:
        bot.send_message(chat_id, "Один из профилей скрыт или не найден.")
        return
    n1 = b1["profile"]["profile"].get("personaname") or f"ID {id1}"
    n2 = b2["profile"]["profile"].get("personaname") or f"ID {id2}"
    r1, m1 = format_rank_tier(b1["profile"].get("rank_tier"), b1["profile"].get("leaderboard_rank"))
    r2, m2 = format_rank_tier(b2["profile"].get("rank_tier"), b2["profile"].get("leaderboard_rank"))
    g1 = b1["wl"].get("win", 0) + b1["wl"].get("lose", 0)
    g2 = b2["wl"].get("win", 0) + b2["wl"].get("lose", 0)
    wr1 = round((b1["wl"].get("win", 0) / max(1, g1)) * 100, 1)
    wr2 = round((b2["wl"].get("win", 0) / max(1, g2)) * 100, 1)
    t1 = {t["field"]: t["sum"] / t["n"] for t in b1.get("totals", []) if t.get("n", 0) > 0}
    t2 = {t["field"]: t["sum"] / t["n"] for t in b2.get("totals", []) if t.get("n", 0) > 0}
    lines = [
        f"<b>Сравнение: {n1} vs {n2}</b>",
        DIV,
        f"Ранг: <b>{r1}</b> (~{m1}) | <b>{r2}</b> (~{m2})",
        f"Матчи: {g1:,} ({wr1}%) | {g2:,} ({wr2}%)".replace(",", " "),
        f"Средний KDA: {t1.get('kda', 0):.2f} | {t2.get('kda', 0):.2f}",
        f"GPM / XPM: {round(t1.get('gold_per_min', 0))}/{round(t1.get('xp_per_min', 0))} | {round(t2.get('gold_per_min', 0))}/{round(t2.get('xp_per_min', 0))}",
        f"Урон по героям: {round(t1.get('hero_damage', 0)):,} | {round(t2.get('hero_damage', 0)):,}".replace(",", " "),
    ]
    bot.send_message(chat_id, "\n".join(lines))


@bot.message_handler(commands=["top"])
def handle_top(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: <code>/top &lt;Герой&gt;</code>\nПример: <code>/top Pudge</code> или <code>/top пудж</code>")
        return
    process_top(message.chat.id, parts[1])


def process_top(chat_id: int, hero_query: str):
    hero = find_hero(hero_query)
    if not hero:
        send_hero_suggestions(chat_id, hero_query)
        return
    lb = http.get(f"{OPENDOTA_API}/rankings?hero_id={hero['id']}", timeout=15).json()
    ranked = sorted(lb.get("rankings", []), key=lambda x: x["score"], reverse=True)
    top15 = ranked[:15]
    top100_score = round(ranked[-1]["score"], 1) if ranked else 0
    pub_wr = round((hero.get("pub_win", 0) / hero.get("pub_pick", 1)) * 100, 1)
    aliases = get_aliases_for_hero(hero["localized_name"])
    lines = [
        f"<b>Топ-15 игроков мира на {hero['localized_name']}</b>",
        DIV,
        f"Пиков за 30 дн.: {hero.get('pub_pick', 0):,} · WR: {pub_wr}% · Порог Топ-100: {top100_score} pts".replace(",", " "),
    ]
    if aliases:
        lines.append(f"Сленг: {', '.join(aliases[:5])}")
    lines.append("")
    for idx, row in enumerate(top15, 1):
        r_label, _ = format_rank_tier(row.get("rank_tier"))
        p_name = row.get("personaname") or row["account_id"]
        lines.append(f"{idx}. <b>{p_name}</b> ({r_label}) — <code>{round(row['score'], 1)} pts</code> [ID: <code>{row['account_id']}</code>]")
    bot.send_message(chat_id, "\n".join(lines))


@bot.message_handler(func=lambda m: bool(m.text) and not m.text.startswith("/"))
def handle_reply_keyboard_buttons(message):
    txt = message.text.strip()
    if txt == "📋 Список команд":
        handle_commands_list(message)
    elif txt == "📊 Мета патча":
        process_meta(message.chat.id)
    elif txt == "🎭 Сленг героев":
        handle_aliases(message)
    elif txt == "🚀 Старт":
        handle_start(message)
    elif txt == "📱 Открыть Mini App":
        handle_app(message)


if __name__ == "__main__":
    register_slash_commands()
    print("Карманный Dotabuff-бот запущен: меню '/', /commands, /profile, /matches, /match, /records, /compare, /meta и inline-поиск активны...")
   

# ==========================================
# Вставь этот единый блок в САМЫЙ КОНЕЦ файла bot.py:
# ==========================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Dota Mini App Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    register_slash_commands()
    print("Карманный Dotabuff-бот запущен...")
    
    # 1. Запускаем веб-сервер Flask в фоновом потоке (чтобы Render видел открытый порт)
    threading.Thread(target=run_web, daemon=True).start()
    
    # 2. В главном потоке запускаем самого Telegram-бота
    bot.infinity_polling(skip_pending=True)
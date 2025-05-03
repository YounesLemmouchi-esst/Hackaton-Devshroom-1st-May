# Configuration file for LangaQuest

# Game settings
ERAS = ["Stone Age", "Medieval", "Industrial", "Modern", "Future"]
XP_PER_QUESTION = 5
XP_FOR_LEVEL_UP = 200  # XP needed to level up

# AI configuration
GEMINI_MODEL = "gemini-2.0-flash"
CREDENTIALS_PATH = "devshroom-hackathon-b428c409d22f.json"

# Game tips that rotate
TIPS = [
    "💡 Try to maintain your streak for bonus XP!",
    "💡 Watch for accents in French words.",
    "💡 Defeat bosses to travel through time!",
    "💡 The further you go, the harder it gets.",
    "💡 Minor spelling errors are forgiven in boss battles."
]

# Default shop items
DEFAULT_SHOP_ITEMS = {
    "hint_powerup": {
        "name": "Hint Powerup",
        "description": "Get a hint on your next difficult question",
        "price": 10,
        "icon": "💡",
        "purchased": False,
        "era": "all"  # This item is available in all eras
    },
    "stone_meat": {
        "name": "Prehistoric Meat",
        "description": "A chunk of raw mammoth meat - Stone Age delicacy",
        "price": 50,
        "icon": "🥩",
        "purchased": False,
        "era": "Stone Age"  # Only available in Stone Age
    },
    "stone_rock": {
        "name": "Sharp Rock",
        "description": "A primitive tool for hunting and crafting",
        "price": 50,
        "icon": "🪨",
        "purchased": False,
        "era": "Stone Age"  # Only available in Stone Age
    },
    "medieval_sword": {
        "name": "Medieval Sword",
        "description": "A knight's trusted weapon",
        "price": 75,
        "icon": "⚔️",
        "purchased": False,
        "era": "Medieval"  # Only available in Medieval era
    },
    "industrial_gear": {
        "name": "Factory Gear",
        "description": "An essential machine part",
        "price": 100,
        "icon": "⚙️",
        "purchased": False,
        "era": "Industrial"  # Only available in Industrial era
    }
}

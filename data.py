# Exile Roulette pool — Path of Exile 2, patch 0.5.
# Kept in sync with the Exile Roulette web app. Excludes Kalguuran (Return of the
# Ancients) skills, which drop separately and are not on the Uncut Skill Gem list.

# (class name, wheel colour, ascendancies)
CLASSES = [
    ("Warrior",   (122, 46, 34),  ["Titan", "Warbringer", "Smith of Kitava"]),
    ("Sorceress", (45, 74, 122),  ["Stormweaver", "Chronomancer", "Disciple of Varashta"]),
    ("Witch",     (90, 42, 94),   ["Infernalist", "Blood Mage", "Lich"]),
    ("Ranger",    (47, 90, 53),   ["Deadeye", "Pathfinder"]),
    ("Monk",      (43, 93, 99),   ["Invoker", "Acolyte of Chayula", "Martial Artist"]),
    ("Mercenary", (107, 90, 42),  ["Witchhunter", "Gemling Legionnaire", "Tactician"]),
    ("Huntress",  (106, 61, 36),  ["Amazon", "Ritualist", "Spirit Walker"]),
    ("Druid",     (63, 90, 42),   ["Oracle", "Shaman"]),
]

# One wheel segment per ascendancy, in wheel order.
SEGMENTS = [
    {"asc": asc, "cls": name, "color": color}
    for name, color, ascs in CLASSES
    for asc in ascs
]

# Source: the Uncut Skill Gem selection list (poe2db.tw/us/Uncut_Skill_Gem), i.e. only
# skills a player can actually create in 0.5. Categories are the game's own groups.
# Left out: buffs, curses, marks, warcries, offerings, movement and utility skills.
# Item-granted skills are listed separately in ITEM_SKILLS below.
SKILLS = {
    "Mace": ["Rolling Slam", "Boneshatter", "Earthquake", "Shockwave Totem", "Molten Blast",
             "Perfect Strike", "Resonating Shield", "Shield Wall", "Earthshatter", "Volcanic Fissure",
             "Forge Hammer", "Sunder", "Supercharged Slam", "Stampede", "Hammer of the Gods",
             "Ancestral Warrior Totem"],
    "Spear": ["Whirling Slash", "Twister", "Explosive Spear", "Rake", "Fangs of Frost", "Lightning Spear",
              "Cull the Weak", "Rapid Assault", "Storm Lance", "Spearfield", "Glacial Lance", "Blood Hunt",
              "Thunderous Leap", "Primal Strikes", "Elemental Sundering", "Whirlwind Lance",
              "Spear of Solaris", "Wind Serpent's Fury"],
    "Bow": ["Lightning Arrow", "Poisonburst Arrow", "Lightning Rod", "Freezing Salvo", "Stormcaller Arrow",
            "Snipe", "Vine Arrow", "Toxic Growth", "Electrocuting Arrow", "Gas Arrow", "Ice Shot",
            "Detonating Arrow", "Rain of Arrows", "Shockchain Arrow", "Tornado Shot", "Magnetic Salvo",
            "Spiral Volley"],
    "Crossbow": ["Explosive Grenade", "Permafrost Bolts", "Fragmentation Rounds", "Armour Piercing Rounds",
                 "High Velocity Rounds", "Incendiary Shot", "Galvanic Shards", "Ice Shards", "Gas Grenade",
                 "Rapid Shot", "Artillery Ballista", "Glacial Bolt", "Explosive Shot", "Voltaic Grenade",
                 "Oil Grenade", "Siege Ballista", "Stormblast Bolts", "Hailstorm Rounds", "Shockburst Rounds",
                 "Siege Cascade", "Plasma Blast", "Cluster Grenade"],
    "Quarterstaff": ["Falling Thunder", "Frozen Locus", "Killing Palm", "Glacial Cascade", "Tempest Bell",
                     "Ice Strike", "Tempest Flurry", "Wave of Frost", "Storm Wave", "Charged Staff",
                     "Hand of Chayula", "Whirling Assault", "Flicker Strike", "Gathering Storm"],
    "Elemental": ["Spark", "Ice Nova", "Flame Wall", "Frost Bomb", "Frost Darts", "Living Bomb", "Fireball",
                  "Orb of Storms", "Arc", "Frostbolt", "Ember Fusillade", "Incinerate", "Ball Lightning",
                  "Firestorm", "Comet", "Flameblast", "Eye of Winter", "Lightning Conduit"],
    "Occult": ["Unearth", "Contagion", "Skeletal Sniper", "Essence Drain", "Skeletal Arsonist",
               "Raise Zombie", "Bonestorm", "Skeletal Frost Mage", "Bind Spectre", "Detonate Dead",
               "Skeletal Reaver", "Dark Effigy", "Skeletal Storm Mage", "Hexblast", "Skeletal Brute"],
    "Primal": ["Lunar Assault", "Entangle", "Volcano", "Furious Slam", "Rolling Magma", "Wing Blast",
               "Thunderstorm", "Fury of the Mountain", "Cross Slash", "Thrashing Vines", "Oil Barrage",
               "Rampage", "Tornado", "Flame Breath"],
}

# Skills granted by items, with the item you need: (skill, item, item description).
# Source: poe2db base-type and unique pages. Where several bases grant the same skill,
# the lowest-level base is named. Left out: auras/buffs/utility (e.g. Mana Drain,
# Sigil of Power, Purity sceptres), and anything from Kalguuran items
# (Twisted Empyrean / Starborn Onslaught).
ITEM_SKILLS = {
    "Wand": [
        ("Chaos Bolt", "Withered Wand", "wand base"),
        ("Bone Blast", "Bone Wand", "wand base"),
        ("Power Siphon", "Siphoning Wand", "wand base"),
        ("Volatile Dead", "Volatile Wand", "wand base"),
        ("Galvanic Field", "Galvanic Wand", "wand base"),
        ("Decompose", "Acrid Wand", "wand base"),
        ("Exsanguinate", "Offering Wand", "wand base"),
        ("Coiling Bolts", "Twisted Wand", "wand base"),
    ],
    "Staff": [
        ("Firebolt", "Ashen Staff", "staff base"),
        ("Freezing Shards", "Gelid Staff", "staff base"),
        ("Lightning Bolt", "Voltaic Staff", "staff base"),
        ("Solar Orb", "Pyrophyte Staff", "staff base"),
        ("Soulrend", "Rending Staff", "staff base"),
        ("Reap", "Reaping Staff", "staff base"),
        ("Enervating Nova", "Paralysing Staff", "staff base"),
        ("Dark Pact", "Dark Staff", "staff base"),
        ("Spiraling Conspiracy", "Perching Staff", "staff base"),
    ],
    "Sceptre": [
        ("Skeletal Warrior", "Rattling Sceptre", "sceptre base"),
    ],
    "Unique": [
        ("Icestorm", "The Whispering Ice", "unique Staff"),
        ("Molten Crash", "Fury of the King", "unique Talisman"),
        ("Requiem", "The Last Lament", "unique Desolate Crossbow"),
        ("Phantasmal Arrow", "Fairgraves' Curse", "unique Artillery Bow"),
        ("Shattering Spite", "Atziri's Contempt", "unique Spear"),
        ("Righteous Descent", "The Ordained", "unique Grand Spear"),
        ("Soaring Midnight", "Nightfall", "unique Glacial Fortress shield"),
        ("Crushing Fear", "Horror's Flight", "unique Engraved Bracers"),
    ],
}

# Flat list of (skill name, category, item or None, item description or None).
SKILL_POOL = (
    [(name, cat, None, None) for cat, names in SKILLS.items() for name in names]
    + [(name, cat, item, desc) for cat, entries in ITEM_SKILLS.items() for name, item, desc in entries]
)

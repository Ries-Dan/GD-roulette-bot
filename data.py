# Exile Roulette pool — Path of Exile 2, patch 0.5.
# Kept in sync with the Exile Roulette web app. Excludes Kalguuran (Return of the
# Ancients) skills, ascendancy-only skills, unique-item skills, and buffs/auras/marks.

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

SKILLS = {
    "Mace": ["Boneshatter", "Earthquake", "Rolling Slam", "Earthshatter", "Perfect Strike",
             "Supercharged Slam", "Sunder", "Volcanic Fissure", "Molten Blast", "Forge Hammer",
             "Stampede", "Hammer of the Gods", "Shockwave Totem", "Ancestral Warrior Totem"],
    "Shield": ["Shield Charge", "Resonating Shield", "Shield Wall"],
    "Spear": ["Whirling Slash", "Explosive Spear", "Fangs of Frost", "Rake", "Blood Hunt",
              "Rapid Assault", "Spearfield", "Lightning Spear", "Twister", "Glacial Lance",
              "Whirlwind Lance", "Thunderous Leap", "Spear of Solaris", "Wind Serpent's Fury",
              "Primal Strikes", "Cull the Weak", "Elemental Sundering"],
    "Bow": ["Lightning Arrow", "Lightning Rod", "Poisonburst Arrow", "Snipe", "Stormcaller Arrow",
            "Vine Arrow", "Electrocuting Arrow", "Ice Shot", "Rain of Arrows", "Tornado Shot",
            "Gas Arrow", "Toxic Growth", "Shockchain Arrow", "Spiral Volley", "Detonating Arrow",
            "Freezing Salvo", "Magnetic Salvo"],
    "Crossbow": ["Armour Piercing Rounds", "Explosive Shot", "Fragmentation Rounds", "Galvanic Shards",
                 "Glacial Bolt", "Hailstorm Rounds", "High Velocity Rounds", "Incendiary Shot",
                 "Permafrost Bolts", "Plasma Blast", "Rapid Shot", "Shockburst Rounds", "Siege Cascade",
                 "Stormblast Bolts", "Artillery Ballista", "Ripwire Ballista", "Explosive Grenade",
                 "Gas Grenade", "Oil Grenade", "Cluster Grenade"],
    "Quarterstaff": ["Falling Thunder", "Glacial Cascade", "Ice Strike", "Tempest Flurry", "Tempest Bell",
                     "Whirling Assault", "Killing Palm", "Charged Staff", "Storm Wave", "Wave of Frost"],
    "Elemental Spell": ["Fireball", "Flame Wall", "Firestorm", "Incinerate", "Flameblast", "Solar Orb",
                        "Ember Fusillade", "Comet", "Frostbolt", "Ice Nova", "Frost Bomb", "Eye of Winter",
                        "Spark", "Arc", "Ball Lightning", "Lightning Conduit", "Orb of Storms",
                        "Galvanic Field", "Living Bomb"],
    "Chaos & Occult": ["Chaos Bolt", "Contagion", "Essence Drain", "Hexblast", "Soulrend", "Dark Effigy",
                       "Bonestorm", "Bone Blast", "Exsanguinate", "Reap", "Detonate Dead", "Volatile Dead",
                       "Power Siphon"],
    "Minion": ["Skeletal Warrior", "Skeletal Sniper", "Skeletal Arsonist", "Skeletal Frost Mage",
               "Skeletal Storm Mage", "Skeletal Reaver", "Skeletal Brute", "Raise Zombie", "Raging Spirits",
               "Bind Spectre", "Unearth", "Tame Beast"],
    "Druid": ["Volcano", "Thunderstorm", "Entangle", "Maul", "Furious Slam", "Rampage",
              "Fury of the Mountain", "Cross Slash", "Lunar Assault", "Pounce", "Shred", "Wing Blast",
              "Flame Breath", "Rolling Magma", "Oil Barrage"],
}

# Flat list of (skill name, category).
SKILL_POOL = [(name, cat) for cat, names in SKILLS.items() for name in names]

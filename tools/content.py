# Hand-written prose for the guide. Numbers never live here: they come from results.json.

TALENT_TEXT = {
    'Shifting Power': 'Turns mana into energy instantly, on an 8 s cooldown. Use it at 53 energy or less, about 23 times in a 3 minute fight. The biggest talent in the tree.',
    'Naturalist': 'All your damage goes up by a flat percent.',
    'Rend and Tear': 'Your melee abilities hit harder on a bleeding target. Your own Rake and Rip keep the boss bleeding.',
    'Sharpened Claws': 'More crit in Cat Form.',
    'Natural Instinct': 'Bigger crits on your melee abilities.',
    'Shredding Attacks': 'Cheaper Shred. This is what makes Shred your builder; without it you Claw.',
    'Savage Fury': 'More damage on Claw, Rake and Shred.',
    "Nature's Majesty": 'More crit, melee included.',
    'Genesis': 'Your bleeds (Rake, Rip) tick harder.',
    'Predatory Strikes': 'Attack power in Cat Form, scaled to your level.',
    'Heart of the Wild': 'More Strength in Cat Form (and Intellect for mana).',
    'Blood Frenzy': 'Builder crits can give an extra combo point, so you reach 4 points faster.',
    'Ferocity': 'Cheaper Claw and Rake. Worth a lot more on Hybrid, which Claws.',
    "Nature's Reach": '+2% hit per point. Each point saves you 20 hit rating on gear.',
    'Predatory Discipline': 'Ferocious Bite stops eating your extra energy but still hits harder with it. Lets you weave Bites in while Rip runs.',
    'Furor': 'Energy back when you shift into Cat Form, like after Innervate. Small, but it beats the utility talents.',
    'Leader of the Pack': '+crit for you and your party. Worth this much to you alone; more to the raid.',
    'Feral Swiftness': 'Run speed and dodge. No DPS; the builds above skip it. Taking it back costs about 2 DPS.',
    'Feral Charge': 'Bear charge. Utility; the builds above skip it. Taking it back costs about 10 DPS (the Nature\u2019s Reach or Majesty point).',
    'Feral Instinct': 'Bear Swipe damage. Tank talent.',
    'Thick Hide': 'Armor. Tank talent.',
    'Lacerate': 'Bear bleed. Tank talent.',
    'Primal Bite': 'Bear threat attack. Tank talent.',
}

BUILDS = {
    'cat': {
        'name': 'Cat', 'sub': 'Shred build, 2/2 Blood Frenzy', 'difficulty': 'Medium', 'main': True,
        'when': 'Pure damage. Shred is your builder, Rip and Rake stay up, Bite between Rips.',
        'changes': 'Versus the sim\u2019s preset: Nature\u2019s Reach 2/2 and Furor 5/5, paid for with Feral Charge and Feral Swiftness. Want Feral Charge back? It costs about 10 DPS.',
    },
    'hybrid': {
        'name': 'Hybrid', 'sub': 'Shred build that can tank', 'difficulty': 'Medium',
        'when': 'Keeps Thick Hide, Lacerate and Primal Bite so you can bear tank when needed, and still Shreds. Gives up Blood Frenzy for them.',
        'changes': 'Versus the sim\u2019s preset: Shredding Attacks instead of Feral Instinct (Shred instead of Claw), Nature\u2019s Majesty 2/2 and Furor 2/5, paid for with Feral Charge and Feral Swiftness. Want Feral Charge back for tanking? It costs about 15 DPS.',
    },
}

OPENER = [
    ('On the pull', 'Dash in as the pull starts.'),
    ('Faerie Fire', "Keep it on the boss if nobody else does. If the raid already has it up, skip it."),
    ('Into the loop', 'Rake, build points, Rip. The sim rarely opens with Ravage, so skip it.'),
]

# Each step: title, text, which builds it applies to
LOOP = [
    ('Shifting Power', 'At 53 energy or less, whenever it is off cooldown (8 s).', ['cat', 'hybrid']),
    ('Ferocious Bite (mid-fight)', 'At {bite_cp}+ combo points, while Rip still has {rip_left}+ s left and you have 75 energy (60 at 5 points, 45 with Clearcasting).', ['cat', 'hybrid']),
    ('Clearcasting → Shred', 'A free Shred whenever Clearcasting is up and Bite is not ready.', ['cat', 'hybrid']),
    ('Rip', 'When it is down and 8+ s of the fight are left: at 4 combo points, or 5 if one more Shred still leaves energy for Rip right after.', ['cat', 'hybrid']),
    ('Rake', 'When it is down, if 6+ s of the fight are left.', ['cat', 'hybrid']),
    ('{builder}', 'Your builder. Hold it back when you are pooling energy for a Bite.', ['cat', 'hybrid']),
    ('Innervate', 'Under 1400 mana with 30 energy or less, then shift back to Cat. On fights of 3 minutes or less you can skip it (a few DPS more); on longer ones you need the mana.', ['cat', 'hybrid']),
]
LOOP_FILL = {
    'cat': {'bite_cp': 4, 'rip_left': 3, 'rip_cp': '4 (5 if one more Shred still leaves energy for Rip right after)', 'builder': 'Shred'},
    'hybrid': {'bite_cp': 5, 'rip_left': 4, 'rip_cp': '4 (5 if one more Shred still leaves energy for Rip right after)', 'builder': 'Shred'},
}
LOOP_END = 'Last 8 s: no new Rip; Bite at 5 points. Last global: Bite at 2+ points.'
COOLDOWNS = 'On cooldown: Mighty Rage Potion, Goblin Sapper Charge, your racial. Major Mana Potion under 1400 mana.'

BUFF_NAMES = {
    'windfuryTotem': 'Windfury Totem', 'graceOfAirTotem': 'Grace of Air Totem', 'greaterBlessingOfKings': 'Greater Blessing of Kings',
    'judgementOfWisdom': 'Judgement of Wisdom', 'battleShout': 'Battle Shout', 'strengthOfEarthTotem': 'Strength of Earth Totem',
    'giftOfArthas': 'Gift of Arthas', 'markOfTheWild': 'Mark of the Wild', 'arcaneIntellect': 'Arcane Intellect',
    'prayerOfSpirit': 'Prayer of Spirit', 'judgementOfLight': 'Judgement of Light', 'curseOfElements': 'Curse of the Elements',
    'insectSwarm': 'Insect Swarm', 'sunderArmor': 'Sunder Armor', 'exposeArmor': 'Expose Armor', 'faerieFire': 'Faerie Fire',
    'curseOfRecklessness': 'Curse of Recklessness',
}

RACES = {
    'RaceNightElf': ('Night Elf', 'Alliance', "+5 Agility. Elune's Light: +10% crit for 15 s every 3 min. +1% dodge"),
    'RaceTauren': ('Tauren', 'Horde', '+5 Strength, \u22125 Agility. +5% health'),
    'RaceHighOrderSkyborne': ('High Order Skyborne', 'Alliance', '+4 Agility. +2% attack speed, +5% damage to Elementals, a mana-regen cast'),
    'RaceWindshaperSkyborne': ('Windshaper Skyborne', 'Horde', '+3 Agility. +2% attack speed, +5% damage to Elementals, a run-speed cast'),
}

ENCHANTS = {
    'Head': 'Lesser Arcane Amalgamation', 'Neck': 'Agility', 'Back': 'Agility', 'Chest': 'Greater Stats',
    'Wrist': 'Agility', 'Hands': 'Superior Agility', 'Legs': 'Lesser Arcane Amalgamation', 'Feet': 'Greater Agility',
    'Weapon': 'Superior Impact',
}

PROFESSIONS = {1: 'Alchemy', 2: 'Blacksmithing', 3: 'Enchanting', 4: 'Engineering', 8: 'Leatherworking', 11: 'Tailoring'}

MACROS = [
    ('Prowl', 'First press shifts you to Cat, second press Prowls.',
     '#showtooltip Prowl\n/cast [noform:3] Cat Form; Prowl'),
    ('Shred (and the opener)', 'Starts your auto attack, opens with Ravage from Prowl, otherwise Shreds.',
     '#showtooltip\n/startattack\n/cast [stealth] Ravage; Shred'),
    ('Cat Form (no toggle)', 'The ! stops a second press from dropping you out of Cat. Use it after Innervate; Furor gives energy back.',
     '#showtooltip\n/cast !Cat Form'),
    ('Innervate yourself', 'Drops Cat Form and Innervates you in one press, even with a friendly target. Then hit Cat Form.',
     '#showtooltip Innervate\n/cancelform [form:3]\n/cast [@player] Innervate'),
    ('Cooldowns', 'Both trinket slots and the strength potion on one key, for the start of the fight.',
     '#showtooltip\n/use 13\n/use 14\n/use Mighty Rage Potion'),
]
MACRO_NOTE = 'Forever uses the Classic client’s macro conditions, the same ones the hunter guide’s macros use. Form 3 is Cat Form when you know Bear, Aquatic and Cat; check yours with /dump GetShapeshiftForm() if it differs.'

CONSUMABLE_NOTE = {
    'cat': 'Sorted by what you lose without it. Everything is on in the setup, so each number is its worth on top of the rest.',
    'hybrid': 'Same consumables, measured on Hybrid.',
}


LOOP_ICONS = {'Shifting Power': 'spell_druid_displacement', 'Ferocious Bite (mid-fight)': 'ability_druid_ferociousbite',
              'Clearcasting \u2192 Shred': 'spell_shadow_manaburn', 'Rip': 'ability_ghoulfrenzy', 'Rake': 'ability_druid_disembowel',
              'Shred': 'spell_shadow_vampiricaura', 'Claw': 'ability_druid_rake', 'Innervate': 'spell_nature_lightning'}

# From a sim log of the Cat build: what it casts in the first seconds.
OPENER_CHIPS = [
    (['ability_druid_dash'], 'Dash', 'on the pull, to get in fast'),
    (['spell_nature_moonglow', 'inv_potion_41', 'spell_fire_selfdestruct'], 'Racial + Mighty Rage Potion + Sapper', 'as you reach the boss'),
    (['ability_druid_disembowel'], 'Rake', ''),
    (['spell_shadow_vampiricaura'], 'Shred', ''),
    (['spell_druid_displacement'], 'Shifting Power', ''),
    (['spell_shadow_vampiricaura'], 'Shred', 'to 4 points'),
    (['ability_ghoulfrenzy'], 'Rip', ''),
]

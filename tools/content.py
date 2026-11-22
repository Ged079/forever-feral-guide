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
    'Furor': 'Energy back when you shift into Cat Form. Barely matters, since you rarely leave it.',
    'Leader of the Pack': '+crit for you and your party. Worth this much to you alone; more to the raid.',
    'Feral Swiftness': 'Run speed and dodge. No DPS.',
    'Feral Charge': 'Bear charge. Utility.',
    'Feral Instinct': 'Bear Swipe damage. Tank talent.',
    'Thick Hide': 'Armor. Tank talent.',
    'Lacerate': 'Bear bleed. Tank talent.',
    'Primal Bite': 'Bear threat attack. Tank talent.',
}

BUILDS = {
    'cat': {
        'name': 'Cat', 'sub': 'Shred build, 2/2 Blood Frenzy', 'difficulty': 'Medium', 'main': True,
        'when': 'Pure damage. Shred is your builder, Rip and Rake stay up, Bite between Rips.',
    },
    'hybrid': {
        'name': 'Hybrid', 'sub': 'Claw build, can tank', 'difficulty': 'Easy',
        'when': 'Takes Thick Hide, Lacerate and Primal Bite so you can bear tank when needed. Claw replaces Shred, so you never need to be behind the boss.',
    },
}

OPENER = [
    ('Before the pull', 'Prowl about 1 s before, then Dash in as the pull starts.'),
    ('Faerie Fire', "Keep it on the boss if nobody else does. If the raid already has it up, skip it."),
    ('Into the loop', 'Rake, build points, Rip. The sim rarely opens with Ravage, so skip it.'),
]

# Each step: title, text, which builds it applies to
LOOP = [
    ('Shifting Power', 'At 53 energy or less, whenever it is off cooldown (8 s).', ['cat', 'hybrid']),
    ('Ferocious Bite (mid-fight)', 'At {bite_cp}+ combo points, while Rip still has {rip_left}+ s left and you have 75 energy (60 at 5 points, 45 with Clearcasting).', ['cat', 'hybrid']),
    ('Clearcasting → Shred', 'A free Shred whenever Clearcasting is up and Bite is not ready.', ['cat', 'hybrid']),
    ('Rip', 'When it is down, at {rip_cp} combo points, if 8+ s of the fight are left.', ['cat', 'hybrid']),
    ('Rake', 'When it is down, if 6+ s of the fight are left.', ['cat', 'hybrid']),
    ('{builder}', 'Your builder. Hold it back when you are pooling energy for a Bite.', ['cat', 'hybrid']),
    ('Innervate', 'Under 1400 mana with 30 energy or less, then shift back to Cat.', ['cat', 'hybrid']),
]
LOOP_FILL = {
    'cat': {'bite_cp': 4, 'rip_left': 3, 'rip_cp': '4 (5 if one more Shred still leaves energy for Rip right after)', 'builder': 'Shred'},
    'hybrid': {'bite_cp': 5, 'rip_left': 4, 'rip_cp': '4 (5 if one more Claw still leaves energy for Rip right after)', 'builder': 'Claw'},
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
    'RaceNightElf': ('Night Elf', 'Alliance', "Elune's Light: +10% crit for 15 s"),
    'RaceTauren': ('Tauren', 'Horde', 'War Stomp, +5% health'),
    'RaceHighOrderSkyborne': ('High Order Skyborne', 'Alliance', '+2% haste'),
    'RaceWindshaperSkyborne': ('Windshaper Skyborne', 'Horde', '+2% haste'),
}

ENCHANTS = {
    'Head': 'Lesser Arcane Amalgamation', 'Neck': 'Agility', 'Back': 'Agility', 'Chest': 'Greater Stats',
    'Wrist': 'Agility', 'Hands': 'Superior Agility', 'Legs': 'Lesser Arcane Amalgamation', 'Feet': 'Greater Agility',
    'Weapon': 'Superior Impact',
}

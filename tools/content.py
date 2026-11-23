# Hand-written prose for the guide. Numbers never live here: they come from results.json.

TALENT_TEXT = {
    'Shifting Power': 'Turns mana into energy instantly, on an 8 s cooldown. Use it at 53 energy or less, about {sp} times in a 3 minute fight. The biggest talent in the tree.',
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
    'Ferocity': 'Cheaper Claw and Rake. Rake is the part that matters here, since both builds Shred.',
    "Nature's Reach": '+2% hit per point. Each point saves you 20 hit rating on gear.',
    'Predatory Discipline': 'Ferocious Bite stops eating your extra energy but still hits harder with it. Lets you weave Bites in while Rip runs.',
    'Furor': 'Energy back when you shift into Cat Form, like after Innervate. Small, but it beats the utility talents.',
    'Leader of the Pack': '+crit for you and your party. Worth this much to you alone; more to the raid.',
    'Feral Swiftness': 'Run speed and dodge. No DPS, so the builds above skip it: its 2 points do more in Furor or Nature\u2019s Reach.',
    'Feral Charge': 'Bear charge. Utility; the builds above skip it. Taking it back costs about {fc} DPS (see the other builds we simmed).',
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
        'name': 'Hybrid', 'sub': 'Shred build that can tank', 'difficulty': 'Medium',
        'when': 'Keeps Thick Hide, Lacerate and Primal Bite so you can bear tank when needed, and still Shreds. Gives up Blood Frenzy for them.',
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
    ('Cooldowns', 'An on-use trinket in either slot and the Strength potion on one key, for the start of the fight. Passive trinkets ignore the /use lines.',
     '#showtooltip\n/use 13\n/use 14\n/use Mighty Rage Potion'),
]
MACRO_NOTE = 'These use the standard macro conditions ([form], [stealth], [@player]), the same kind the hunter guide’s macros use. Form 3 is Cat Form when you know Bear, Aquatic and Cat; check yours with /dump GetShapeshiftForm() if it differs.'



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


# Rank-by-rank talent tooltips. {0}, {1}, {2} are the talent's per-rank values from the sim's game data
# (one per effect curve), shown with the unit named in TIP_UNITS; 'unit@i' reads effect i instead.
# Talents without a curve are fixed text.
# Written from what each effect changes in the game files (WoWSims Forever, spells_auto_gen.go).
TIP_UNITS = {'pct': lambda v: abs(v), 'sec': lambda v: abs(v) / 1000, 'tenth': lambda v: abs(v) / 10,
             'cent': lambda v: abs(v) / 100, 'lvl': lambda v: v * 60, 'lvlpct': lambda v: v * 60 / 100}
TALENT_TIPS = {
    # Balance
    'Improved Wrath': ('Reduces the cast time of Wrath by {0} sec and its mana cost by {1}%.', ['sec', 'pct']),
    'Genesis': ('Increases the periodic damage and healing of your spells and abilities by {0}%, Rake, Rip, Lacerate '
                'and Pounce bleeds included, and the healing of Swiftmend by {1}%.', ['pct', 'pct']),
    'Moonglow': ('Reduces the mana cost of your damaging spells by {0}%.', ['pct']),
    'Improved Moonfire': ('Increases the critical strike chance of Moonfire by {0}% and its damage by {1}%.', ['pct', 'pct']),
    "Nature's Majesty": ('Increases your critical strike chance with spells and melee attacks by {0}%, in every form.', ['pct']),
    "Nature's Reach": ('Increases the range of your Balance spells and Faerie Fire by {0}%, and your chance to hit with '
                       'melee attacks and spells by {1}%.', ['pct', 'pct']),
    'Improved Entangling Roots': ('Increases the damage of Entangling Roots by {0}%.', ['pct']),
    "Nature's Splendor": ('Increases the duration of Moonfire and Rejuvenation by 3 sec, Regrowth by 6 sec and Insect Swarm by 2 sec.', []),
    'Insect Swarm': ('Swarms the target with insects for 12 sec, dealing Nature damage over time and lowering its chance to hit by 2%.', []),
    'Vengeance': ('Increases the critical strike damage bonus of your Arcane and Nature spells by {0}%.', ['pct']),
    'Improved Starfire': ('Reduces the cast time of Starfire by {0} sec and gives it a {1}% chance to stun the target for 3 sec.', ['sec', 'pct']),
    'Overgrowth': ('Increases the number of targets Entangling Roots can hold by {0}.', ['pct']),
    "Nature's Grace": ('When one of your spells critically strikes, your casting speed rises by 10% and your global '
                       'cooldown drops by 10% for 3 sec.', []),
    'Eclipse': ('Each Wrath that lands cuts the cast time of your next 2 Starfires by {1} sec. Stores up to 4 charges, '
                'which last 15 sec.', ['pct', 'sec']),
    'Moonfury': ('Increases the damage of your Arcane and Nature spells by {0}%.', ['pct']),
    'Moonkin Form': ('Shapeshift into Moonkin Form, giving your party 3% spell critical strike chance. In the form, '
                     'Omen of Clarity triggers twice as often, with half the time between triggers.', []),
    # Feral Combat
    'Ferocity': ('Reduces the cost of Maul, Swipe and Primal Bite by {0} Rage, and of Claw and Rake by {1} Energy.', ['tenth', 'pct']),
    'Furor': ('When you shift into Cat Form you get back {1}% of the Energy you had when you left it, which keeps '
              'regenerating while you are out of form. Shifting into Bear or Dire Bear Form has a {0}% chance to give 10 Rage.', ['pct', 'pct']),
    'Feral Swiftness': ('Increases your chance to dodge by {0}% and your movement speed in Cat Form by {1}%.', ['pct', 'pct']),
    'Feral Instinct': ('Improves your stealth while Prowling by {0} and increases the damage of Swipe by {1}%.', ['pct', 'pct']),
    'Brutal Impact': ('Increases the stun of Bash and Pounce by {0} sec and reduces the cooldown of Bash by {1} sec.', ['sec', 'sec']),
    'Thick Hide': ('Increases your armor by {1} (at level 60), plus {0} armor for each point of defense from gear and buffs. '
                   'Bear and Dire Bear Form multiply both.', ['cent', 'lvl']),
    'Shredding Attacks': ('Reduces the Energy cost of Shred by {0} and the Rage cost of Lacerate by {1}.', ['pct', 'tenth']),
    'Savage Fury': ('Increases the damage of Claw, Rake, Shred, Maul and Swipe by {0}%, and of the Rake bleed by {1}%.', ['pct', 'pct']),
    'Feral Charge': ('Cat Form: leap to an enemy 8 to 25 yards away (30 sec cooldown). Bear Form: charge an enemy 8 to 25 '
                     'yards away for 5 Rage, interrupting its spellcasting and rooting it for 4 sec (15 sec cooldown).', []),
    'Sharpened Claws': ('Increases your critical strike chance in Cat, Bear and Dire Bear Form by {0}%.', ['pct']),
    'Predatory Strikes': ('Increases your attack power in Cat, Bear and Dire Bear Form by {0}% of your level, {1} at level 60.', ['pct', 'lvlpct@0']),
    'Lacerate': ('Bear Form, 15 Rage: lacerates the target, causing a bleed for 15 sec that stacks up to 5 times. '
                 'Generates extra threat.', []),
    'Predatory Discipline': ('Ferocious Bite no longer spends your extra Energy, but still deals the extra damage for it.', []),
    'Blood Frenzy': ('In Bear and Dire Bear Form, your critical strikes have a {0}% chance to give 5 Rage. In Cat Form, '
                     'critical strikes with combo point abilities have a {1}% chance to add an extra combo point.', ['pct', 'pct']),
    'Leader of the Pack': ('In Cat, Bear or Dire Bear Form, increases the critical strike chance of party members within '
                           '45 yards by 3%.', []),
    'Natural Instinct': ('Increases the critical strike damage bonus of your melee abilities by {0}%, and your healing by '
                         '{1}% of your Intellect.', ['pct', 'pct']),
    'Rend and Tear': ('Increases the damage of your melee abilities and bleeds against bleeding targets by {0}%. '
                      'Auto attacks are not affected.', ['pct']),
    'Natural Reaction': ('Increases your chance to dodge by {0}%. In Bear Form, each dodge has a {1}% chance to give 5 Rage.', ['pct', 'pct']),
    'Primal Bite': ('Bear Form, 20 Rage: bite the target for 100% weapon damage plus 42, generating high threat. 6 sec cooldown.', []),
    'Shifting Power': ('Cat Form: costs 55% of base mana to instantly gain 40 Energy. 8 sec cooldown and a 1 sec global '
                       'cooldown; not usable at full Energy.', []),
    # Restoration
    "Nature's Focus": ('Gives Healing Touch, Regrowth, Tranquility, Wrath, Starfire, Hurricane and Entangling Roots a {0}% '
                       'chance to lose no casting time when you take damage.', ['pct']),
    'Heart of the Wild': ('Increases your Intellect by {0}%. In Bear and Dire Bear Form your Stamina rises by {1}%, and in '
                          'Cat Form your Strength by {2}%.', ['pct', 'pct', 'pct']),
    'Naturalist': ('Reduces the cast time of Healing Touch and Wild Growth by {0} sec, and increases all damage you deal by {1}%, '
                   'physical included.', ['sec', 'pct']),
    'Reflection': ('Allows {0}% of your mana regeneration to continue while casting.', ['pct']),
    'Natural Shapeshifter': ('Reduces the mana cost of your shapeshifts and of Shifting Power by {0}%.', ['pct']),
    'Subtlety': ('Reduces the threat of your Arcane and Nature spells by {0}%.', ['pct']),
    'Gift of Nature': ('Increases the healing of Healing Touch, Regrowth, Swiftmend and Tranquility by {0}%, and of your '
                       'heals over time by {1}%.', ['pct', 'pct']),
    'Bloom': ('When your Rejuvenation or Regrowth runs its full duration, the target is healed for 100% of your Spirit.', []),
    'Tranquil Spirit': ('Reduces the mana cost of Healing Touch and Tranquility by {0}%.', ['pct']),
    'Improved Rejuvenation': ('Increases the healing of Rejuvenation by {0}%.', ['pct']),
    'Swiftmend': ('Consumes a Rejuvenation or Regrowth on a friendly target to instantly heal it for the whole effect. '
                  '15 sec cooldown.', []),
    "Nature's Swiftness": ('Your next Nature spell with a cast time becomes instant. 3 min cooldown.', []),
    'Living Spirit': ('Increases your Spirit by {0}%.', ['pct']),
    'Improved Tranquility': ('Reduces the threat of Tranquility by {0}% and its cooldown by {1}%.', ['pct', 'pct']),
    'Improved Regrowth': ('Increases the critical effect chance of Regrowth by {0}%.', ['pct']),
    'Wild Growth': ('Heals up to 5 party or raid members within 15 yards of the target over 7 sec. 6 sec cooldown.', []),
}

def compute_effective_damage(base_damage, attack_range, attack_speed, splash_range):
    """
    Compute an effective damage value as a function of:
      - base damage,
      - attack speed (attacks per second),
      - attack range (longer range might mean earlier engagement),
      - splash_range (contributing to area damage).
    Example formula (tunable):
      effective_damage = base_damage * attack_speed * (1 + splash_range / 2) * (attack_range / 5)
    """
    return base_damage * attack_speed * (1 + splash_range / 2) * (1 + attack_range / 6)

def compute_effective_hp(base_health, attack_range):
    """
    Compute an effective HP value as a function of:
      - base health,
      - attack range (a longer range might imply increased vulnerability).
    Example formula (tunable):
      effective_hp = base_health * (1 + attack_range / 10)
    """
    return base_health * (1 + attack_range / 10)

# Base stats: (cost, base_damage, attack_range, attack_speed, splash_range, discovery_range, base_health)
# Note: These values come from your provided table.
base_stats = {
    "Archer":    (3, 118, 5.0, 6, 0, 8, 334),
    "Minion":    (3, 129, 2.0, 6, 0, 4, 252),
    "Knight":    (3, 221, 0,   6, 0, 7, 1938),
    "Skeleton":  (3, 89,  0,   6, 0, 4, 89),
    "Dragon":    (4, 176, 3.5, 6, 1, 5, 1267),
    "Valkyrie":  (4, 195, 0,   6, 1, 7, 2097),
    "Musketeer": (4, 239, 6.0, 3, 0, 8, 792),
    "Giant":     (5, 337, 0,   2, 0, 7, 5423),
    "Prince":    (5, 392, 0,   6, 0, 5, 1920),
    "Barbarian": (3, 161, 0,   3, 0, 5, 736),
    "Balloon":   (5, 424, 0,   3, 1, 5, 2226),
    "Wizard":    (5, 410, 5.5, 6, 1, 8, 1100)
}

# "number" for each troop (number of units per card) from the provided class definitions:
troop_numbers = {
    "Archer":    2,
    "Minion":    3,
    "Knight":    1,
    "Skeleton":  10,
    "Dragon":    1,
    "Valkyrie":  1,
    "Musketeer": 1,
    "Giant":     1,
    "Prince":    1,
    "Barbarian": 3,
    "Balloon":   1,
    "Wizard":    1
}

# Simplified flags for each troop.
# Flags: splash, fly, walk, air, gnd, tank, charge.
flags_data = {
    "Archer":    {"splash": False, "fly": False, "walk": True,  "air": True,  "gnd": False,  "tank": False, "charge": False},
    "Minion":    {"splash": False, "fly": True,  "walk": False, "air": True,  "gnd": False,  "tank": False, "charge": False},
    "Knight":    {"splash": False, "fly": False, "walk": True,  "air": False, "gnd": True,  "tank": True,  "charge": False},
    "Skeleton":  {"splash": False, "fly": False, "walk": True,  "air": False, "gnd": True,  "tank": False, "charge": False},
    "Dragon":    {"splash": True,  "fly": True,  "walk": False, "air": True,  "gnd": False,  "tank": False, "charge": False},
    "Valkyrie":  {"splash": True,  "fly": False, "walk": True,  "air": False, "gnd": True,  "tank": False, "charge": False},
    "Musketeer": {"splash": False, "fly": False, "walk": True,  "air": True,  "gnd": False,  "tank": False, "charge": False},
    "Giant":     {"splash": False, "fly": False, "walk": True,  "air": False, "gnd": True,  "tank": True,  "charge": False},
    "Prince":    {"splash": False, "fly": False, "walk": True,  "air": False, "gnd": True,  "tank": False, "charge": True},
    "Barbarian": {"splash": False, "fly": False, "walk": True,  "air": False, "gnd": True,  "tank": False, "charge": False},
    "Balloon":   {"splash": True,  "fly": True,  "walk": False, "air": False, "gnd": True,  "tank": False, "charge": False},
    "Wizard":    {"splash": True,  "fly": False, "walk": True,  "air": True,  "gnd": False,  "tank": False, "charge": False}
}

# Build the associative table.
troops = {}

for troop_name, stats in base_stats.items():
    cost, base_dmg, atk_range, atk_speed, splash_range, discovery_range, base_hp = stats
    number = troop_numbers[troop_name]

    # Compute effective damage (scaled by number)
    eff_dmg = compute_effective_damage(base_dmg, atk_range, atk_speed, splash_range) * number

    if flags_data[troop_name]["fly"] or flags_data[troop_name]["air"]:
        air_dmg = gnd_dmg = eff_dmg
    else:
        air_dmg = 0
        gnd_dmg = eff_dmg

    # Compute effective hit points (scaled by number)
    eff_hp = compute_effective_hp(base_hp, atk_range) * number

    troops[troop_name] = {
        "cost": cost,
        "flags": set(),
        "air_dmg": round(air_dmg, 2),
        "gnd_dmg": round(gnd_dmg, 2),
        "hp": round(eff_hp, 2),
        "number": number,
        "range": discovery_range,
    }
    
    for flag, present in flags_data[troop_name].items():
        if present:
            troops[troop_name]["flags"].add(flag)
    

if __name__ == "__main__":
    print("{")
    for name, data in troops.items():
        print(f'\t"{name}": \x7b "cost": {data['cost']}, "flags": {data['flags']}, "air_dmg": {data['air_dmg']}, "gnd_dmg": {data['gnd_dmg']}, "hp": {data['hp']}, "range": {data['range']} \x7d,')
        # print(f"Troop: {name}")
        # print(f"  Cost: {data['cost']}")
        # print(f"  Flags: {data['flags']}")
        # print(f"  Air Damage: {data['air_dmg']}")
        # print(f"  Ground Damage: {data['gnd_dmg']}")
        # print(f"  HP: {data['hp']}\n")
    print("}")

# Godlike LeviOsa Killer Bot
# Features:
# - Full elixir & cycle tracking
# - UID-aware opponent troop memory
# - Role-based behavior (DEFENSE, OFFENSE, NEUTRAL)
# - Splash baiting and response
# - Split-lane pressure
# - Adaptive troop scoring
# - All state in team_signal

# ✨ May the Splash be with you.

import random
from teams.helper_function import Troops, Utils

troops = [
    Troops.wizard, Troops.minion, Troops.archer, Troops.musketeer,
    Troops.dragon, Troops.skeleton, Troops.valkyrie, Troops.prince
]
team_name = "GODMODE"
deploy_list = Troops([])
team_signal = "||10"

# Deployment logic entry point
def deploy(arena_data: dict):
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

# Godlike logic core
def logic(arena_data: dict):
    global team_signal

    # === Parse state ===
    troops_data = Troops.troops_data
    my = arena_data["MyTower"]
    opp = arena_data["OppTroops"]
    elixir = my.total_elixir
    timer = my.game_timer

    # Signal layout: name uid,name uid|self_cycle|opp_elixir|splash_frame|splash_bait
    parts = team_signal.split("|") + [""] * 5
    deck_raw, cycle_raw, opp_elixir, splash_frame, bait_success = parts[:5]
    cycle = list(filter(None, cycle_raw.split(",")))
    opp_elixir = float(opp_elixir)
    if splash_frame=='':
        splash_frame = 0
    else:
        splash_frame = int(splash_frame)
    if bait_success=='':
        bait_success = 0
    else:
        bait_success = int(bait_success)

    # Track opponent troops by UID
    opp_deck = {}
    for troop in opp:
        name, uid = troop.name, str(troop.uid)
        if name not in opp_deck:
            opp_deck[name] = []
        if uid not in opp_deck[name]:
            opp_deck[name].append(uid)

    # Remove disappeared UIDs
    past_deck = {}
    if deck_raw:
        for entry in deck_raw.split(","):
            tokens = entry.strip().split()
            if not tokens: continue
            name, uids = tokens[0], tokens[1:]
            still = [uid for uid in uids if any(t.name == name and str(t.uid) == uid for t in opp)]
            if still:
                past_deck[name] = still

    # Detect new splash troop
    if any(name in ["Wizard", "Valkyrie"] for name in opp_deck):
        splash_frame = timer

    # === Compute threat level ===
    air_threat = sum(1 for t in opp if t.type == "air")
    ground_threat = sum(1 for t in opp if t.type == "ground")
    clustered = [t for t in opp if Utils.calculate_distance(t.position, my.position, type_troop=False) < 9]

    # === Role Assignment ===
    def determine_role():
        if air_threat >= 3 or len(clustered) >= 4 or ground_threat >= 5:
            return "DEFENSE"
        if timer > 1400 or opp_elixir < 3 or my.health > 4000:
            return "OFFENSE"
        return "NEUTRAL"

    role = determine_role()

    # === Splash baiting logic ===
    bait_window = (timer - splash_frame) > 250
    if bait_window and elixir >= 3 and bait_success < 3:
        if "Skeleton" in my.deployable_troops:
            deploy_list.deploy_skeleton(pos_defense(my.position))
            bait_success += 1
            return

    # === Post-splash counterattack ===
    if (timer - splash_frame) < 40 and bait_success:
        for air_unit in ["Minion", "Dragon"]:
            if air_unit in my.deployable_troops and elixir >= troops_data[air_unit].elixir:
                getattr(deploy_list, f"deploy_{air_unit.lower()}")(pos_attack(my.position))
                return

    # === Full Offensive Wave ===
    if role == "OFFENSE" and elixir >= 7:
        for win in ["Prince", "Dragon"]:
            if win in my.deployable_troops and elixir >= troops_data[win].elixir:
                getattr(deploy_list, f"deploy_{win.lower()}")(lane_left(my.position))
        for support in ["Minion", "Archer"]:
            if support in my.deployable_troops and elixir >= troops_data[support].elixir:
                getattr(deploy_list, f"deploy_{support.lower()}")(lane_right(my.position))
        return

    # === Defense Cluster Handling ===
    if role == "DEFENSE":
        if air_threat >= 2:
            for air_def in ["Musketeer", "Archer", "Wizard"]:
                if air_def in my.deployable_troops and elixir >= troops_data[air_def].elixir:
                    getattr(deploy_list, f"deploy_{air_def.lower()}")(pos_defense(my.position))
                    return
        if len(clustered) >= 3:
            for splash in ["Wizard", "Valkyrie"]:
                if splash in my.deployable_troops and elixir >= troops_data[splash].elixir:
                    getattr(deploy_list, f"deploy_{splash.lower()}")(pos_defense(my.position))
                    return

    # === Mid-game value cycle ===
    if elixir >= 5:
        for mid in ["Valkyrie", "Skeleton"]:
            if mid in my.deployable_troops and elixir >= troops_data[mid].elixir:
                getattr(deploy_list, f"deploy_{mid.lower()}")(pos_defense(my.position))
                return

    if elixir >= 3:
        for cheap in ["Archer", "Minion"]:
            if cheap in my.deployable_troops and elixir >= troops_data[cheap].elixir:
                getattr(deploy_list, f"deploy_{cheap.lower()}")(pos_defense(my.position))
                return

    # === Update state ===
    last = deploy_list.list_[-1][0] if deploy_list.list_ else None
    if last:
        cycle.append(last)
    cycle = cycle[-4:]

    opp_deck_final = {**past_deck, **opp_deck}
    opp_str = ",".join(f"{k} {' '.join(v)}" for k, v in opp_deck_final.items())
    team_signal = f"{opp_str}|{','.join(cycle)}|{opp_elixir:.2f}|{splash_frame}|{bait_success}"

# === Position Utilities ===
def pos_defense(pos):
    x = pos[0] + random.randint(-5, 5)
    y = pos[1] + random.randint(2, 10)
    return (max(0, min(49, x)), max(0, min(49, y)))

def pos_attack(pos):
    x = pos[0] + random.randint(-3, 3)
    y = pos[1] + random.randint(8, 12)
    return (max(0, min(49, x)), max(0, min(49, y)))

def lane_left(pos):
    x = max(0, pos[0] - 10)
    y = pos[1] + random.randint(3, 8)
    return (x, min(49, y))

def lane_right(pos):
    x = min(49, pos[0] + 10)
    y = pos[1] + random.randint(3, 8)
    return (x, min(49, y))

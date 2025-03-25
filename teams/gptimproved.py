import random
from teams.helper_function import Troops, Utils

team_name = "Spash Royale"
troops = [
    Troops.wizard, Troops.minion, Troops.archer, Troops.musketeer,
    Troops.dragon, Troops.skeleton, Troops.valkyrie, Troops.giant
]
deploy_list = Troops([])
team_signal = ""

def deploy(arena_data: dict):
    """
    DON'T TEMPER DEPLOY FUNCTION
    """
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

def logic(arena_data: dict):
    global team_signal

    troops_data = Troops.troops_data
    my_tower = arena_data["MyTower"]
    opp_tower = arena_data["OppTower"]
    my_troops = arena_data["MyTroops"]
    opp_troops = arena_data["OppTroops"]
    elixir = my_tower.total_elixir
    timer = my_tower.game_timer

    # Deploy wizard if possible
    if "Wizard" in my_tower.deployable_troops:
        deploy_list.deploy_wizard((offense_position(my_tower.position)))

    # 1. Update team_signal with closest enemy name
    if opp_troops:
        closest_enemy = min(opp_troops, key=lambda t: Utils.calculate_distance(t.position, my_tower.position, type_troop=False))
        new_signal = closest_enemy.name
        if new_signal not in team_signal:
            parts = team_signal.split(",") if team_signal else []
            parts.append(new_signal)
            team_signal = ",".join(parts)[:200]

    # 2. End-Game All-Out Push (Last 10% of Game)
    if timer > 1500:
        # Aggressively push every available unit
        if "Giant" in my_tower.deployable_troops and elixir >= troops_data["Giant"].elixir:
            deploy_list.deploy_giant(offense_position(my_tower.position))
        if "Dragon" in my_tower.deployable_troops and elixir >= troops_data["Dragon"].elixir:
            deploy_list.deploy_dragon(offense_position(my_tower.position))
        if "Minion" in my_tower.deployable_troops and elixir >= troops_data["Minion"].elixir:
            deploy_list.deploy_minion(offense_position(my_tower.position))
        if "Archer" in my_tower.deployable_troops and elixir >= troops_data["Archer"].elixir:
            deploy_list.deploy_archer(offense_position(my_tower.position))
        return

    # 3. Adaptive Defense: React to Air & Group Threats
    # Detect air threats that are within a 15-unit radius
    air_threats = [t for t in opp_troops if t.type == "air" and Utils.calculate_distance(t.position, my_tower.position, type_troop=False) < 15]
    if air_threats:
        if "Musketeer" in my_tower.deployable_troops and elixir >= troops_data["Musketeer"].elixir:
            deploy_list.deploy_musketeer(defense_position(my_tower.position))
            return
        elif "Archer" in my_tower.deployable_troops and elixir >= troops_data["Archer"].elixir:
            deploy_list.deploy_archer(defense_position(my_tower.position))
            return

    # If enemy troop count is high, use splash damage to counter a swarm
    if len(opp_troops) >= 5:
        if "Wizard" in my_tower.deployable_troops and elixir >= troops_data["Wizard"].elixir:
            deploy_list.deploy_wizard(defense_position(my_tower.position))
            return

    # 4. High-Elixir Offensive Push: Mixed Attack
    if elixir >= 8:
        # Deploy a coordinated push using heavy and supporting units
        if "Giant" in my_tower.deployable_troops and elixir >= troops_data["Giant"].elixir:
            deploy_list.deploy_giant(offense_position(my_tower.position))
        if "Dragon" in my_tower.deployable_troops and elixir >= troops_data["Dragon"].elixir:
            deploy_list.deploy_dragon(offense_position(my_tower.position))
        if "Minion" in my_tower.deployable_troops and elixir >= troops_data["Minion"].elixir:
            deploy_list.deploy_minion(offense_position(my_tower.position))
        if "Archer" in my_tower.deployable_troops and elixir >= troops_data["Archer"].elixir:
            deploy_list.deploy_archer(offense_position(my_tower.position))
        return

    # 5. Moderate Elixir: Balanced Reaction
    if elixir >= 5:
        # If a ground push is viable, use Valkyrie or Skeleton for defense/support
        if "Valkyrie" in my_tower.deployable_troops and elixir >= troops_data["Valkyrie"].elixir:
            deploy_list.deploy_valkyrie(offense_position(my_tower.position))
            return
        elif "Skeleton" in my_tower.deployable_troops and elixir >= troops_data["Skeleton"].elixir:
            deploy_list.deploy_skeleton(defense_position(my_tower.position))
            return

    # 6. Cheap Cycle: Maintain Presence
    if elixir >= 3:
        # Cycle through the cheapest units to keep pressure
        for unit in ["Archer", "Minion", "Skeleton"]:
            if unit in my_tower.deployable_troops and elixir >= troops_data[unit].elixir:
                getattr(deploy_list, f"deploy_{unit.lower()}")(defense_position(my_tower.position))
                return

    # 7. Else: Save Elixir
    pass

# Position Helper Functions
def defense_position(tower_pos):
    """
    Returns a slightly randomized position around our tower for defense.
    """
    x = tower_pos[0] + random.randint(-4, 4)
    y = tower_pos[1] + random.randint(-4, 4)
    return (max(0, min(49, x)), max(0, min(49, y)))

def offense_position(tower_pos):
    """
    Returns a forward position to pressure the enemy tower,
    with added randomness to avoid predictability.
    """
    x = tower_pos[0] + random.randint(6, 10)
    y = tower_pos[1] + random.randint(-3, 3)
    return (max(0, min(49, x)), max(0, min(49, y)))

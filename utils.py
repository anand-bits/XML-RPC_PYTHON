from config import N


def print_battlefield_layout(battlefield, soldiers, missile_position=None, impact_radius=None, commander_id=None):
    # Create a copy of the battlefield to modify for printing
    display_field = [row.copy() for row in battlefield]

    # Mark soldiers on the display field
    for soldier in soldiers:
        if soldier["alive"]:
            display_field[soldier["y"]][soldier["x"]] = str(soldier["id"])

    # Mark the missile's impact zone on the display field
    if missile_position and impact_radius:
        x, y = missile_position
        for dx in range(-impact_radius, impact_radius + 1):
            for dy in range(-impact_radius, impact_radius + 1):
                if 0 <= x + dx < N and 0 <= y + dy < N:
                    current_value = display_field[y + dy][x + dx]
                    display_field[y + dy][x + dx] = 'X' if current_value == 0 else f"X{current_value}"

    # Print the display field


    # Print additional information
    print("\nSoldiers:")
    for soldier in soldiers:
        status = "Alive" if soldier["alive"] else "Dead"
        role = "Commander" if soldier["id"] == commander_id else "Soldier"
        print(f"ID: {soldier['id']}, Position: ({soldier['x']}, {soldier['y']}), Status: {status}, Role: {role}")

    if missile_position and impact_radius:
        print(f"\nMissile landed at: {missile_position} with impact radius: {impact_radius}")
        casualties = [soldier["id"] for soldier in soldiers if
                      not soldier["alive"] and abs(soldier["x"] - x) <= impact_radius and abs(
                          soldier["y"] - y) <= impact_radius]
        if casualties:
            print(f"Soldiers {', '.join(map(str, casualties))} died due to the missile.")

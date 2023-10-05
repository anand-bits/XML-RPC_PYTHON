import xmlrpc.server
import xmlrpc.client
import logging
from client import soldiers
from config import N, M, t, Si, T
import random
import time
from utils import print_battlefield_layout

# Global state of Battlefield
logging.basicConfig(filename='server_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
battlefield = [[0 for _ in range(N)] for _ in range(N)]
commander = random.randint(1, M)  # Initialize the commander which is soldier and have soldier id.
#client running on Local Host

client_url = "http://localhost:8000/"
alive_soldiers = list(range(1, M + 1))

# soldier speed levels according to the assignment we have to take random
soldier_speeds = {1: 1, 2: 2, 3: 3, 4: 4}



def simulate_missile_strike():
    x, y = random.randint(3, N - 4), random.randint(3, N - 4)
    impact_radius = random.choice([1, 2, 3, 4])

    print(f"Missile approaching at ({x}, {y}) with impact radius {impact_radius}")

    # tell the  client about the missile from server and tell the impact area
    try:
        client = xmlrpc.client.ServerProxy(client_url)
        client.handle_missile_notification(x, y, impact_radius)
    except Exception as e:
        print(f"Failed to notify client at {client_url}. Error: {e}")

    # Check for casualties based on soldier's speed and update the commander if necessary ,if the commander is died than election will takes place.
    check_casualties(x, y, impact_radius)
    check_commander_status()

    return x, y, impact_radius
def check_casualties(missile_x, missile_y, impact_radius):
    global commander, alive_soldiers
    casualties = []

    for soldier_id in alive_soldiers.copy():
        from client import soldiers
        soldier = soldiers[soldier_id - 1]

        if not soldier["alive"]:
            continue

        speed = soldier_speeds.get(soldier["speed"], 0)
        distance_to_impact = max(0, abs(soldier["x"] - missile_x), abs(soldier["y"] - missile_y))

        # Check if the soldier is within the impact radius and it's not the commander
        if soldier_id != commander and speed < impact_radius - distance_to_impact and not (missile_x == soldier["x"] and missile_y == soldier["y"]):
            soldier["alive"] = False
            casualties.append(soldier_id)

    # Check if the commander is in the impact area
    commander_distance_to_impact = max(0, abs(soldiers[commander - 1]["x"] - missile_x), abs(soldiers[commander - 1]["y"] - missile_y))
    if commander_distance_to_impact <= impact_radius:
        print("\nCommander died!")
        alive_soldiers.remove(commander)
        if alive_soldiers:
            commander = random.choice(alive_soldiers)
            print(f"Election took place. New commander chosen: Soldier {commander}")

    if casualties:
        print(f"Soldiers {', '.join(map(str, casualties))} died due to the missile.")
        alive_soldiers = [soldier_id for soldier_id in alive_soldiers if soldier_id not in casualties]


def get_safe_moves(soldier_id, x, y, impact_radius):
    safe_moves = []

    for dx in range(-1, 2):
        for dy in range(-1, 2):
            new_x, new_y = x + dx, y + dy

            if (
                0 <= new_x < N
                and 0 <= new_y < N
                and not (dx == 0 and dy == 0)
                and (abs(new_x - x) + abs(new_y - y) <= impact_radius)
            ):
                safe_moves.append((soldier_id, new_x, new_y))

    return safe_moves

#after every iteration The commander status will be shown ..if died Than election will take place.

def check_commander_status():
    global commander, alive_soldiers
    print(f"Checking status of commander: Soldier {commander} (Alive: {commander in alive_soldiers})")

# Function to log battlefield state
def log_battlefield_state():
    battlefield_state = "\n".join(["".join(map(str, row)) for row in battlefield])
    logging.info(f"Battlefield state:\n{battlefield_state}")

if __name__ == "__main__":
    print("Server started. Waiting for initial setup...")
    time.sleep(10)  # Wait for 10 seconds before starting missile strikes

    num_iterations = T // t  # Calculate the number of iterations based on the missile strike interval `t`


    for _ in range(num_iterations):
        time.sleep(t)
        missile_x, missile_y, impact_radius = simulate_missile_strike()

        # Log the battlefield state including safe moves for soldiers
        log_battlefield_state()

        # Print safe moves for soldiers
        for soldier_id in alive_soldiers:
            soldier = soldiers[soldier_id - 1]
            if soldier["alive"]:
                safe_moves = get_safe_moves(soldier_id, soldier["x"], soldier["y"], impact_radius)
                print(f"Safe moves for Soldier {soldier_id}: {safe_moves}")

        print_battlefield_layout(battlefield, soldiers, (missile_x, missile_y), impact_radius, commander)

    # Check the battle outcome
    if len(alive_soldiers) > M // 2:
        message = "Battle won! More than 50% soldiers are alive."
        print(message)
        logging.info(message)
    else:
        message = "Battle lost! Less than or equal to 50% soldiers are alive."
        print(message)
        logging.info(message)
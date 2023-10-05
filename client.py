import xmlrpc.server
from config import N, M, Si
import random

soldiers = [{"id": i, "x": random.randint(0, N-1), "y": random.randint(0, N-1), "speed": random.choice(Si), "alive": True} for i in range(1, M+1)]

def is_in_impact_zone_modified(soldier_x, soldier_y, x, y, impact_radius):
    return abs(soldier_x - x) <= impact_radius and abs(soldier_y - y) <= impact_radius

def handle_missile_notification(x, y, impact_radius):
    print(f"Received missile approach notification at ({x}, {y}) with impact radius {impact_radius}")
    for soldier in soldiers:
        if soldier["alive"]:
            take_shelter_modified(soldier, x, y, impact_radius)


def take_shelter_modified(soldier, x, y, impact_radius):
    if is_in_impact_zone_modified(soldier["x"], soldier["y"], x, y, impact_radius):
        possible_moves = [(i, j) for i in range(-soldier["speed"], soldier["speed"] + 1)
                                  for j in range(-soldier["speed"], soldier["speed"] + 1)
                                  if 0 <= soldier["x"] + i < N and 0 <= soldier["y"] + j < N]
        safe_moves = [(i, j) for i, j in possible_moves if not is_in_impact_zone_modified(soldier["x"] + i, soldier["y"] + j, x, y, impact_radius)]
        if safe_moves:
            dx, dy = random.choice(safe_moves)
            soldier["x"] += dx
            soldier["y"] += dy
        else:
            soldier["alive"] = False

def is_alive_modified(soldier_id):
    print(f"Checking if Soldier {soldier_id} is alive")
    soldier = next((s for s in soldiers if s["id"] == soldier_id), None)
    return soldier["alive"] if soldier else False

def elect_new_commander_modified():
    alive_soldiers = [s for s in soldiers if s["alive"]]
    new_commander = random.choice(alive_soldiers)
    return new_commander["id"]

if __name__ == "__main__":
    client_server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    client_server.register_function(handle_missile_notification, "notify_missile_approach")
    client_server.register_function(is_alive_modified, "is_alive")
    client_server.register_function(elect_new_commander_modified, "elect_new_commander")
    print(f"Client server started on port 8000")
    client_server.serve_forever()

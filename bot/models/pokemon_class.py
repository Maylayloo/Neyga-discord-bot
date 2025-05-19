import random
import requests


class Pokemon:
    def __init__(self, name):
        self.name = name
        url = f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Nie znaleziono Pokémona.")
        data = response.json()
        self.hp = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'hp')
        self.attack = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'attack')
        self.defense = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'defense')
        self.sprite = data['sprites']['front_default']

        all_moves = [move['move']['name'] for move in data['moves']]
        self.possible_moves = all_moves
        selected_moves = random.sample(all_moves, min(4, len(all_moves)))

        self.moves = {}
        for move_name in selected_moves:
            move_url = f"https://pokeapi.co/api/v2/move/{move_name}"
            move_resp = requests.get(move_url)
            if move_resp.status_code == 200:
                move_data = move_resp.json()
                self.moves[move_name] = move_data['power']
            else:
                self.moves[move_name] = None


def calculate_damage(attacker, defender, move_power):
    if move_power is None:
        return random.randint(1, 5)

    modifier = random.uniform(0.85, 1.0)
    base_damage = ((((2 * 50 / 5 + 2) * move_power * (attacker.attack / defender.defense)) / 50) + 2) / 2
    return int(base_damage * modifier)

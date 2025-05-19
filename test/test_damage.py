from unittest.mock import patch

from bot.main import calculate_damage


class DummyPokemon:
    def __init__(self, attack, defense):
        self.attack = attack
        self.defense = defense


def test_damage_with_known_move_power():
    attacker = DummyPokemon(attack=100, defense=50)
    defender = DummyPokemon(attack=80, defense=40)
    move_power = 60

    with patch("random.uniform", return_value=0.9):
        damage = calculate_damage(attacker, defender, move_power)

    expected_base = ((((2 * 50 / 5 + 2) * move_power * (attacker.attack / defender.defense)) / 50) + 2) / 2
    expected_damage = int(expected_base * 0.9)

    assert damage == expected_damage


def test_damage_with_none_power():
    attacker = DummyPokemon(attack=100, defense=100)
    defender = DummyPokemon(attack=80, defense=100)

    with patch("random.randint", return_value=4):
        damage = calculate_damage(attacker, defender, None)

    assert damage == 4


@patch("random.uniform", return_value=0.99)
def test_mewtwo_tri_attack(mocked_rand):
    mewtwo = DummyPokemon(110, 90)
    blissey = DummyPokemon(10, 10)
    dmg = calculate_damage(mewtwo, blissey, 80)
    assert 192 <= dmg <= 194


@patch("random.uniform", return_value=0.85)
def test_blissey_mega_kick(mocked_rand):
    blissey = DummyPokemon(10, 10)
    mewtwo = DummyPokemon(110, 90)
    dmg = calculate_damage(blissey, mewtwo, 120)
    assert 2 <= dmg <= 4

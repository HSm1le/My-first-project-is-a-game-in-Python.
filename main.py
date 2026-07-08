import random as r
import json
import os
from typing import Tuple

SAVE_FILE = "save.json"


# Инициализация 
name = input("Ведите ваш никнейм: ")

# базовые параметры (инициализация через init_game)
hp = 0
coins = 0
damage = 0

# Зелья — единая структура
potions = {
    "weak": {"name": "Слабое зелье", "heal": 25, "count": 0},
    "medium": {"name": "Среднее зелье", "heal": 50, "count": 0},
    "strong": {"name": "Сильное зелье", "heal": 150, "count": 0},
    "berserk": {"name": "Зелье Берсерка", "heal": 325, "count": 0},
    "gods": {"name": "Зелье Богов", "heal": 1500, "count": 0},
}

# список имён монстров
MONSTER_NAMES = [
    "Реми", "Чи-Хуа-Хуа","Слизень",
    "Крысолюд", "Гоблин", "Разбойник", "Скелет"
]


# Вспомогательные функции
def print_parameters():
    print(
        "\nУ тебя:\n"
        f"{hp} здоровья,\n"
        f"{coins} монет,\n"
        f"{damage} урона,\n"
        f"{total_potions()} зелий.\n"
    )


def print_hp():
    print("У тебя", hp, "жизней")


def print_coins():
    print("У тебя", coins, "монет\n")


def print_damage():
    print("У тебя", damage, "урона")


def total_potions() -> int:
    return sum(p["count"] for p in potions.values())


def print_potions():
    print("\nУ тебя:")
    any_p = False
    for p in potions.values():
        if p["count"] > 0:
            print(f"- {p['name']} x{p['count']} (восстан. {p['heal']} HP)")
            any_p = True
    if not any_p:
        print("Нет зелий.")


# Сохранение / загрузка
def save_game():
    data = {
        "hp": hp,
        "coins": coins,
        "damage": damage,
        "potions": {k: v["count"] for k, v in potions.items()},
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Игра сохранена!")
    except Exception as e:
        print("Ошибка при сохранении:", e)


def load_game() -> bool:
    global hp, coins, damage
    if not os.path.exists(SAVE_FILE):
        print("Сохранений не найдено.")
        return False
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        hp = data.get("hp", 50)
        coins = data.get("coins", 15)
        damage = data.get("damage", 10)
        saved_potions = data.get("potions", {})
        for k in potions.keys():
            potions[k]["count"] = saved_potions.get(k, 0)
        print("Сохранение загружено!")
        print_parameters()
        return True
    except Exception as e:
        print("Ошибка при загрузке:", e)
        return False


def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        print("Сохранение удалено.")


# Инициализация игры
def init_game(init_hp=50, init_coins=15, init_dmg=10):
    global hp, coins, damage
    hp = init_hp
    coins = init_coins
    damage = init_dmg
    for p in potions.values():
        p["count"] = 0


# Уровни и генерация монстров
def get_player_level() -> int:
    """
    Простой динамичний уровень игрока, зависящий от HP и урона.
    Чем больше HP/урон — тем выше уровень.
    """
    # hp // 10 делает вклад выносливости менее доминирующим
    lvl = max(1, (damage + hp // 10) // 10)
    return lvl


def get_monster_level(player_level: int) -> int:
    """
    Возвращает уровень монстра относительно уровня игрока.
    60% слабее, 30% равный, 10% сильнее.
    """
    chance = r.random()
    if chance < 0.6:
        return max(1, player_level - 1)
    elif chance < 0.9:
        return player_level
    else:
        return player_level + 1


def generate_monster_stats(monster_level: int) -> Tuple[int, int]:
    """
    Возвращает hp, dmg монстра, балансируемые по уровню.
    Формулы можно подкорректировать под сложность.
    """
    base_hp = 30 + monster_level * 25    # рост HP по уровню
    base_dmg = 5 + monster_level * 8     # рост урона по уровню
    return base_hp, base_dmg


# Боевая система
def player_attack(monster_hp: int) -> int:
    """Атака игрока: шанс промаха, шанс крита, иначе обычный урон."""
    global damage
    miss_chance = 0.10
    crit_chance = 0.18  # суммарно: 10% промах, 18% крит (можно менять)
    x = r.random()
    if x < miss_chance:
        print("Ты промахнулся!")
        return monster_hp
    x2 = r.random()
    if x2 < crit_chance:
        crit = damage * 2
        print(f"Критический удар! Ты нанес {crit} урона!")
        return monster_hp - crit
    print(f"Ты нанес {damage} урона.")
    return monster_hp - damage


def monster_attack(monster_name: str, monster_dmg: int):
    """Атака монстра: есть шанс промаха, в противном случае снимаем HP."""
    global hp
    miss_chance = 0.15
    if r.random() < miss_chance:
        print(f"{monster_name} промахнулся!")
    else:
        hp -= monster_dmg
        print(f"{monster_name} атакует! Ты теряешь {monster_dmg} HP. У тебя осталось {hp} HP.")


# Использование зелий
def use_potion() -> bool:
    """Меню использования зелья. Возвращает True, если зелье выпито."""
    global hp
    if total_potions() == 0:
        print("У тебя нет зелий.")
        return False

    print_potions()
    keys = list(potions.keys())
    print("\nВыбери зелье:")
    for i, key in enumerate(keys, start=1):
        p = potions[key]
        print(f"{i}. {p['name']} (+{p['heal']} HP) x{p['count']}")
    print(f"{len(keys) + 1}. Отмена")

    choice = input("Номер зелья: ").strip()
    if not choice.isdigit():
        print("Неверный ввод.")
        return False
    choice = int(choice)
    if choice == len(keys) + 1:
        return False
    if 1 <= choice <= len(keys):
        k = keys[choice - 1]
        if potions[k]["count"] > 0:
            potions[k]["count"] -= 1
            hp += potions[k]["heal"]
            print(f"Ты выпил {potions[k]['name']}! Теперь у тебя {hp} HP.")
            return True
        else:
            print("У тебя нет такого зелья.")
            return False
    print("Неверный выбор.")
    return False



# События: сундук, торговец, монстр
def meet_box():
    """Сундук: иногда даёт зелье, чаще — монеты"""
    global coins
    print("\nВы нашли сундук! (нажми Enter)")
    input()
    chance = r.randint(0, 10)
    if chance == 0:
        potions["weak"]["count"] += 1
        print("Вы нашли 1 слабое зелье!")
    else:
        reward = r.randint(4, 46)
        coins += reward
        print(f"Вы нашли {reward} монет.")
        print_coins()


def meet_shop():
    """Торговец: исцеление, карты, зелья, оружия"""
    global hp, coins, damage
    # цены
    hp25_cost = 15
    hp50_cost = 20
    hp100_cost = 35
    map_cost = 150
    potion_costs = {"weak": 35, "medium": 50, "strong": 75, "berserk": 120, "gods": 500}

    def can_buy(cost: int) -> bool:
        global coins
        if coins >= cost:
            return True
        print("У вас недостаточно монет.")
        return False

    print("\nНа пути тебе встретился торговец!")
    print_parameters()
    while True:
        print("\nЧто ты хочешь купить?")
        # случайное оружие
        weapon_rarity = r.choice(["Обычный", "Редкий", "Легендарный"])
        weapon_names = ["Деревянный меч", "Стальной меч", "экскалибур", "Деревянный лук", "Эльфийский лук", "Посох"]
        weapon = r.choice(weapon_names)
        # значения зависят от редкости
        if weapon_rarity == "Обычный":
            weapon_dmg = r.randint(13, 19)
            weapon_cost = r.randint(15, 27)
        elif weapon_rarity == "Редкий":
            weapon_dmg = r.randint(20, 28)
            weapon_cost = r.randint(29, 35)
        else:
            weapon_dmg = r.randint(30, 45)
            weapon_cost = r.randint(38, 55)

        print(f"1. +25 HP - {hp25_cost} монет")
        print(f"2. +50 HP - {hp50_cost} монет")
        print(f"3. +100 HP - {hp100_cost} монет")
        print(f"4. Карта - {map_cost} монет (можно попасть к сундуку/фарму/боссу)")
        print("5. Магазин зелий")
        print(f"6. Купить {weapon_rarity} {weapon} (={weapon_dmg} урон) - {weapon_cost} монет")
        print("7. Выйти из магазина")

        ch = input("Выбор: ").strip()
        if ch == "1":
            if can_buy(hp25_cost):
                coins -= hp25_cost
                hp += 25
                print_hp(); print_coins()
        elif ch == "2":
            if can_buy(hp50_cost):
                coins -= hp50_cost
                hp += 50
                print_hp(); print_coins()
        elif ch == "3":
            if can_buy(hp100_cost):
                coins -= hp100_cost
                hp += 100
                print_hp(); print_coins()
        elif ch == "4":
            if can_buy(map_cost):
                coins -= map_cost
                print("\nВы купили карту. Куда хотите направиться?")
                print("1. Сокровища")
                print("2. Фарм монстров (5 боёв)")
                print("3. Босс")
                c = input("Путь: ").strip()
                if c == "1":
                    loot = r.randint(80, 350)
                    coins += loot
                    print(f"В сундуке лежало {loot} монет.")
                    print_coins()
                elif c == "2":
                    for _ in range(5):
                        meet_monster()
                        if hp <= 0:
                            break
                elif c == "3":
                    meet_dragon()
                else:
                    print("Неверный ввод.")
        elif ch == "5":
            # магазин зелий
            while True:
                print("\nМагазин зелий:")
                for i, k in enumerate(potions.keys(), start=1):
                    print(f"{i}. {potions[k]['name']} - {potion_costs[k]} монет")
                print(f"{len(potions)+1}. Назад")
                choice = input("Покупка: ").strip()
                if not choice.isdigit():
                    print("Неверный ввод.")
                    continue
                choice = int(choice)
                if choice == len(potions) + 1:
                    break
                keys = list(potions.keys())
                if 1 <= choice <= len(keys):
                    key = keys[choice - 1]
                    cost = potion_costs[key]
                    if can_buy(cost):
                        coins -= cost
                        potions[key]["count"] += 1
                        print(f"Куплено: {potions[key]['name']}.")
                else:
                    print("Неверный ввод.")
        elif ch == "6":
            if can_buy(weapon_cost):
                coins -= weapon_cost
                damage = weapon_dmg
                print("Вы купили оружие.")
                print_damage(); print_coins()
        elif ch == "7":
            action = input("\n(Enter — продолжить / S — сохранить / L — загрузить / Q — выйти): ").strip().lower()
            if action == "s":
                save_game()
                break
            elif action == "l":
                load_game()
                break
            elif action == "q":
                print("Выход из игры...")
                save_game()
                exit(0)
            else:
                break
        else:
            print("Неверный ввод.")


def meet_monster():
    """Логика встречи с обычным монстром (баланс по уровню игрока)."""
    global hp, coins, damage
    player_level = get_player_level()
    monster_level = get_monster_level(player_level)
    monster_hp, monster_dmg = generate_monster_stats(monster_level)
    monster_name = r.choice(MONSTER_NAMES)
    print(f"\nНа тебя напал {monster_name} (уровень {monster_level})!")
    print(f"У него {monster_hp} HP и {monster_dmg} урона.")
    print_parameters()

    while monster_hp > 0:
        if hp <= 0:
            game_over()
            return

        action = input("\nЧто будешь делать? (1. Атаковать / 2. Бежать / 3. Зелья): ").strip().lower()
        if action == "1":
            monster_hp = player_attack(monster_hp)
            print(f"У {monster_name}: {monster_hp} hp")
            if monster_hp > 0:
                monster_attack(monster_name, monster_dmg)
            else:
                # победа
                loot = monster_level * r.randint(8, 18)
                coins += loot
                hp += 5  # маленькая регенерация
                # небольшая прогрессия
                damage += 1
                print(f"\nТы победил {monster_name}!")
                print(f"Награда: {loot} монет, +5 HP и +1 урон.")
                print_parameters()
                break
        elif action == "2":
            # шанс побега снижается с уровнем монстра
            escape_chance = 0.5 - (monster_level - player_level) * 0.1
            escape_chance = max(0.15, min(0.85, escape_chance))
            if r.random() < escape_chance:
                print("Ты успешно сбежал!")
                break
            else:
                print("Побег не удался — монстр догнал тебя!")
                monster_attack(monster_name, monster_dmg)
        elif action == "3":
            used = use_potion()
            if used:
                # после использования зелья обычно монстр получает ход
                monster_attack(monster_name, monster_dmg)
        else:
            print("Неверный ввод.")


def meet_dragon():
    """Бой с боссом — более тяжёлый, но награда сильнее."""
    global hp, coins, damage
    dragon_name = "Рамишище"
    dragon_hp = 1000
    dragon_dmg = 150
    input("\nТы подошёл к логову дракона...")
    input("Из шахты выходит огромный дракон!")
    print(f"Его зовут {dragon_name}. HP: {dragon_hp}, Урон: {dragon_dmg}")
    print("Начинается битва!")
    while dragon_hp > 0:
        if hp <= 0:
            game_over()
            return
        action = input("\n(1. Атаковать / 2. Зелья / S. Сохранить / Q. Выйти): ").strip().lower()
        if action == "1":
            dragon_hp = player_attack(dragon_hp)
            if dragon_hp > 0:
                monster_attack(dragon_name, dragon_dmg)
            else:
                print("\nТы одолел великого дракона - Рамишище!")
                coins += 1500
                hp += 500
                damage += 250
                print("Ты получаешь 1500 монет, +500 HP и +250 урона!")
                print_parameters()
                # возможность продолжить или выйти
                while True:
                    retry = input("Хочешь продолжить приключение? (1. Да / 2. Нет): ").strip()
                    if retry == "1":
                        return
                    elif retry == "2":
                        print("Прощай, путник!")
                        save_game()
                        exit(0)
                    else:
                        print("Неверный ввод.")
        elif action == "2":
            used = use_potion()
            if used:
                monster_attack(dragon_name, dragon_dmg)
        elif action == "s":
            save_game()
        elif action == "q":
            print("Выход из игры...")
            save_game()
            exit(0)
        else:
            print("Неверный ввод.")



# Главный цикл игры
def game_loop():
    """Основной игровой цикл: случайные события или меню сохранения"""
    while True:
        # выбираем событие
        situation = r.randint(0, 4)
        if situation == 0:
            meet_shop()
        elif situation == 1:
            meet_box()
        elif situation == 2:
            meet_monster()
        else:
            print("\nБлуждаешь... (нажми Enter)")
            input()



# Старт/перезапуск/выход
def start_game_menu():
    print("\n1. Начать новое приключение")
    print("2. Загрузить сохранение")
    print("3. Удалить сохранение")
    print("4. Выйти")
    choice = input("Выбор: ").strip()
    if choice == "1":
        init_game()
        print("Новое приключение начинается!")
    elif choice == "2":
        if not load_game():
            print("Не удалось загрузить. Начинаем новое приключение.")
            init_game()
    elif choice == "3":
        delete_save()
        init_game()
    elif choice == "4":
        print("Ну ладно.")
        exit(0)
    else:
        print("Неверный ввод.")
        start_game_menu()



def game_over():
    global hp
    if hp <= 0:
        print("\nТы погиб!")
        choice = input("Хочешь начать сначала? (1. Да / 2. выход / L - загрузить сохранение): ").strip()
        if choice == "1":
            init_game()
            return
        else:
            print("Прощай.")
            exit(0)



# Запуск
init_game()  # стартовые параметры по умолчанию
print(f"\nВаш ник: {name}")
print_parameters()
start_game_menu()
game_loop()

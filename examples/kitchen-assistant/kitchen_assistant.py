"""A throwaway kitchen assistant. Four small commands, standard library only."""
import json
import pathlib
import re
import sys
from decimal import Decimal, InvalidOperation

TO_BASE = {"g": (Decimal(1), "g"), "kg": (Decimal(1000), "g"), "ml": (Decimal(1), "ml"), "l": (Decimal(1000), "ml")}
QUANTITY_LINE = re.compile(r"^(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>kg|g|ml|l)?\s+(?:of\s+)?(?P<name>[a-z][a-z ]*)$", re.I)
SERVES_LINE = re.compile(r"^serves\s+(?P<count>\d+)$", re.I)
STOCK_COMMAND = re.compile(r"^(?P<verb>used|bought)\s+(?P<rest>.+)$", re.I)
MAX_RECENT_CREDIT = 3


class KitchenError(Exception):
    pass


def parse_quantity(text):
    match = QUANTITY_LINE.match(text.strip())
    if not match:
        raise KitchenError(f"cannot parse: {text.strip()!r}")
    try:
        quantity = Decimal(match["qty"])
    except InvalidOperation:
        raise KitchenError(f"cannot parse: {text.strip()!r}") from None
    factor, unit = TO_BASE.get((match["unit"] or "").lower(), (Decimal(1), "count"))
    return match["name"].strip().lower(), quantity * factor, unit


def show(quantity, unit):
    if unit in ("g", "ml") and quantity >= 1000:
        quantity, unit = quantity / 1000, "kg" if unit == "g" else "l"
    return f"{format(quantity.normalize(), 'f')} {unit}".replace(" count", "")


def parse_recipe(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise KitchenError("empty recipe")
    recipe = {"title": lines[0], "serves": None, "ingredients": []}
    for number, line in enumerate(lines[1:], start=2):
        serves = SERVES_LINE.match(line)
        if serves:
            recipe["serves"] = int(serves["count"])
            continue
        try:
            name, quantity, unit = parse_quantity(line)
        except KitchenError as error:
            raise KitchenError(f"line {number}: {error}") from None
        recipe["ingredients"].append({"name": name, "qty": str(quantity), "unit": unit})
    if not recipe["ingredients"]:
        raise KitchenError("no ingredients")
    return recipe


def apply_stock_command(stock, command):
    match = STOCK_COMMAND.match(command.strip())
    if not match:
        raise KitchenError(f"cannot parse: {command.strip()!r}")
    name, quantity, unit = parse_quantity(match["rest"])
    held = stock.get(name)
    if match["verb"].lower() == "bought":
        if held and held["unit"] != unit:
            raise KitchenError(f"{name} is kept in {held['unit']}, not {unit}")
        total = Decimal(held["qty"]) + quantity if held else quantity
        return {**stock, name: {"qty": str(total), "unit": unit}}
    if not held:
        raise KitchenError(f"no {name} in stock")
    if held["unit"] != unit:
        raise KitchenError(f"{name} is kept in {held['unit']}, not {unit}")
    remaining = Decimal(held["qty"]) - quantity
    if remaining < 0:
        raise KitchenError(f"only {show(Decimal(held['qty']), unit)} {name} in stock, cannot use {show(quantity, unit)}")
    return {**stock, name: {"qty": str(remaining), "unit": unit}}


def shortfalls(recipes, stock):
    needed = {}
    for recipe in recipes:
        for item in recipe["ingredients"]:
            entry = needed.setdefault(item["name"], {"qty": Decimal(0), "unit": item["unit"]})
            if entry["unit"] != item["unit"]:
                raise KitchenError(f"{item['name']} is needed in both {entry['unit']} and {item['unit']}")
            entry["qty"] += Decimal(item["qty"])
    result = {}
    for name, entry in sorted(needed.items()):
        held = stock.get(name, {"qty": "0", "unit": entry["unit"]})
        if held["unit"] != entry["unit"]:
            raise KitchenError(f"{name} is needed in {entry['unit']} but kept in {held['unit']}")
        missing = entry["qty"] - Decimal(held["qty"])
        if missing > 0:
            result[name] = {"qty": missing, "unit": entry["unit"]}
    return result


def score_recipe(recipe, stock, times_cooked):
    covered, missing = [], []
    for item in recipe["ingredients"]:
        held = stock.get(item["name"])
        enough = held and held["unit"] == item["unit"] and Decimal(held["qty"]) >= Decimal(item["qty"])
        (covered if enough else missing).append(item["name"])
    habit = min(times_cooked, MAX_RECENT_CREDIT)
    return len(covered) - len(missing) + habit, covered, missing, habit


def suggest(recipes, stock, cooked_titles):
    scored = []
    for recipe in recipes:
        score, covered, missing, habit = score_recipe(recipe, stock, cooked_titles.count(recipe["title"]))
        scored.append((-score, recipe["title"], score, covered, missing, habit))
    return [row[1:] for row in sorted(scored)]


def read_json(path, default):
    path = pathlib.Path(path)
    return json.loads(path.read_text()) if path.exists() else default


def write_json(path, data):
    pathlib.Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def run(arguments):
    command, rest = arguments[0], arguments[1:]
    if command == "recipe":
        dictated, catalogue = rest
        recipe = parse_recipe(pathlib.Path(dictated).read_text())
        entries = read_json(catalogue, [])
        write_json(catalogue, [e for e in entries if e["title"] != recipe["title"]] + [recipe])
        saved = f"saved {recipe['title']}, serves {recipe['serves']}"
        return [saved] + [f"  {i['name']}: {show(Decimal(i['qty']), i['unit'])}" for i in recipe["ingredients"]]
    if command == "stock":
        path, text = rest
        stock = read_json(path, {})
        write_json(path, apply_stock_command(stock, text))
        updated = read_json(path, {})
        return [f"ok: {name} {show(Decimal(updated[name]['qty']), updated[name]['unit'])}" for name in sorted(updated) if updated[name] != stock.get(name)]
    if command == "list":
        catalogue, stock_path, *titles = rest
        recipes = [r for r in read_json(catalogue, []) if r["title"] in titles]
        unknown = set(titles) - {r["title"] for r in recipes}
        if unknown:
            raise KitchenError(f"not in the catalogue: {', '.join(sorted(unknown))}")
        short = shortfalls(recipes, read_json(stock_path, {}))
        return [f"buy {show(v['qty'], v['unit'])} {name}" for name, v in short.items()] or ["nothing to buy"]
    if command == "suggest":
        catalogue, stock_path, log = rest
        ranked = suggest(read_json(catalogue, []), read_json(stock_path, {}), read_json(log, []))
        lines = [f"{title}: score {score} = {len(covered)} in stock - {len(missing)} missing + {habit} cooked" for title, score, covered, missing, habit in ranked]
        title, _, _, missing, _ = ranked[0]
        return lines + [f"choose {title}" + (f" (still need: {', '.join(missing)})" if missing else " (everything in stock)")]
    raise KitchenError(f"unknown command: {command}")


def main(arguments):
    try:
        lines = run(arguments)
    except KitchenError as error:
        print(f"refused: {error}")
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

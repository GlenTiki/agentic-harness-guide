import contextlib
import io
import pathlib
import shutil
import tempfile
import unittest

import kitchen_assistant as kitchen

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


class KitchenAssistant(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        shutil.copytree(FIXTURES, self.tmp / "work")
        self.work = self.tmp / "work"

    def call(self, *arguments):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = kitchen.main([str(a) for a in arguments])
        return code, out.getvalue().splitlines()

    def catalogue(self, *files):
        for name in files:
            self.assertEqual(self.call("recipe", self.work / name, self.work / "catalogue.json")[0], 0)
        return self.work / "catalogue.json"

    def test_dictated_recipe_becomes_an_entry(self):
        code, lines = self.call("recipe", self.work / "pancakes.txt", self.work / "catalogue.json")
        self.assertEqual((code, lines), (0, ["saved Pancakes, serves 4", "  eggs: 2", "  flour: 200 g", "  milk: 300 ml"]))
        entry = kitchen.read_json(self.work / "catalogue.json", [])[0]
        self.assertEqual(entry["serves"], 4)
        self.assertEqual(entry["ingredients"][1], {"name": "flour", "qty": "200", "unit": "g"})

    def test_unparsable_line_rejects_the_whole_entry(self):
        code, lines = self.call("recipe", self.work / "bad-recipe.txt", self.work / "catalogue.json")
        self.assertEqual((code, lines), (1, ["refused: line 5: cannot parse: 'a pinch of salt'"]))
        self.assertFalse((self.work / "catalogue.json").exists())

    def test_bought_converts_kilograms_and_adds(self):
        code, lines = self.call("stock", self.work / "stock.json", "bought 1 kg flour")
        self.assertEqual((code, lines), (0, ["ok: flour 2.5 kg"]))

    def test_used_reduces_stock(self):
        self.assertEqual(self.call("stock", self.work / "stock.json", "used 2 eggs"), (0, ["ok: eggs 4"]))

    def test_stock_never_goes_below_zero_and_file_is_unchanged(self):
        before = (self.work / "stock.json").read_text()
        code, lines = self.call("stock", self.work / "stock.json", "used 7 eggs")
        self.assertEqual((code, lines), (1, ["refused: only 6 eggs in stock, cannot use 7"]))
        self.assertEqual((self.work / "stock.json").read_text(), before)

    def test_used_item_never_stocked_is_refused(self):
        self.assertEqual(self.call("stock", self.work / "stock.json", "used 1 kg rice")[0], 1)

    def test_shopping_list_is_recipes_minus_stock(self):
        catalogue = self.catalogue("pancakes.txt", "omelette.txt")
        code, lines = self.call("list", catalogue, self.work / "stock.json", "Pancakes", "Omelette")
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["buy 50 g cheese", "buy 100 ml milk"])

    def test_nothing_to_buy_when_stock_covers_it(self):
        catalogue = self.catalogue("pancakes.txt")
        self.call("stock", self.work / "stock.json", "bought 100 ml milk")
        self.assertEqual(self.call("list", catalogue, self.work / "stock.json", "Pancakes"), (0, ["nothing to buy"]))

    def test_mismatched_units_fail_loudly(self):
        catalogue = self.catalogue("fried-rice.txt")
        code, lines = self.call("list", catalogue, self.work / "stock-oil.json", "Fried rice")
        self.assertEqual((code, lines), (1, ["refused: oil is needed in g but kept in ml"]))

    def test_unknown_recipe_title_is_refused(self):
        catalogue = self.catalogue("pancakes.txt")
        self.assertEqual(self.call("list", catalogue, self.work / "stock.json", "Soup")[0], 1)

    def test_suggestion_shows_its_scoring(self):
        catalogue = self.catalogue("pancakes.txt", "omelette.txt")
        code, lines = self.call("suggest", catalogue, self.work / "stock.json", self.work / "cooked.json")
        self.assertEqual(code, 0)
        self.assertEqual(lines, [
            "Pancakes: score 3 = 2 in stock - 1 missing + 2 cooked",
            "Omelette: score 2 = 2 in stock - 1 missing + 1 cooked",
            "choose Pancakes (still need: milk)",
        ])

    def test_ties_break_alphabetically(self):
        ranked = kitchen.suggest(
            [{"title": "B", "ingredients": []}, {"title": "A", "ingredients": []}], {}, []
        )
        self.assertEqual([row[0] for row in ranked], ["A", "B"])


if __name__ == "__main__":
    unittest.main()

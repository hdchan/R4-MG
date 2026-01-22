import unittest
import random

from SWUApp.Models import ParsedDeckList, CardType


from Tests.SWUAppTests.Mocks.Models import RandomModels

class ParsedDeckList_test(unittest.TestCase):

    def test_has_cards_true(self):
        resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(),
            RandomModels.swu_trading_card_backed_local_card_resource(),
            RandomModels.swu_trading_card_backed_local_card_resource(),
        ]

        sut = ParsedDeckList(resources)

        self.assertTrue(sut.has_cards)
    
    def test_has_cards_false(self):
        sut = ParsedDeckList([])

        self.assertFalse(sut.has_cards)

    def test_all_cards(self):
        resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(),
            RandomModels.swu_trading_card_backed_local_card_resource(),
            RandomModels.swu_trading_card_backed_local_card_resource(),
        ]

        sut = ParsedDeckList(resources)

        self.assertEqual(sut.all_cards, resources)

    def test_main_deck_and_sideboard(self):
        main_deck_resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(),
        ]

        sideboard_resource = RandomModels.swu_trading_card_backed_local_card_resource()
        sideboard_resource.set_is_sideboard(True)

        sideboard_resources = [
            sideboard_resource,
        ]

        sut = ParsedDeckList(main_deck_resources + sideboard_resources)

        self.assertEqual(sut.main_deck, main_deck_resources)
        self.assertEqual(sut.sideboard, sideboard_resources)


    def test_first_leader_and_first_base(self):
        first_leader = RandomModels.swu_trading_card_backed_local_card_resource(trading_card=RandomModels.swu_trading_card(type=CardType.LEADER.value))
        first_base = RandomModels.swu_trading_card_backed_local_card_resource(trading_card=RandomModels.swu_trading_card(type=CardType.BASE.value))
        resources = [
            first_leader,
            RandomModels.swu_trading_card_backed_local_card_resource(trading_card=RandomModels.swu_trading_card(type=CardType.LEADER.value)),
            first_base,
            RandomModels.swu_trading_card_backed_local_card_resource(trading_card=RandomModels.swu_trading_card(type=CardType.BASE.value)),
        ]

        sut = ParsedDeckList(resources)

        self.assertEqual(sut.first_leader_and_first_base, [first_leader, first_base])

    def test_all_cards_excluding_leader_base(self):
        leader_base_resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.LEADER.value)),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.BASE.value))
        ]

        resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(),
        ]

        sut = ParsedDeckList(leader_base_resources + resources)

        self.assertEqual(sut.all_cards_excluding_leader_base(), resources)

    def test_main_deck_with_cost(self):
        main_deck_resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(),
        ]

        expected_cost = random.randint(1, 100)
        main_deck_resources_with_cost = [
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost=f"{expected_cost}")),
        ]
        
        sut = ParsedDeckList(main_deck_resources + main_deck_resources_with_cost)

        self.assertEqual(sut.main_deck_with_cost(expected_cost), main_deck_resources_with_cost)

    def test_sideboard_with_cost(self):
        sideboard_resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(),
        ]

        expected_cost = random.randint(0, 100)
        sideboard_resource = RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost=f"{expected_cost}"))
        sideboard_resource.set_is_sideboard(True)

        sideboard_resources_with_cost = [
            sideboard_resource
        ]
        
        sut = ParsedDeckList(sideboard_resources + sideboard_resources_with_cost)

        self.assertEqual(sut.sideboard_with_cost(expected_cost), sideboard_resources_with_cost)

    def test_all_main_deck_units_with_cost(self):
        resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.UNIT.value)),
        ]

        expected_cost = random.randint(1, 100)
        resources_with_cost = RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.UNIT.value, cost=f"{expected_cost}"))

        resources_with_cost = [
            resources_with_cost
        ]

        # should exclude sideboard
        sideboard_resource = RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.UNIT.value, cost=f"{expected_cost}"))
        sideboard_resource.set_is_sideboard(True)

        sideboard_resources_with_cost = [
            sideboard_resource
        ]
        
        sut = ParsedDeckList(resources + resources_with_cost + sideboard_resources_with_cost)

        self.assertEqual(sut.all_main_deck_units_with_cost(expected_cost), resources_with_cost)

    def test_all_main_deck_upgrades_and_events_with_cost(self):
        resources = [
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.EVENT.value)),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.UPGRADE.value))
        ]

        expected_cost = random.randint(1, 100)

        event_resource_with_cost = RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.EVENT.value, cost=f"{expected_cost}"))

        upgrade_resource_with_cost = RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.UPGRADE.value, cost=f"{expected_cost}"))

        resources_with_cost = [
            event_resource_with_cost,
            upgrade_resource_with_cost
        ]

        # should exclude sideboard
        event_sideboard_resource = RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.EVENT.value, cost=f"{expected_cost}"))
        event_sideboard_resource.set_is_sideboard(True)

        upgrade_sideboard_resource = RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(type=CardType.UPGRADE.value, cost=f"{expected_cost}"))
        upgrade_sideboard_resource.set_is_sideboard(True)

        sideboard_resources_with_cost = [
            event_sideboard_resource,
            upgrade_sideboard_resource
        ]
        
        sut = ParsedDeckList(resources + resources_with_cost + sideboard_resources_with_cost)

        self.assertEqual(sut.all_main_deck_upgrades_and_events_with_cost(expected_cost), resources_with_cost)


    def test_main_deck_cost_curve_values(self):
        main_deck_resources_with_cost = [
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="1")),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="3")),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="5")),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="20")),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="100")),
        ]
        
        sut = ParsedDeckList(main_deck_resources_with_cost)

        self.assertEqual(sut.main_deck_cost_curve_values, [1, 3, 5, 20, 100])


    def test_sideboard_cost_curve_values(self):
        sideboard_resources_with_cost = [
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="1")),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="3")),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="5")),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="20")),
            RandomModels.swu_trading_card_backed_local_card_resource(RandomModels.swu_trading_card(cost="100")),
        ]
        for i in sideboard_resources_with_cost:
            i.set_is_sideboard(True)
        
        sut = ParsedDeckList(sideboard_resources_with_cost)

        self.assertEqual(sut.sideboard_cost_curve_values, [1, 3, 5, 20, 100])
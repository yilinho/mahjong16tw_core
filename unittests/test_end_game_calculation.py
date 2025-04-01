import unittest
from collections import deque

from mahjong16tw_core.engine import MahjongGame, PointType, GameState, Action


def _key(score_type: PointType):
    return f"point_{score_type.value}"

class MyTestCase(unittest.TestCase):
    def test_not_goal(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.banker = 0

        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 214, 215, 216, 300, 301]
        mj_game.player_tiles[0].recent_tile = 301

        game_result, game_result_banker = mj_game.game_result(0, (1,))
        self.assertFalse(game_result)
        self.assertFalse(game_result_banker)

    def test_discard_self_goal(self):
        mj_game = MahjongGame(4, {}, seed=612116)

        mj_game.banker = 0

        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 214, 215, 216, 300, 300]
        mj_game.player_tiles[0].recent_tile = 300
        game_result, game_result_banker = mj_game.game_result(0, (1, 2, 3))
        self.assertIn((1, _key(PointType.BANKER), ()), game_result_banker)
        self.assertIn((3, _key(PointType.ALL_SELF_GOAL), ()), game_result)
        game_result, game_result_banker = mj_game.game_result(0, (1,))
        self.assertIn((1, _key(PointType.BANKER), ()), game_result_banker)
        self.assertIn((1, _key(PointType.ALL_SELF), ()), game_result)

        mj_game.player_tiles[0].shown_chow = [201, 202, 203]
        mj_game.player_tiles[0].hand = [204, 205, 206, 207, 208, 209, 211, 212, 213, 214, 215, 216, 300, 300]
        mj_game.player_tiles[0].recent_tile = 300
        game_result, game_result_banker = mj_game.game_result(0, (1, 2, 3))
        self.assertIn((1, _key(PointType.BANKER), ()), game_result_banker)
        self.assertIn((1, _key(PointType.SELF_GOAL), ()), game_result)

        game_result, game_result_banker = mj_game.game_result(0, (1,))
        self.assertIn((1, _key(PointType.BANKER), ()), game_result_banker)
        self.assertNotIn((1, _key(PointType.SELF_GOAL), ()), game_result)

        mj_game.banker = 3
        game_result, game_result_banker = mj_game.game_result(0, (1,))
        self.assertNotIn((1, _key(PointType.BANKER), ()), game_result_banker)
        mj_game.banker = 1
        game_result, game_result_banker = mj_game.game_result(0, (1,))
        self.assertIn((1, _key(PointType.BANKER), ()), game_result_banker)

        mj_game.running = 5
        game_result, game_result_banker = mj_game.game_result(0, (1,))
        self.assertIn((1, _key(PointType.BANKER), ()), game_result_banker)
        self.assertIn((10, _key(PointType.RUNNING), (5, 5)), game_result_banker)

        mj_game.banker = 3
        game_result, game_result_banker = mj_game.game_result(0, (1,))
        self.assertNotIn((1, _key(PointType.BANKER), ()), game_result_banker)
        self.assertNotIn((10, _key(PointType.RUNNING), (5, 5)), game_result_banker)

    def test_flower(self):
        mj_game = MahjongGame(4, {}, seed=612116)

        mj_game.banker = 3
        mj_game.dice_result = (1, 1, 1)  # opening pos = 1
        mj_game.player_tiles[1].flowers = [100, 101, 102, 103, 104, 105]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 300, 300, 300, 311, 311]
        mj_game.player_tiles[1].recent_tile = 311
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.FLOWER), (100,)), game_result)
        self.assertIn((1, _key(PointType.FLOWER), (104,)), game_result)
        self.assertNotIn((1, _key(PointType.FLOWER), (102,)), game_result)
        self.assertNotIn((1, _key(PointType.FLOWER), (107,)), game_result)

        mj_game.player_tiles[2].flowers = [100, 101, 102, 103, 104, 105]
        mj_game.player_tiles[2].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 300, 300, 300, 311, 311]
        mj_game.player_tiles[2].recent_tile = 311
        game_result, _ = mj_game.game_result(2, (1,))
        self.assertIn((1, _key(PointType.FLOWER), (103,)), game_result)
        self.assertNotIn((1, _key(PointType.FLOWER), (100,)), game_result)
        self.assertNotIn((1, _key(PointType.FLOWER), (104,)), game_result)
        self.assertNotIn((1, _key(PointType.FLOWER), (107,)), game_result)

        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.FLOWER_KONG), ()), game_result)

        mj_game.player_tiles[1].flowers = [104, 105, 106, 107]
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.FLOWER_KONG), ()), game_result)

        mj_game.player_tiles[1].flowers = [104, 105, 106]
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((1, _key(PointType.FLOWER_KONG), ()), game_result)

    def test_wind(self):
        mj_game = MahjongGame(4, {}, seed=612116)

        mj_game.banker = 3
        mj_game.dice_result = (1, 1, 2)  # opening pos = 2
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 300, 300, 300, 301, 301, 301, 311, 311]
        mj_game.player_tiles[1].recent_tile = 311

        mj_game.round = 0
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.WIND_ROUND), (300,)), game_result)
        self.assertNotIn((1, _key(PointType.WIND_ROUND), (301,)), game_result)
        self.assertNotIn((1, _key(PointType.WIND_SEAT), (300,)), game_result)
        self.assertIn((1, _key(PointType.WIND_SEAT), (301,)), game_result)

        mj_game.player_tiles[1].shown_pong = [300]
        mj_game.player_tiles[1].shown_kong = [301]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 311, 311]
        mj_game.player_tiles[1].recent_tile = 311
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.WIND_ROUND), (300,)), game_result)
        self.assertNotIn((1, _key(PointType.WIND_ROUND), (301,)), game_result)
        self.assertNotIn((1, _key(PointType.WIND_SEAT), (300,)), game_result)
        self.assertIn((1, _key(PointType.WIND_SEAT), (301,)), game_result)

        mj_game.round = 1
        mj_game.player_tiles[0].self_kong = [300]
        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 301, 301, 301, 311, 311]
        mj_game.player_tiles[0].recent_tile = 311
        game_result, _ = mj_game.game_result(0, (2,))
        self.assertNotIn((1, _key(PointType.WIND_ROUND), (300,)), game_result)
        self.assertIn((1, _key(PointType.WIND_ROUND), (301,)), game_result)
        self.assertNotIn((1, _key(PointType.WIND_SEAT), (300,)), game_result)
        self.assertNotIn((1, _key(PointType.WIND_SEAT), (301,)), game_result)

        mj_game.player_tiles[0].self_kong = [300]
        mj_game.player_tiles[0].shown_kong = [301]
        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 302, 302, 302, 303, 303]
        mj_game.player_tiles[0].recent_tile = 303
        game_result, _ = mj_game.game_result(0, (2,))
        self.assertIn((8, _key(PointType.SMALL_WIND), ()), game_result)


        mj_game.player_tiles[0].hand = [201, 201, 204, 205, 206, 300, 300, 300, 301, 301, 301, 302, 302, 302, 303, 303, 303]
        mj_game.player_tiles[0].recent_tile = 201
        game_result, _ = mj_game.game_result(0, (2,))
        self.assertIn((16, _key(PointType.BIG_WIND), ()), game_result)
        for w in range(300, 304):
            self.assertNotIn((1, _key(PointType.WIND_ROUND), (w,)), game_result)
            self.assertNotIn((1, _key(PointType.WIND_SEAT), (w,)), game_result)

    def test_dragon(self):
        mj_game = MahjongGame(4, {}, seed=612116)

        mj_game.banker = 3
        mj_game.dice_result = (1, 1, 2)  # opening pos = 2
        mj_game.player_tiles[1].hand = [201, 201, 201, 204, 205, 206, 207, 208, 209, 300, 300, 311, 311, 311, 312, 312, 312]
        mj_game.player_tiles[1].recent_tile = 300

        mj_game.round = 0
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.DRAGON), (311,)), game_result)
        self.assertIn((1, _key(PointType.DRAGON), (312,)), game_result)

        mj_game.player_tiles[1].hand = [201, 201, 201, 204, 205, 206, 207, 208, 209, 310, 310, 311, 311, 311, 312, 312, 312]
        mj_game.player_tiles[1].recent_tile = 310
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((4, _key(PointType.SMALL_DRAGON), ()), game_result)
        self.assertNotIn((1, _key(PointType.DRAGON), (311,)), game_result)
        self.assertNotIn((1, _key(PointType.DRAGON), (312,)), game_result)

        mj_game.player_tiles[1].hand = [201, 201, 204, 205, 206, 207, 208, 209, 310, 310, 310, 311, 311, 311, 312, 312, 312]
        mj_game.player_tiles[1].recent_tile = 310
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((8, _key(PointType.BIG_DRAGON), ()), game_result)
        self.assertNotIn((1, _key(PointType.DRAGON), (310,)), game_result)
        self.assertNotIn((1, _key(PointType.DRAGON), (311,)), game_result)
        self.assertNotIn((1, _key(PointType.DRAGON), (312,)), game_result)

    def test_pong(self):
        mj_game = MahjongGame(4, {}, seed=612116)

        mj_game.banker = 3
        mj_game.dice_result = (1, 1, 2)  # opening pos = 2
        mj_game.player_tiles[1].self_kong = [202]
        mj_game.player_tiles[1].hand = [201, 201, 201, 213, 213, 213, 214, 214, 214, 221, 221, 221, 300, 300]
        mj_game.player_tiles[1].recent_tile = 300
        game_result, _ = mj_game.game_result(1, (2, ))
        print(game_result)
        self.assertIn((1, _key(PointType.ALL_SELF), ()), game_result)
        self.assertIn((4, _key(PointType.ALL_PONG), ()), game_result)
        self.assertIn((8, _key(PointType.COVER_PONG5), ()), game_result)
        mj_game.player_tiles[1].self_kong = [202]
        mj_game.player_tiles[1].shown_kong = [201]
        mj_game.player_tiles[1].hand = [213, 213, 213, 214, 214, 214, 221, 221, 221, 300, 300]
        mj_game.player_tiles[1].recent_tile = 300
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((4, _key(PointType.ALL_PONG), ()), game_result)
        self.assertIn((5, _key(PointType.COVER_PONG4), ()), game_result)
        mj_game.player_tiles[1].self_kong = [202]
        mj_game.player_tiles[1].shown_kong = [201]
        mj_game.player_tiles[1].hand = [211, 212, 213, 214, 214, 214, 221, 221, 221, 300, 300]
        mj_game.player_tiles[1].recent_tile = 300
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((4, _key(PointType.ALL_PONG), ()), game_result)
        self.assertIn((2, _key(PointType.COVER_PONG3), ()), game_result)

    def test_all_pong(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.banker = 3
        mj_game.dice_result = (1, 1, 2)  # opening pos = 2

        mj_game.player_tiles[1].self_kong = [202]
        mj_game.player_tiles[1].shown_kong = [201]
        mj_game.player_tiles[1].hand = [213, 213, 213, 214, 214, 214, 221, 221, 221, 300, 300]
        mj_game.player_tiles[1].recent_tile = 300
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((4, _key(PointType.ALL_PONG), ()), game_result)

        mj_game.player_tiles[1].self_kong = [202]
        mj_game.player_tiles[1].shown_kong = [201]
        mj_game.player_tiles[1].hand = [213, 213, 213, 214, 214, 214, 221, 221, 221, 300, 300]
        mj_game.player_tiles[1].recent_tile = 213
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((4, _key(PointType.ALL_PONG), ()), game_result)



    def test_no_self_all_self(self):
        mj_game = MahjongGame(4, {}, seed=612116)

        mj_game.banker = 3
        mj_game.dice_result = (1, 1, 2)  # opening pos = 2
        mj_game.player_tiles[1].shown_pong = [201, 202, 203, 204, 205]
        mj_game.player_tiles[1].hand = [300, 300]
        mj_game.player_tiles[1].recent_tile = 300
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.NO_SELF), ()), game_result)
        self.assertNotIn((1, _key(PointType.HALF_NO_SELF), ()), game_result)
        game_result, _ = mj_game.game_result(1, (2, 3, 0))
        self.assertNotIn((1, _key(PointType.NO_SELF), ()), game_result)
        self.assertIn((1, _key(PointType.HALF_NO_SELF), ()), game_result)

        mj_game.player_tiles[1].self_kong = [201]
        mj_game.player_tiles[1].hand = [202, 202, 202, 213, 213, 213, 214, 214, 214, 221, 221, 221, 300, 300]
        mj_game.player_tiles[1].recent_tile = 300
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.ALL_SELF), ()), game_result)

    def test_single_candidate(self):
        mj_game = MahjongGame(4, {}, seed=612116)

        mj_game.player_tiles[1].self_kong = [201, 202, 203]
        mj_game.player_tiles[1].hand = [213, 213, 213, 214, 214, 214, 300, 300]
        mj_game.player_tiles[1].recent_tile = 300
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.SINGLE_CANDIDATE), ()), game_result)

        mj_game.player_tiles[1].self_kong = [201, 202, 203]
        mj_game.player_tiles[1].hand = [206, 207, 208, 213, 213, 213, 300, 300]
        mj_game.player_tiles[1].recent_tile = 208
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((1, _key(PointType.SINGLE_CANDIDATE), ()), game_result)

        mj_game.player_tiles[1].self_kong = [201, 202, 203]
        mj_game.player_tiles[1].hand = [207, 208, 209, 213, 213, 213, 300, 300]
        mj_game.player_tiles[1].recent_tile = 208
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.SINGLE_CANDIDATE), ()), game_result)

        mj_game.player_tiles[1].self_kong = [201, 202, 203]
        mj_game.player_tiles[1].hand = [207, 208, 209, 213, 213, 213, 300, 300]
        mj_game.player_tiles[1].recent_tile = 207
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((1, _key(PointType.SINGLE_CANDIDATE), ()), game_result)

    def test_sequence(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 211, 212, 213, 216, 216, 221, 222, 223]
        mj_game.player_tiles[1].recent_tile = 216
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((1, _key(PointType.SEQUENCE), ()), game_result)

        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 211, 212, 213, 216, 216, 221, 222, 223]
        mj_game.player_tiles[1].recent_tile = 212
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((1, _key(PointType.SEQUENCE), ()), game_result)

        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 211, 212, 213, 216, 216, 221, 222, 223]
        mj_game.player_tiles[1].recent_tile = 211
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((2, _key(PointType.SEQUENCE), ()), game_result)

        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 211, 212, 213, 221, 222, 223, 300, 300]
        mj_game.player_tiles[1].recent_tile = 211
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((1, _key(PointType.SEQUENCE), ()), game_result)

        mj_game.player_tiles[1].shown_pong = [201]
        mj_game.player_tiles[1].hand = [204, 205, 206, 211, 212, 213, 216, 216, 221, 222, 223]
        mj_game.player_tiles[1].recent_tile = 211
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((1, _key(PointType.SEQUENCE), ()), game_result)

    def test_one_suit(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.player_tiles[1].shown_pong = [202, 205, 207]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 208, 208]
        mj_game.player_tiles[1].recent_tile = 208
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((8, _key(PointType.ONE_SUIT), ()), game_result)
        self.assertNotIn((8, _key(PointType.ONLY_HONOR), ()), game_result)
        self.assertNotIn((4, _key(PointType.ONE_SUIT_MIX), ()), game_result)

        mj_game.player_tiles[1].shown_pong = [300]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 208, 208]
        mj_game.player_tiles[1].recent_tile = 208
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((8, _key(PointType.ONE_SUIT), ()), game_result)
        self.assertNotIn((8, _key(PointType.ONLY_HONOR), ()), game_result)
        self.assertIn((4, _key(PointType.ONE_SUIT_MIX), ()), game_result)

        mj_game.player_tiles[1].shown_pong = [300]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 218, 218]
        mj_game.player_tiles[1].recent_tile = 218
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((8, _key(PointType.ONE_SUIT), ()), game_result)
        self.assertNotIn((8, _key(PointType.ONLY_HONOR), ()), game_result)
        self.assertNotIn((4, _key(PointType.ONE_SUIT_MIX), ()), game_result)

        mj_game.player_tiles[1].shown_pong = [311]
        mj_game.player_tiles[1].hand = [300, 300, 300, 301, 301, 301, 302, 302, 302, 303, 303, 303, 312, 312]
        mj_game.player_tiles[1].recent_tile = 312
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertNotIn((8, _key(PointType.ONE_SUIT), ()), game_result)
        self.assertIn((8, _key(PointType.ONLY_HONOR), ()), game_result)
        self.assertNotIn((4, _key(PointType.ONE_SUIT_MIX), ()), game_result)
        self.assertNotIn((4, _key(PointType.ALL_PONG), ()), game_result)

        mj_game.player_tiles[1].shown_pong = [311]
        mj_game.player_tiles[1].hand = [300, 300, 301, 301, 301, 302, 302, 302, 303, 303, 303, 312, 312, 312]
        mj_game.player_tiles[1].recent_tile = 312
        game_result, _ = mj_game.game_result(1, (2,))
        self.assertIn((8, _key(PointType.ONLY_HONOR), ()), game_result)
        self.assertIn((4, _key(PointType.ALL_PONG), ()), game_result)

    def test_goal_after_kong1(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.ROLL_DICE:
            pid, state, target, actions = mj_game.get_next_state()
        mj_game.tiles = deque([
            201, 202, 204, 205, 203, 203, 203, 300, 201, 202, 204, 205, 201, 202, 204, 205,
            211, 212, 214, 215, 213, 213, 213, 300, 211, 212, 214, 215, 211, 212, 214, 215,
            221, 222, 224, 225, 223, 223, 223, 300, 221, 222, 224, 225, 221, 222, 224, 225,
            228, 229, 218, 219, 226, 226, 226, 300, 228, 229, 218, 219, 228, 229, 218, 219,
            302, 311
        ] + list(mj_game.tiles) + [
            311
        ])
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.SELF_KONG, 300), actions)
        pid, state, target, actions = mj_game.perform_action(Action.SELF_KONG, 300)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.SUPPLY)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.SELF_GOAL, 311), actions)
        pid, state, target, actions = mj_game.perform_action(Action.SELF_GOAL, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.END)
        game_result, game_result_banker = actions
        self.assertIn((1, _key(PointType.KONG_GOAL), ()), game_result)

    def test_goal_after_kong2(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.ROLL_DICE:
            pid, state, target, actions = mj_game.get_next_state()
        mj_game.tiles = deque([
            201, 202, 204, 205, 203, 203, 203, 300, 201, 202, 204, 205, 201, 202, 204, 205,
            211, 212, 214, 215, 213, 213, 213, 300, 211, 212, 214, 215, 211, 212, 214, 215,
            221, 222, 224, 225, 223, 223, 223, 300, 221, 222, 224, 225, 221, 222, 224, 225,
            228, 229, 218, 219, 226, 226, 226, 311, 228, 229, 218, 219, 209, 209, 209, 311,
            209
        ] + list(mj_game.tiles) + [
            311
        ])
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 209)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.KONG, 209), actions)
        self.assertEqual(pid, 3)
        pid, state, target, actions = mj_game.perform_action(Action.KONG, 209)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.SUPPLY)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.GOAL, 311), actions)
        pid, state, target, actions = mj_game.perform_action(Action.GOAL, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.END)
        game_result, game_result_banker = actions
        self.assertNotIn((1, _key(PointType.KONG_GOAL), ()), game_result)

    def test_goal_after_kong3(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.ROLL_DICE:
            pid, state, target, actions = mj_game.get_next_state()
        mj_game.tiles = deque([
            201, 202, 204, 205, 203, 203, 203, 300, 201, 202, 204, 205, 201, 202, 204, 205,
            211, 212, 214, 215, 203, 213, 213, 300, 211, 212, 214, 215, 211, 212, 214, 215,
            221, 222, 224, 225, 223, 223, 223, 311, 221, 222, 224, 225, 221, 222, 224, 225,
            228, 229, 218, 219, 226, 226, 226, 311, 228, 229, 218, 219, 209, 209, 209, 312,
            209, 312, 311
        ] + list(mj_game.tiles) + [
            213, 311,
        ])
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 209)
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertIn((Action.KONG, 209), actions)
        pid, state, target, actions = mj_game.perform_action(Action.KONG, 209)
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.SUPPLY)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 311)
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertNotIn((Action.GOAL, 311), actions)
        self.assertIn((Action.PONG, 311), actions)
        pid, state, target, actions = mj_game.perform_action(Action.PASS, 311)
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.DRAW)
        self.assertEqual(target, 312)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 312)
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.DRAW)
        self.assertEqual(target, 311)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.SELF_KONG, 203), actions)
        self.assertNotIn((Action.SELF_GOAL, 213), actions)  # cannot goal
        pid, state, target, actions = mj_game.perform_action(Action.SELF_KONG, 203)
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.SUPPLY)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertIn((Action.SELF_GOAL, 213), actions)
        pid, state, target, actions = mj_game.perform_action(Action.SELF_GOAL, 213)
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.END)
        game_result, game_result_banker = actions
        self.assertIn((1, _key(PointType.KONG_GOAL), ()), game_result)

    def test_live_bug(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.banker = 3
        mj_game.round = 3
        mj_game.player_tiles[3].shown_pong = [227]
        for t in [202, 204, 207, 208, 209, 214, 215, 216, 223, 223, 224, 225, 226, 203]:
            mj_game.player_tiles[3].append_hand(t)
        game_result, game_result_banker = mj_game.game_result(3, (0, 1, 2))
        self.assertIn((1, _key(PointType.SELF_GOAL), ()), game_result)
        self.assertIn((1, _key(PointType.SINGLE_CANDIDATE), ()), game_result)
        self.assertIn((1, _key(PointType.BANKER), ()), game_result_banker)
        mj_game.player_tiles[3].hand.sort()
        game_result, game_result_banker = mj_game.game_result(3, (0, 1, 2))
        self.assertIn((1, _key(PointType.SELF_GOAL), ()), game_result)
        self.assertIn((1, _key(PointType.SINGLE_CANDIDATE), ()), game_result)
        self.assertIn((1, _key(PointType.BANKER), ()), game_result_banker)


if __name__ == '__main__':
    unittest.main()

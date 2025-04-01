import unittest
from collections import deque

from mahjong16tw_core.engine import MahjongGame, GameState, Action


class MyTestCase(unittest.TestCase):
    def test_can_goal1(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.banker = 0
        mj_game.new_game()

        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()

        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 300, 301, 302, 303, 310]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 211, 213, 301, 301, 302, 303]
        mj_game.player_tiles[2].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 214, 215, 216, 300, 300]  # missing 213
        mj_game.player_tiles[3].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 211, 213, 300, 301, 302, 312]
        mj_game.player_tiles[2].recent_tile = 0
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 213)
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 2)
        self.assertEqual(state, GameState.CHECK_DISCARD_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.PASS, 213)
        self.assertEqual(pid, 2)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 213)
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 2)
        self.assertNotEqual(actions[0][0], Action.GOAL)
        pid, state, target, actions = mj_game.perform_action(Action.CHOW_RIGHT, 213)
        self.assertEqual(pid, 2)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 2)
        self.assertFalse(actions)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 300)
        self.assertEqual(pid, 2)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 300)
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 2)
        self.assertEqual(actions[0][0], Action.GOAL)

    def test_can_goal2(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.banker = 0
        mj_game.new_game()

        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()

        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 300, 301, 302, 303, 310]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 214, 215, 216, 300, 300]  # missing 213
        mj_game.player_tiles[1].recent_tile = 0
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 213)
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.CHECK_DISCARD_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.CHOW_RIGHT, 213)
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertFalse(actions)

    def test_can_goal_after_extend_kong1(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.ROLL_DICE:
            pid, state, target, actions = mj_game.get_next_state()
        mj_game.tiles = deque([
            201, 202, 204, 205, 203, 203, 204, 300, 311, 202, 204, 205, 201, 202, 204, 205,
            211, 212, 214, 215, 213, 213, 213, 300, 211, 212, 214, 215, 211, 212, 214, 215,
            221, 222, 224, 225, 223, 223, 223, 300, 221, 222, 224, 225, 221, 222, 224, 225,
            228, 229, 218, 219, 226, 226, 226, 311, 228, 229, 218, 219, 209, 209, 209, 312,
            203, 303, 303, 303, 311
        ] + list(mj_game.tiles) + [
            213, 311,
        ])
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 203)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.PONG, 203), actions)
        self.assertEqual(pid, 1)
        pid, state, target, actions = mj_game.perform_action(Action.PONG, 203)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 204)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.GOAL, 311), actions)
        pid, state, target, actions = mj_game.perform_action(Action.PASS, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertNotIn((Action.SELF_GOAL, 311), actions)

    def test_can_goal_after_extend_kong2(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.ROLL_DICE:
            pid, state, target, actions = mj_game.get_next_state()
        mj_game.tiles = deque([
            201, 202, 204, 205, 203, 203, 204, 300, 311, 202, 204, 205, 201, 202, 204, 205,
            211, 212, 214, 215, 213, 213, 213, 300, 211, 212, 214, 215, 211, 212, 214, 215,
            221, 222, 224, 225, 223, 223, 223, 300, 221, 222, 224, 225, 221, 222, 224, 225,
            228, 229, 218, 219, 226, 226, 226, 311, 228, 229, 218, 219, 209, 209, 209, 312,
            203, 303, 303, 303, 213
        ] + list(mj_game.tiles) + [
            213, 311,
        ])
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 203)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.PONG, 203), actions)
        self.assertEqual(pid, 1)
        pid, state, target, actions = mj_game.perform_action(Action.PONG, 203)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 204)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.GOAL, 311), actions)
        pid, state, target, actions = mj_game.perform_action(Action.PASS, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertIn((Action.SELF_KONG, 213), actions)
        pid, state, target, actions = mj_game.perform_action(Action.SELF_KONG, 213)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.SUPPLY)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertNotIn((Action.SELF_GOAL, 311), actions)

    def test_can_goal_after_extend_kong3(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.ROLL_DICE:
            pid, state, target, actions = mj_game.get_next_state()
        mj_game.tiles = deque([
            201, 202, 204, 205, 203, 203, 204, 300, 311, 202, 204, 205, 201, 202, 204, 205,
            211, 212, 214, 215, 213, 213, 213, 300, 211, 212, 214, 215, 211, 212, 214, 215,
            221, 222, 224, 225, 223, 223, 223, 300, 221, 222, 224, 225, 221, 222, 224, 225,
            228, 229, 218, 219, 226, 226, 226, 311, 228, 229, 218, 219, 209, 209, 209, 312,
            203, 303, 303, 303, 203
        ] + list(mj_game.tiles) + [
            213, 311,
        ])
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 203)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.PONG, 203), actions)
        self.assertEqual(pid, 1)
        pid, state, target, actions = mj_game.perform_action(Action.PONG, 203)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 204)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertIn((Action.GOAL, 311), actions)
        pid, state, target, actions = mj_game.perform_action(Action.PASS, 311)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertIn((Action.EXTEND_KONG, 203), actions)
        pid, state, target, actions = mj_game.perform_action(Action.EXTEND_KONG, 203)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.SUPPLY)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertIn((Action.SELF_GOAL, 311), actions)


if __name__ == '__main__':
    unittest.main()

import unittest

from mahjong16tw_core.engine import MahjongGame, GameState, Action


class MyTestCase(unittest.TestCase):
    def test_goal_sequence(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.banker = 0
        mj_game.new_game()

        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()

        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 300, 301, 302, 303, 310]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 214, 215, 216, 300, 300]  # goal+chow
        mj_game.player_tiles[2].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 214, 215, 216, 300, 301]
        mj_game.player_tiles[3].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 214, 215, 216, 300, 300]  # goal
        mj_game.player_tiles[2].recent_tile = 0

        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 213)
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)

        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.CHECK_DISCARD_ACTION)
        self.assertIn((Action.GOAL, 213), actions)
        self.assertIn((Action.PASS, 213), actions)
        self.assertNotIn((Action.CHOW_LEFT, 213), actions)
        self.assertNotIn((Action.CHOW_MIDDLE, 213), actions)
        self.assertNotIn((Action.CHOW_RIGHT, 213), actions)

        pid, state, target, actions = mj_game.perform_action(Action.PASS, 213)
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)

        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertIn((Action.GOAL, 213), actions)
        self.assertIn((Action.PASS, 213), actions)
        self.assertNotIn((Action.CHOW_LEFT, 213), actions)
        self.assertNotIn((Action.CHOW_MIDDLE, 213), actions)
        self.assertNotIn((Action.CHOW_RIGHT, 213), actions)

        pid, state, target, actions = mj_game.perform_action(Action.PASS, 213)
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)

        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertIn((Action.PASS, 213), actions)
        self.assertIn((Action.CHOW_LEFT, 213), actions)
        self.assertIn((Action.CHOW_MIDDLE, 213), actions)
        self.assertIn((Action.CHOW_RIGHT, 213), actions)


if __name__ == '__main__':
    unittest.main()

import unittest

from mahjong16tw_core.engine import MahjongGame, GameState, Action


class MyTestCase(unittest.TestCase):
    def test_can_kong1(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.banker = 0
        mj_game.new_game()

        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()

        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 300, 301, 302, 303, 310]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 211, 213, 301, 301, 302, 303]
        mj_game.player_tiles[2].hand = [201, 202, 203, 204, 204, 206, 207, 208, 209, 211, 212, 214, 215, 216, 300, 300]  # missing 213
        mj_game.player_tiles[3].hand = [201, 201, 201, 204, 205, 206, 207, 208, 209, 211, 211, 213, 300, 301, 302, 312]
        mj_game.player_tiles[3].recent_tile = 0
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.CHECK_DISCARD_ACTION)
        self.assertIn((Action.KONG, 201), actions)
        self.assertIn((Action.PONG, 201), actions)
        pid, state, target, actions = mj_game.perform_action(Action.PONG, 201)
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertNotIn((Action.EXTEND_KONG, 201), actions)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 204)
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 2)
        self.assertEqual(state, GameState.CHECK_DISCARD_ACTION)
        self.assertIn((Action.PONG, 204), actions)
        pid, state, target, actions = mj_game.perform_action(Action.PONG, 204)
        self.assertEqual(pid, 2)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 2)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 206)
        self.assertEqual(pid, 2)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.CHECK_DISCARD_ACTION)
        self.assertIn((Action.CHOW_LEFT, 206), actions)
        self.assertIn((Action.CHOW_MIDDLE, 206), actions)
        pid, state, target, actions = mj_game.perform_action(Action.PASS, 206)
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.DRAW)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 3)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertIn((Action.EXTEND_KONG, 201), actions)  # can kong

    def test_can_kong2(self):
        mj_game = MahjongGame(4, {}, seed=612116)
        mj_game.banker = 0
        mj_game.new_game()

        pid, state, target, actions = mj_game.get_next_state()
        while state != GameState.CHECK_DRAW_ACTION:
            pid, state, target, actions = mj_game.get_next_state()

        mj_game.player_tiles[0].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 300, 301, 302, 303, 310]
        mj_game.player_tiles[1].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 211, 213, 303, 303, 303, 303]
        mj_game.player_tiles[2].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 214, 215, 216, 300, 300]  # missing 213
        mj_game.player_tiles[3].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 211, 213, 300, 301, 302, 312]
        mj_game.player_tiles[3].recent_tile = 0
        pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 201)
        self.assertEqual(pid, 0)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.CHECK_DISCARD_ACTION)
        self.assertIn((Action.CHOW_LEFT, 201), actions)
        pid, state, target, actions = mj_game.perform_action(Action.CHOW_LEFT, 201)
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.ACTION_ACCEPTED)
        pid, state, target, actions = mj_game.get_next_state()
        self.assertEqual(pid, 1)
        self.assertEqual(state, GameState.CHECK_DRAW_ACTION)
        self.assertNotIn((Action.SELF_KONG, 303), actions)


if __name__ == '__main__':
    unittest.main()

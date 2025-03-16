import unittest

from ..engine import MahjongGame, GameState, Action


class MyTestCase(unittest.TestCase):
    def test_discard_action_sequence(self):
        for banker in range(4):
            mj_game = MahjongGame(4, {}, seed=612116)
            mj_game.banker = banker
            mj_game.new_game()

            pid, state, target, actions = mj_game.get_next_state()
            while state != GameState.CHECK_DRAW_ACTION:
                pid, state, target, actions = mj_game.get_next_state()

            for i in range(4):
                if i == banker:
                    continue
                mj_game.player_tiles[i].hand = [201, 202, 203, 204, 205, 206, 207, 208, 209, 211, 212, 213, 214, 215, 216, 300]

            pid, state, target, actions = mj_game.perform_action(Action.DISCARD, 300)

            self.assertEqual(pid, banker)  # add assertion here
            pid, state, target, actions = mj_game.get_next_state()
            self.assertEqual(pid, (banker + 1) % 4)  # add assertion here



if __name__ == '__main__':
    unittest.main()

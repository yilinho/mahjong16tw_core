import time

import ai
import engine

STABILITY_TEST = False
languages = {
    "zh_tw": {
        "numbers_half": "0123456789",
        "numbers_full": "零一二三四五六七八九",
        "tile_0": "ＸＸ",
        "tile_100": "春１",
        "tile_101": "夏２",
        "tile_102": "秋３",
        "tile_103": "冬４",
        "tile_104": "梅１",
        "tile_105": "蘭２",
        "tile_106": "竹３",
        "tile_107": "菊４",
        "tile_300": "東風",
        "tile_301": "南風",
        "tile_302": "西風",
        "tile_303": "北風",
        "tile_310": "紅中",
        "tile_311": "青發",
        "tile_312": "白皮",
        "tile_200": "萬",
        "tile_210": "筒",
        "tile_220": "條",
    },
    "zh": {
        "numbers_half": "0123456789",
        "numbers_full": "零一二三四五六七八九",
        "tile_0": "ＸＸ",
        "tile_100": "春１",
        "tile_101": "夏２",
        "tile_102": "秋３",
        "tile_103": "冬４",
        "tile_104": "梅１",
        "tile_105": "兰２",
        "tile_106": "竹３",
        "tile_107": "菊４",
        "tile_300": "东风",
        "tile_301": "南风",
        "tile_302": "西风",
        "tile_303": "北风",
        "tile_310": "红中",
        "tile_311": "青发",
        "tile_312": "白皮",
        "tile_200": "万",
        "tile_210": "筒",
        "tile_220": "条",
    }
}
_language = "zh_tw"


def i18n(key):
    return languages.get(_language, {}).get(key, languages["zh_tw"].get(key, f"[undefined {key}]"))


def get_tile_string(value: int):
    if value == -1:
        return "  "
    if engine.get_tile_type(value) in engine.SUIT_TYPES:
        return i18n(f"numbers_full")[engine.get_tile_idx(value)] + i18n(f"tile_{value // 10 * 10}")
    return i18n(f"tile_{value}")


def print_hand(flowers, display_tiles, hand):
    for t in flowers:
        print(get_tile_string(t)[0], end="\t")
    for t in display_tiles:
        print(get_tile_string(t)[0], end="\t")
    print()
    for t in flowers:
        print(get_tile_string(t)[1], end="\t")
    for t in display_tiles:
        print(get_tile_string(t)[1], end="\t")
    print()

    for t in hand:
        print(t, end="\t")
    print()
    for t in hand:
        print(get_tile_string(t)[0], end="\t")
    print()
    for t in hand:
        print(get_tile_string(t)[1], end="\t")
    print()


if __name__ == "__main__":
    # mj_game = MahjongGame(4, {}, 612116)
    mj_game = engine.MahjongGame(4, {})
    wins = [0, 0, 0, 0]
    loses = [0, 0, 0, 0]
    while True:
        t1 = time.time()
        mj_game.new_game()

        pid, state, target, actions = mj_game.get_next_state()
        while state != engine.GameState.END:
            if not STABILITY_TEST:
                time.sleep(0.5)
                print("-------------------------------------------------------------------------------")
                print(f"player{pid}", state.name, target, actions)
                if pid == 0:
                    print_hand(mj_game.player_tiles[pid].flowers, mj_game.player_tiles[pid].display_tiles, mj_game.player_tiles[pid].hand)
            if state in (engine.GameState.CHECK_DRAW_ACTION, engine.GameState.CHECK_DISCARD_ACTION):
                if pid == 0 and not STABILITY_TEST:
                    print("actions:", [(a.name, t, get_tile_string(t)) for a, t in actions])
                    while True:
                        try:
                            if state == engine.GameState.CHECK_DRAW_ACTION:
                                action, target = input("discard/action, target: ").split()
                            else:
                                action, target = input("action, target: ").split()
                            action = eval(f"engine.Action.{action.upper()}")
                            break
                        except Exception as e:
                            print(e)
                    pid, state, target, actions = mj_game.perform_action(action, int(target))
                else:
                    if state == engine.GameState.CHECK_DISCARD_ACTION:
                        action, target = ai.get_discard_action(pid, actions, target, mj_game, 0)
                    else:
                        action, target = ai.get_draw_action(pid, actions, mj_game, 0.1, False, 0)
                    if not STABILITY_TEST:
                        print(action.name, target)
                    pid, state, target, actions = mj_game.perform_action(action, target)
            else:
                try:
                    pid, state, target, actions = mj_game.get_next_state()
                except StopIteration:
                    break

        winner = target[0]
        losers = target[1]
        game_result = actions[0]
        game_result_banker = actions[1]

        if not STABILITY_TEST:
            print("Winner:", winner)
            print("Losers:", losers)
            print("-------------------------------------------------------------------------------")
            for point, reason, ex in game_result_banker:
                print(point, reason, ex)
            print("-------------------------------------------------------------------------------")
            for point, reason, ex in game_result:
                print(point, reason, ex)
            print("-------------------------------------------------------------------------------")

        if winner >= 0:
            wins[winner] += 1
            for loser in losers:
                loses[loser] += 1
        print(wins, loses)
        print(time.time() - t1)

        if not STABILITY_TEST:
            input("next round?")
        # break

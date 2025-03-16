import random
from functools import lru_cache

from . import engine

def _evaluate_discard(hand: tuple[int, ...], draw_no_flowers: list[int]) -> list[tuple[int, int]]:
    scores = []
    processed = set()
    for i, tile in enumerate(hand):
        if tile in processed:
            continue
        processed.add(tile)
        scores.append((_evaluate(hand[:i] + hand[i + 1:], draw_no_flowers), tile))

    return scores


def get_discard(hand: tuple[int, ...], draw_no_flowers: list[int], avoid: tuple[int, ...]) -> list[tuple[int, int]]:
    type_counter = engine.get_type_counter(hand)
    scores = []

    for score, tile in _evaluate_discard(tuple(hand), draw_no_flowers):
        if tile in avoid:
            continue
        score += 10 * type_counter[engine.get_tile_type(tile)]  # keep more types if the scores are the same
        score += abs(5 - engine.get_tile_idx(tile))  # keep tiles closer to middle
        scores.append((score, tile))
    if not scores:
        return get_discard(hand, draw_no_flowers, avoid[:-1])
    scores.sort(reverse=True)

    return scores


def _evaluate(hand: tuple[int, ...], draw_no_flowers: list[int]) -> int:
    if len(hand) == 2 and hand[0] == hand[1]:  # goal
        return 999999

    if len(hand) not in (1, 4, 7, 10, 13, 16):
        return max(_evaluate_discard(hand, draw_no_flowers))[0]

    if len(hand) in (1, 4):
        # reduced_hand must be [hand] due to the above logic. Hence, we only check the following if it's possible to goal
        candidates = engine.get_candidates(tuple(hand))
        if candidates:
            distance_score = 0
            for i, t in enumerate(draw_no_flowers):
                if t in candidates:
                    distance_score += (20 - i) * 2000
            counts = 0
            tile_counter = engine.get_tile_counter(hand)
            for candidate in candidates:
                counts += 4 - tile_counter.get(candidate, 0)
            return 8000 * counts + distance_score

    score = _evaluate_reduced(hand)
    for _hand in engine.reduce_hand(hand):
        if hand == _hand:
            continue
        score = max(score, _evaluate(_hand, draw_no_flowers))
    return score

@lru_cache(maxsize=8192)
def _evaluate_reduced(hand: tuple[int, ...]) -> int:
    tile_counter = engine.get_tile_counter(hand)

    score = 0
    single_count = 0
    single_penalty = 0
    for tile, count in tile_counter.items():
        if engine.get_tile_type(tile) in engine.HONOR_TYPES:
            if count == 1:  # single honor
                score -= 10000
            elif count == 3:
                if engine.get_tile_type(tile) == engine.TileType.DRAGON:
                    score += 500
                score += 1000

    for suit in engine.SUIT_TYPE_VALUES:  # alone 1 and 9
        if tile_counter.get(suit + 1) == 1:
            if (suit + 2) not in tile_counter:
                if (suit + 3) not in tile_counter:  # single 1
                    single_penalty += 4000
                    single_count += 1
                score -= 1000  # 1, 3
            if (suit + 3) not in tile_counter:
                score -= 300

        if tile_counter.get(suit + 9) == 1:
            if (suit + 8) not in tile_counter:
                if (suit + 7) not in tile_counter:  # single 9
                    single_penalty += 4000
                    single_count += 1
                score -= 1000  # 7, 9
            if (suit + 7) not in tile_counter:
                score -= 300

    for suit in engine.SUIT_TYPE_VALUES:  # alone 2 and 8
        if tile_counter.get(suit + 2) == 1 and (suit + 1) not in tile_counter and (suit + 3) not in tile_counter:
            if (suit + 4) not in tile_counter:  # single 2
                single_penalty += 3500
                single_count += 1
            score -= 900  # 2, 4
        if tile_counter.get(suit + 8) == 1 and (suit + 9) not in tile_counter and (suit + 7) not in tile_counter:
            if (suit + 6) not in tile_counter:  # single 8
                single_penalty += 3500
                single_count += 1
            score -= 900  # 6, 8

    for suit in engine.SUIT_TYPE_VALUES:  # alone 3, 4, 5, 6, 7
        for v in (3, 4, 5, 6, 7):
            if tile_counter.get(suit + v) == 1 and (suit + v + 1) not in tile_counter and (suit + v - 1) not in tile_counter:
                if (suit + v + 2) not in tile_counter and (suit + v - 2) not in tile_counter:  # single
                    single_penalty += 3000
                    single_count += 1
                score -= 600  # 3, 5, 7
                score += 200 * abs(5 - v)  # 3, 7 are better than 4, 6 than 5
    if single_count == 1:
        single_penalty //= 2  # we can simply drop this tile
    score -= single_penalty

    if len(hand) < 8 and len(hand) == len(tile_counter):  # no pair
        score -= 2000

    score += 3000 * (16 - len(hand))

    return score


def get_action(
    owner: int, hand: list[int], actions: list[tuple[engine.Action, int]],
    draw_no_flowers: list[int], supply_no_flowers: int
) -> tuple[engine.Action, int]:
    for action, target in actions:
        if action in (engine.Action.GOAL, engine.Action.SELF_GOAL):
            return action, target
    for action, target in actions:
        if engine.get_tile_type(target) == engine.TileType.DRAGON:
            if action == engine.Action.EXTEND_KONG:
                return action, target
            if action == engine.Action.SELF_KONG:
                return action, target
            if owner != 3 and action == engine.Action.KONG:
                return action, target
    scores: list[tuple[int, tuple[engine.Action, int]]] = []
    if owner == 3:
        scores.append((_evaluate(tuple(hand), draw_no_flowers) + 1500, (engine.Action.PASS, 0)))
    else:
        scores.append((_evaluate(tuple(hand), draw_no_flowers) + 200, (engine.Action.PASS, 0)))

    for action, target in actions:
        match action:
            case engine.Action.KONG:
                _new_hand = hand.copy()
                _new_hand.remove(target)
                _new_hand.remove(target)
                _new_hand.remove(target)
                _new_hand.append(supply_no_flowers)
                _new_hand.sort()
                scores.append((_evaluate(tuple(_new_hand), draw_no_flowers) + 1000 + 750 * (3 - owner), (action, target)))

            case engine.Action.SELF_KONG:
                _new_hand = hand.copy()
                _new_hand.remove(target)
                _new_hand.remove(target)
                _new_hand.remove(target)
                _new_hand.remove(target)
                _new_hand.append(supply_no_flowers)
                _new_hand.sort()
                scores.append((_evaluate(tuple(_new_hand), draw_no_flowers) + 3000, (action, target)))

            case engine.Action.EXTEND_KONG:
                _new_hand = hand.copy()
                _new_hand.remove(target)
                _new_hand.append(supply_no_flowers)
                _new_hand.sort()
                scores.append((_evaluate(tuple(_new_hand), draw_no_flowers) + 3000, (action, target)))

            case engine.Action.PONG:
                _new_hand = hand.copy()
                _new_hand.remove(target)
                _new_hand.remove(target)
                scores.append((_evaluate(tuple(_new_hand), draw_no_flowers) + 750 * (3 - owner), (action, target)))

            case engine.Action.CHOW_LEFT:
                _new_hand = hand.copy()
                _new_hand.remove(target + 1)
                _new_hand.remove(target + 2)
                scores.append((_evaluate(tuple(_new_hand), draw_no_flowers), (action, target)))

            case engine.Action.CHOW_MIDDLE:
                _new_hand = hand.copy()
                _new_hand.remove(target - 1)
                _new_hand.remove(target + 1)
                scores.append((_evaluate(tuple(_new_hand), draw_no_flowers), (action, target)))

            case engine.Action.CHOW_RIGHT:
                _new_hand = hand.copy()
                _new_hand.remove(target - 2)
                _new_hand.remove(target - 1)
                scores.append((_evaluate(tuple(_new_hand), draw_no_flowers), (action, target)))

    scores.sort(reverse=True)
    return max(scores)[1]


def _get_no_flower(tiles: list[int], look_ahead: int = 0) -> tuple[list[int], int]:
    no_flower =  list(filter(lambda _t: engine.get_tile_type(_t) != engine.TileType.FLOWER, tiles))
    supply = no_flower.pop(-1)
    return no_flower[:look_ahead], supply


def get_discard_action(pid, actions, owner, mj_game, look_ahead: int = 0) -> tuple[engine.Action, int]:
    no_flowers, supply = _get_no_flower(list(mj_game.tiles), look_ahead)

    tiles = mj_game.player_tiles[pid]

    owner = (4 + owner - pid) % 4
    return get_action(owner, tiles.hand, actions, no_flowers, supply)


def get_draw_action(pid, actions, mj_game, temperature, avoid: bool = False, look_ahead: int = 0) -> tuple[engine.Action, int]:
    no_flowers, supply = _get_no_flower(list(mj_game.tiles), look_ahead)

    tiles = mj_game.player_tiles[pid]
    _action = engine.Action.DISCARD
    _target = tiles.recent_tile
    if actions:
        _action, _target = get_action(0, tiles.hand, actions, no_flowers, supply)
        if _action == engine.Action.PASS:
            _action = engine.Action.DISCARD

    if _action == engine.Action.DISCARD:  # pass or no actions
        _action = engine.Action.DISCARD
        if avoid:
            _c_set = set()
            for i, pt in enumerate(mj_game.player_tiles):
                if i == pid:
                    continue
                for _c in engine.get_candidates(tuple(pt.hand)):
                    _c_set.add(_c)
            avoid_tiles = tuple(_c_set)
        else:
            avoid_tiles = tuple()

        scores = get_discard(tuple(sorted(tiles.hand)), no_flowers, avoid_tiles)
        if temperature > 0:
            best_score = scores[0][0]
            scores = [(s + best_score * random.random() * temperature, t) for s, t in scores[:3]]
            scores.sort(reverse=True)
        _target = scores[0][1]
    return _action, _target

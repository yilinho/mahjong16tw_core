import random
from collections import Counter, deque
from enum import Enum, IntEnum, auto
from functools import lru_cache
from itertools import groupby
from typing import Deque, Iterable, Any


class TileType(Enum):
    # translation: https://www.xqbase.com/other/mahjongg_english.htm

    # abstract types
    BASE = 0
    HONOR = 10  # 東南西北中發白
    SUIT = 20  # 萬筒條

    # real types
    FLOWER = 100  # 花
    CHARACTER = 200  # 萬
    DOT = 210  # 筒
    BAMBOO = 220  # 條
    WIND = 300  # 東南西北
    DRAGON = 310  # 中發白

HONOR_TYPES = (TileType.WIND, TileType.DRAGON)
SUIT_TYPES = (TileType.CHARACTER, TileType.DOT, TileType.BAMBOO)
SUIT_TYPE_VALUES = (TileType.CHARACTER.value, TileType.DOT.value, TileType.BAMBOO.value)

ALL_TILES_WITHOUT_FLOWERS = tuple(4 * (
    [TileType.WIND.value + i for i in range(4)] +
    [TileType.DRAGON.value + i for i in range(3)] +
    [TileType.CHARACTER.value + i for i in range(1, 10)] +
    [TileType.DOT.value + i for i in range(1, 10)] +
    [TileType.BAMBOO.value + i for i in range(1, 10)]
))
ALL_TILES = tuple(list(ALL_TILES_WITHOUT_FLOWERS) + [TileType.FLOWER.value + i for i in range(8)])
VALID_TILES = tuple(sorted(set(ALL_TILES)))

TOTAL_TILES = len(ALL_TILES)  # 144

NUMBER_TILES_IN_HAND = 16
RESERVED_TILES = 16


class Action(IntEnum):
    # the greater value the higher priority
    PASS = 0  # 過水

    CHOW = 1  # 吃
    CHOW_RIGHT = 2
    CHOW_MIDDLE = 3
    CHOW_LEFT = 4

    PONG = 11  # 碰

    KONG = 31  # 槓
    SELF_KONG = 32  # 暗槓
    EXTEND_KONG = 33  # 槓在已經碰過的

    GOAL = 41  # 胡
    SELF_GOAL = 42  # 自摸

    DISCARD = 100


class PointType(Enum):
    BANKER = "banker"  # 莊家
    RUNNING = "running"  # 連莊

    SELF_GOAL = "self_goal"
    ALL_SELF = "all_self"  # 門清
    ALL_SELF_GOAL = "all_self_goal"  # 門清一摸三(不計前兩者)
    NO_SELF = "no_self"  # 全求
    HALF_NO_SELF = "half_no_self"  # 半求
    SELF_GOAL_LAST_TILE = "self_goal_last_tile"  # 海底撈月

    FLOWER = "flower"  # 花牌
    FLOWER_KONG = "flower_kong"  # 花槓
    FLOWER_8 = "flower_8"  # 摸八花
    FLOWER_7 = "flower_7"  # 七搶一

    WIND_ROUND = "wind_round"  # 圈風
    WIND_SEAT = "wind_seat"  # 門風
    SMALL_WIND = "small_wind"  # 小四喜(仍記前二)
    BIG_WIND = "big_wind"  # 大四喜(不計前三)

    DRAGON = "dragon"  # 三元牌
    SMALL_DRAGON = "small_dragon"  # 小三元 (不計前)
    BIG_DRAGON = "big_dragon"  # 大三元  (不計前二)

    KONG_GOAL = "kong_goal"  # 槓上開花
    EXTEND_KONG_GOAL = "extend_kong_goal"  # 搶槓

    COVER_PONG3 = "cover3"  # 三暗刻
    COVER_PONG4 = "cover4"
    COVER_PONG5 = "cover5"
    ALL_PONG = "all_pong"  # 碰碰胡

    SINGLE_CANDIDATE = "single_candidate"  # 獨聽(邊張, 中洞, 單吊)
    SEQUENCE = "sequence"  # 平胡(5順, 無字, 無花, 無獨聽, 無自摸)

    ONE_SUIT = "one_suit"  # 清一色
    ONE_SUIT_MIX = "one_suit_mix"  # 混一色
    ONLY_HONOR = "only_honor"  # 字一色


def get_tile_counter(hand: Iterable[int]) -> dict[int, int]:
    return {int(k): v for k,  v in Counter(hand).items()}


def get_type_counter(hand: Iterable[int]) -> dict[TileType, int]:
    return {k: len(list(g)) for k, g in groupby(hand, key=get_tile_type)}


def get_tile_type(value: int) -> TileType:
    return TileType(value // 10 * 10)


def get_tile_idx(value: int) -> int:
    return value % 10


@lru_cache(maxsize=8192)
def reduce_hand(hand: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    if len(hand) < 3:
        return hand,

    final = set()
    for i, tile in enumerate(hand[:-2]):  # triplet
        if hand[i+1] == tile and hand[i+2] == tile:
            for _h in reduce_hand(hand[:i] + hand[i+3:]):
                final.add(_h)

    for i, tile in enumerate(hand[:-2]):  # sequence
        if get_tile_type(tile) in SUIT_TYPES and hand[i+1] == tile + 1 and tile + 2 in hand:
            _new_hand = list(hand[:i] + hand[i+2:])
            _new_hand.remove(tile + 2)
            for _h in reduce_hand(tuple(_new_hand)):
                final.add(_h)

    if not final:
        final.add(hand)
    return tuple(final)


@lru_cache(maxsize=4096)
def get_candidates(hand: tuple[int, ...]):
    all_candidates = set()
    for tile in hand:
        all_candidates.add(tile)
        if get_tile_type(tile) in HONOR_TYPES:
            continue
        if get_tile_idx(tile) != 1:
            all_candidates.add(tile - 1)
        if get_tile_idx(tile) != 9:
            all_candidates.add(tile + 1)

    candidates = []
    for c in all_candidates:
        for _hand in reduce_hand(tuple(sorted(hand + (c,)))):
            if len(_hand) == 2 and _hand[0] == _hand[1]:
                candidates.append(c)
                break
    return candidates


class GameState(IntEnum):
    INITIAL = auto()
    START = auto()
    ROLL_DICE = auto()

    INIT_DRAW = auto()
    INIT_BANKER_DRAW = auto()
    INIT_FLOWER_SUPPLY = auto()

    DRAW = 300
    SUPPLY = 400
    CHECK_DRAW_ACTION = 500  # self-goal, self-kong, extend-kong, flower
    CHECK_DISCARD_ACTION = 600  # goal, kong, pong, chow. This state is not used in the state machine, only for communication

    ACTION_ACCEPTED = 700
    ACTION_PENDING = 701
    END = 800  # game result

    def __add__(self, other: int):
        return GameState(self.value + other)


class PlayerTiles:
    def __init__(self):
        # change the following lists in-place to keep reference
        self.hand: list[int] = []
        self.shown_chow: list[int] = []
        self.shown_pong: list[int] = []
        self.shown_kong: list[int] = []
        self.self_kong: list[int] = []
        self.flowers: list[int] = []
        self.discarded: list[int] = []
        self.display_tiles: list[int] = []  # from left to right, from the earliest action to latest
        self.recent_tile: int = 0

    def clear(self):
        # do not use clear() because of race condition
        self.hand = []
        self.shown_chow = []
        self.shown_pong = []
        self.shown_kong = []
        self.self_kong = []
        self.flowers = []
        self.discarded = []
        self.display_tiles = []
        self.recent_tile = 0

    def append_hand(self, tile: int):
        self.hand.append(tile)
        self.recent_tile = tile

    def sort(self):
        self.hand.sort()

    def check_flowers(self) -> int:
        flower_count = 0
        for t in self.hand:
            if get_tile_type(t) == TileType.FLOWER:
                flower_count += 1
                self.flowers.append(t)
        if flower_count > 0:
            for t in self.flowers[-flower_count:]:
                self.hand.remove(t)
        return flower_count

    @property
    def total_tiles(self) -> int:
        return len(self.hand) + len(self.shown_chow) + 3 * len(self.shown_pong + self.shown_kong + self.self_kong)

    def undo(self, action, target):
        match action:
            case Action.CHOW_LEFT | Action.CHOW_MIDDLE | Action.CHOW_RIGHT | Action.CHOW:
                self.hand.append(self.shown_chow.pop(-1))
                assert target == self.shown_chow.pop(-1)
                self.hand.append(self.shown_chow.pop(-1))
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)  # space
            case Action.PONG:
                assert target == self.shown_pong.pop(-1)
                for _ in range(2):
                    self.hand.append(target)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)  # space
            case Action.KONG:
                assert target == self.shown_kong.pop(-1)
                for _ in range(3):
                    self.hand.append(target)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)  # space
            case Action.SELF_KONG:
                assert target == self.self_kong.pop(-1)
                for _ in range(4):
                    self.hand.append(target)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)
                self.display_tiles.pop(-1)  # space
            case Action.EXTEND_KONG:
                assert target == self.shown_kong.pop(-1)
                self.hand.append(target)
                self.shown_pong.append(target)
                self.display_tiles.remove(target)
            case Action.GOAL:
                assert target == self.hand.pop(-1)
            case Action.SELF_GOAL | Action.PASS:
                pass
            case Action.DISCARD:
                assert target == self.discarded.pop(-1)
                self.hand.append(target)
            case _:
                raise NotImplementedError
        self.hand.sort()

    def do_discard(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND + 1 or target not in self.hand:
            return False
        self.hand.remove(target)
        self.discarded.append(target)
        return True

    def pop_discard(self):
        # someone else chow/pong/kong/goal
        self.discarded.pop(-1)

    def append_discard(self, tile):
        # for undo
        self.discarded.append(tile)

    def do_goal(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND:
            return False
        actions = self.get_discard_actions(target, 3, True)
        if (Action.GOAL, target) not in actions:
            return False
        self.hand.append(target)
        self.recent_tile = target
        return True

    def do_self_kong(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND + 1 or self.hand.count(target) != 4:
            return False
        for _ in range(4):
            self.hand.remove(target)
        self.self_kong.append(target)
        self.display_tiles.append(0)
        self.display_tiles.append(0)
        self.display_tiles.append(target)
        self.display_tiles.append(0)
        self.display_tiles.append(-1)
        return True

    def do_extend_kong(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND + 1 or target not in self.hand or target not in self.shown_pong:
            return False
        self.hand.remove(target)
        self.shown_pong.remove(target)
        self.shown_kong.append(target)
        self.display_tiles.insert(self.display_tiles.index(target), target)
        return True

    def pop_extend_kong(self):
        # someone goal to this tile
        target = self.shown_kong.pop(-1)
        self.shown_pong.append(target)
        self.display_tiles.remove(target)

    def do_kong(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND or self.hand.count(target) != 3:
            return False
        for _ in range(3):
            self.hand.remove(target)
        self.shown_kong.append(target)
        self.display_tiles.append(target)
        self.display_tiles.append(target)
        self.display_tiles.append(target)
        self.display_tiles.append(target)
        self.display_tiles.append(-1)
        return True

    def do_pong(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND or self.hand.count(target) < 2:
            return False
        for _ in range(2):
            self.hand.remove(target)
        self.shown_pong.append(target)
        self.display_tiles.append(target)
        self.display_tiles.append(target)
        self.display_tiles.append(target)
        self.display_tiles.append(-1)
        return True

    def do_chow_left(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND or target + 1 not in self.hand or target + 2 not in self.hand:
            return False
        self.hand.remove(target + 1)
        self.hand.remove(target + 2)
        self.shown_chow.append(target + 1)
        self.shown_chow.append(target)
        self.shown_chow.append(target + 2)
        self.display_tiles.append(target + 1)
        self.display_tiles.append(target)
        self.display_tiles.append(target + 2)
        self.display_tiles.append(-1)
        return True

    def do_chow_middle(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND or target -1 not in self.hand or target + 1 not in self.hand:
            return False
        self.hand.remove(target - 1)
        self.hand.remove(target + 1)
        self.shown_chow.append(target - 1)
        self.shown_chow.append(target)
        self.shown_chow.append(target + 1)
        self.display_tiles.append(target - 1)
        self.display_tiles.append(target)
        self.display_tiles.append(target + 1)
        self.display_tiles.append(-1)
        return True

    def do_chow_right(self, target) -> bool:
        if self.total_tiles != NUMBER_TILES_IN_HAND or target - 2 not in self.hand or target - 1 not in self.hand:
            return False
        self.hand.remove(target - 2)
        self.hand.remove(target - 1)
        self.shown_chow.append(target - 2)
        self.shown_chow.append(target)
        self.shown_chow.append(target - 1)
        self.display_tiles.append(target - 2)
        self.display_tiles.append(target)
        self.display_tiles.append(target - 1)
        self.display_tiles.append(-1)
        return True

    def get_draw_actions(self, can_goal: bool) -> list[tuple[Action, int]]:
        actions: list[tuple[Action, int]] = []
        tile_counter = get_tile_counter(self.hand)

        # SELF GOAL
        if can_goal:
            self.hand.remove(self.recent_tile)
            if self.recent_tile in get_candidates(tuple(self.hand)):
                actions.append((Action.SELF_GOAL, self.recent_tile))
            self.hand.append(self.recent_tile)
            self.sort()

        # KONG
        for t, c in tile_counter.items():
            if c == 4:
                actions.append((Action.SELF_KONG, t))

        for tile in self.shown_pong:
            if tile_counter.get(tile, 0) == 1:
                actions.append((Action.EXTEND_KONG, tile))
        return actions

    def get_discard_actions(self, target: int, owner: int, can_goal: bool) -> list[tuple[Action, int]]:
        actions: list[tuple[Action, int]] = []

        tile_counter = get_tile_counter(self.hand)
        tile_type = get_tile_type(target)

        # GOAL
        if can_goal and target in get_candidates(tuple(self.hand)):
            actions.append((Action.GOAL, target))

        # PONG
        if tile_counter.get(target, 0) >= 2:
            actions.append((Action.PONG, target))

        # KONG
        if tile_counter.get(target, 0) == 3:
            actions.append((Action.KONG, target))

        if owner == 3 and tile_type in SUIT_TYPES:
            if tile_counter.get(target + 1, 0) > 0 and tile_counter.get(target + 2, 0):
                actions.append((Action.CHOW_LEFT, target))
            if tile_counter.get(target - 1, 0) > 0 and tile_counter.get(target + 1, 0):
                actions.append((Action.CHOW_MIDDLE, target))
            if tile_counter.get(target - 2, 0) > 0 and tile_counter.get(target - 1, 0):
                actions.append((Action.CHOW_RIGHT, target))
        return actions


class MahjongGame:
    def __init__(self, player_count: int, rules, seed: int = 0):
        # seed = 5379031  # player 1 wins
        if seed:
            self.random = random.Random(seed)
        else:
            self.random = random.Random()

        self.player_count: int = player_count
        self.rules = rules

        self.round: int = 0
        self.banker: int = 0
        self.running: int = 0
        self._current_pid: int = 0
        self.dice_result: tuple[int, int, int] = (1, 1, 1)

        self._kong_goal_available: bool = False

        self.tiles: Deque[int] = deque()
        self.player_tiles: list[PlayerTiles] = [PlayerTiles() for _ in range(player_count)]

        self._game = self._state_machine()

    def __del__(self):
        self._game.close()

    def get_next_state(self) -> tuple[int, GameState, Any, Any]:
        return next(self._game)

    def perform_action(self, action: Action, target: int) -> tuple[int, GameState, Any, Any]:
        return self._game.send((action, target))

    def close_game(self):
        self._game.close()

    @property
    def current_player(self) -> PlayerTiles:
        return self.player_tiles[self._current_pid]

    def new_game(self):
        self._game.close()
        self._game = self._state_machine()

    def game_result(
        self,
        winner: int,
        losers: tuple[int, ...],
        extra_points: tuple[PointType, ...] = tuple()
    ) -> tuple[list[tuple[int, str, tuple[int, ...]]], list[tuple[int, str, tuple[int, ...]]]]:
        """
        :param winner: idx of the winner
        :param losers: idx of all losers
        :param extra_points: 8 flowers, 7 flowers, extend_kong_goal
        :return: list of points. (number of point, i18n key, (i18n key for format, key2, key3)
        """
        _key = lambda t: f"point_{t.value}"
        tiles = self.player_tiles[winner]
        points: list[tuple[int, str, tuple[int, ...]]] = []
        points_banker: list[tuple[int, str, tuple[int, ...]]] = []

        flowers8 = len(tiles.flowers) == 8
        if flowers8:  # force self-goal. All results are on top of it.
            points.append((8, _key(PointType.FLOWER_8), ()))

        for s in extra_points:  # TODO: add logic to handle it
            match s:
                case PointType.FLOWER_7:
                    points.append((8, _key(s), ()))
                case PointType.EXTEND_KONG_GOAL:
                    points.append((1, _key(s), ()))
                case PointType.KONG_GOAL:
                    points.append((1, _key(s), ()))
                case _:
                    raise NotImplementedError

        _hand_without_goal_tile = tiles.hand.copy()
        try:
            _hand_without_goal_tile.remove(tiles.recent_tile)
        except ValueError:  # 7 flowers. winner may not have that recent_tile
            return points, points_banker  # not goal yet

        candidates = get_candidates(tuple(_hand_without_goal_tile))
        if tiles.recent_tile not in candidates:
            return points, points_banker  # not goal yet

        # banker
        if self.banker in losers + (winner,):
            points_banker.append((1, _key(PointType.BANKER), tuple()))
            if self.running:
                points_banker.append((self.running * 2, _key(PointType.RUNNING), (self.running, self.running)))

        # self goal, all_self
        _all_self = len(tiles.hand) + 3 * len(tiles.self_kong) == NUMBER_TILES_IN_HAND + 1
        if len(losers) == self.player_count - 1 and not flowers8:  # self goal
            if _all_self:
                points.append((3, _key(PointType.ALL_SELF_GOAL), tuple()))
            else:
                if len(tiles.hand) == 2:
                    points.append((1, _key(PointType.HALF_NO_SELF), tuple()))
                points.append((1, _key(PointType.SELF_GOAL), tuple()))
            if len(self.tiles) == RESERVED_TILES:
                points.append((1, _key(PointType.SELF_GOAL_LAST_TILE), tuple()))
        else:
            if _all_self:
                points.append((1, _key(PointType.ALL_SELF), tuple()))
            elif len(tiles.hand) == 2:
                points.append((2, _key(PointType.NO_SELF), tuple()))

        winner_seat = (3 + sum(self.dice_result) + self.banker - winner) % 4

        if not flowers8 and PointType.FLOWER_7 not in extra_points:
            for f in (TileType.FLOWER.value + winner_seat, TileType.FLOWER.value+ 4 + winner_seat):
                if f in tiles.flowers:
                    points.append((1, _key(PointType.FLOWER), (f,)))

            if all((TileType.FLOWER.value + f) in tiles.flowers for f in range(4)):
                points.append((1, _key(PointType.FLOWER_KONG), tuple()))
            if all((TileType.FLOWER.value + f) in tiles.flowers for f in range(4, 8)):
                points.append((1, _key(PointType.FLOWER_KONG), tuple()))

        tile_counter = get_tile_counter(tiles.hand)
        def has_3(_t):
            return _t in tiles.shown_pong + tiles.shown_kong + tiles.self_kong or tile_counter.get(_t, 0) >= 3

        has_wind = [has_3(w) for w in range(TileType.WIND.value, TileType.WIND.value + 4)]
        if sum(has_wind) == 4:
            points.append((16, _key(PointType.BIG_WIND), tuple()))
        else:
            if sum(has_wind) == 3 and tile_counter.get(has_wind.index(False) + TileType.WIND.value, 0) == 2:
                points.append((8, _key(PointType.SMALL_WIND), tuple()))

            if has_3(TileType.WIND.value + self.round):
                points.append((1, _key(PointType.WIND_ROUND), (TileType.WIND.value + self.round,)))
            if has_3(TileType.WIND.value + winner_seat):
                points.append((1, _key(PointType.WIND_SEAT), (TileType.WIND.value + winner_seat,)))

        has_dragon = [has_3(d) for d in range(TileType.DRAGON.value, TileType.DRAGON.value + 3)]
        if sum(has_dragon) == 3:
            points.append((8, _key(PointType.BIG_DRAGON), tuple()))
        else:
            if sum(has_dragon) == 2 and tile_counter.get(has_dragon.index(False) + TileType.DRAGON.value, 0) == 2:
                points.append((4, _key(PointType.SMALL_DRAGON), tuple()))
            else:
                for i, h in enumerate(has_dragon):
                    if h:
                        points.append((1, _key(PointType.DRAGON), (TileType.DRAGON.value + i,)))

        cover_pong = len(tiles.self_kong)
        _hand = _hand_without_goal_tile.copy()
        i = 0
        while i + 2 < len(_hand):
            if _hand[i] == _hand[i + 1] and _hand[i] == _hand[i + 2]:
                if tiles.recent_tile in get_candidates(tuple(_hand[:i] + _hand[i+3:])):
                    _hand.pop(i)
                    _hand.pop(i)
                    _hand.pop(i)
                    cover_pong += 1
                    continue
            i += 1
        if cover_pong == 5:
            points.append((8, _key(PointType.COVER_PONG5), ()))
        elif cover_pong == 4:
            points.append((5, _key(PointType.COVER_PONG4), ()))
        elif cover_pong == 3:
            points.append((2, _key(PointType.COVER_PONG3), ()))

        _new_pong = int(tile_counter.get(tiles.recent_tile, 0) == 3)
        if cover_pong + len(tiles.shown_pong) + len(tiles.shown_kong) + _new_pong == 5 and sum(has_wind) != 4:
            points.append((4, _key(PointType.ALL_PONG), ()))

        if len(candidates) == 1:
            points.append((1, _key(PointType.SINGLE_CANDIDATE), ()))

        if all((
            cover_pong == 0,
            len(tiles.shown_kong) == 0,
            len(tiles.shown_pong) == 0,
            len(tiles.self_kong) == 0,
            all(get_tile_type(t) not in HONOR_TYPES for t in tiles.hand),
            len(tiles.flowers) == 0,
            len(candidates) > 1,
            len(losers) == 1,
        )):
            points.append((2, _key(PointType.SEQUENCE), ()))

        _all_tiles = tiles.hand + tiles.shown_pong + tiles.shown_chow + tiles.shown_kong + tiles.self_kong
        if all(get_tile_type(t) in HONOR_TYPES for t in _all_tiles):
            points.append((8, _key(PointType.ONLY_HONOR), ()))
        else:
            for suit in SUIT_TYPES:
                if all(get_tile_type(t) == suit for t in _all_tiles):
                    points.append((8, _key(PointType.ONE_SUIT), ()))
                    break
            else:
                for suit in SUIT_TYPES:
                    if all(get_tile_type(t) in (suit, TileType.DRAGON, TileType.WIND) for t in _all_tiles):
                        points.append((4, _key(PointType.ONE_SUIT_MIX), ()))
                        break

        return points, points_banker

    def _state_machine(self):
        state: GameState = GameState.START
        self._current_pid: int = self.banker

        can_goal = [True, True, True, True]
        winner = -1
        losers = tuple()
        game_result = [], []

        def next_player():
            self._current_pid = (self._current_pid + 1) % self.player_count

        while state != GameState.END:
            match state:
                case GameState.START:
                    winner = -1
                    losers = tuple()
                    game_result = [], []

                    for pt in self.player_tiles:
                        pt.clear()
                    _tiles = list(ALL_TILES)

                    self.random.shuffle(_tiles)
                    self.tiles = deque(_tiles)
                    del _tiles
                    yield self.banker, state, self.running, None
                    state += 1

                case GameState.ROLL_DICE:  # dice result doesn't matter in real random. It's for UI only
                    self.dice_result = [self.random.randint(1, 6), self.random.randint(1, 6), self.random.randint(1, 6)]
                    yield self.banker, state, self.dice_result, None
                    state += 1

                case GameState.INIT_DRAW:
                    for _ in range(4):  # 4 rounds
                        for _ in range(self.player_count):
                            for _ in range(4):
                                self.current_player.append_hand(self.tiles.popleft())
                            yield self._current_pid, state, self.current_player.hand[-4:], None
                            self.current_player.sort()
                            next_player()
                    state += 1

                case GameState.INIT_BANKER_DRAW:
                    assert self._current_pid == self.banker
                    new_tile = self.tiles.popleft()
                    self.current_player.append_hand(new_tile)
                    for p in self.player_tiles:
                        p.sort()
                    yield self._current_pid, state, new_tile, None
                    state += 1

                case GameState.INIT_FLOWER_SUPPLY:
                    resupply = False
                    for _ in range(self.player_count):
                        flower_count = self.current_player.check_flowers()
                        if flower_count:
                            resupply = True
                            for _ in range(flower_count):
                                self.current_player.append_hand(self.tiles.pop())
                            new_tiles = self.current_player.hand[-flower_count:]
                            self.current_player.sort()
                            yield self._current_pid, state, new_tiles, None
                        next_player()

                    if not resupply:
                        state = GameState.CHECK_DRAW_ACTION  # banker already drawn 1 extra tile in the beginning

                case GameState.DRAW:
                    self._kong_goal_available = False
                    self.current_player.append_hand(self.tiles.popleft())
                    if len(self.tiles) < RESERVED_TILES:
                        state = GameState.END
                    else:
                        yield self._current_pid, state, self.current_player.recent_tile, None
                        state = GameState.CHECK_DRAW_ACTION

                case GameState.SUPPLY:
                    self.current_player.append_hand(self.tiles.pop())
                    if len(self.tiles) < RESERVED_TILES and sum(len(p.flowers) for p in self.player_tiles) != 8:
                        state = GameState.END
                    else:
                        yield self._current_pid, state, self.current_player.recent_tile, None
                        state = GameState.CHECK_DRAW_ACTION

                case GameState.CHECK_DRAW_ACTION:  # self-goal, self-kong, extend-kong, flower
                    assert self.current_player.total_tiles == NUMBER_TILES_IN_HAND + 1

                    flower_count = self.current_player.check_flowers()
                    if flower_count:
                        assert flower_count == 1

                        state = GameState.SUPPLY
                        for i in range(1, self.player_count):
                            opponent = (self._current_pid + i) % self.player_count
                            if len(self.player_tiles[opponent].flowers) == 7:
                                state = GameState.END
                                winner = opponent
                                losers = (self._current_pid, )
                                game_result = self.game_result(winner, losers, extra_points=(PointType.FLOWER_7,))
                                break
                        continue

                    if len(self.current_player.flowers) == 8:
                        state = GameState.END
                        winner = self._current_pid
                        losers = tuple(i for i in range(self.player_count) if i != self._current_pid)
                        game_result = self.game_result(winner, losers)
                        continue

                    if len(self.current_player.flowers) == 7 and sum(len(p.flowers) for p in self.player_tiles) == 8:
                        state = GameState.END
                        winner = self._current_pid
                        losers = (next(i for i in range(4) if len(self.player_tiles[i].flowers) == 1), )
                        game_result = self.game_result(winner, losers, extra_points=(PointType.FLOWER_7,))
                        continue

                    actions = self.current_player.get_draw_actions(can_goal[self._current_pid])
                    self.current_player.sort()

                    _r = yield self._current_pid, GameState.CHECK_DRAW_ACTION, 0, actions
                    action, target = _r
                    match action:
                        case Action.SELF_GOAL:
                            if (Action.SELF_GOAL, target) not in actions:
                                continue
                            yield self._current_pid, GameState.ACTION_ACCEPTED, target, action
                            state = GameState.END
                            winner = self._current_pid
                            losers = tuple(i for i in range(self.player_count) if i != self._current_pid)
                            if self._kong_goal_available:
                                game_result = self.game_result(winner, losers, extra_points=(PointType.KONG_GOAL,))
                            else:
                                game_result = self.game_result(winner, losers)

                        case Action.SELF_KONG:
                            if not self.current_player.do_self_kong(target):
                                continue
                            yield self._current_pid, GameState.ACTION_ACCEPTED, target, action
                            self._kong_goal_available = True
                            state = GameState.SUPPLY

                        case Action.EXTEND_KONG:
                            if not self.current_player.do_extend_kong(target):
                                continue
                            yield self._current_pid, GameState.ACTION_ACCEPTED, target, action
                            can_goal[self._current_pid] = True
                            # check if the rest 3 players have goal to this self-kong tile
                            opponents = []
                            for i in range(1, self.player_count):
                                opponent = (self._current_pid + i) % self.player_count

                                assert self.player_tiles[opponent].total_tiles == NUMBER_TILES_IN_HAND

                                owner = (self.player_count + self._current_pid - opponent) % self.player_count  # get_actions() assume owner in [1, 2, 3]
                                opponent_actions = self.player_tiles[opponent].get_discard_actions(target, owner, can_goal[opponent])

                                if opponent_actions and opponent_actions[0] == (Action.GOAL, target):
                                    opponents.append(opponent)

                            opponents.sort(reverse=True, key=lambda x: (self._current_pid - x) % self.player_count)

                            state = GameState.SUPPLY
                            for opponent in opponents:
                                _r = yield opponent, GameState.CHECK_DISCARD_ACTION, self._current_pid, [(Action.GOAL, target), (Action.PASS, target)]
                                opponent_action, _ = _r
                                if opponent_action != Action.GOAL:
                                    can_goal[opponent] = False
                                else:
                                    yield opponent, GameState.ACTION_ACCEPTED, target, opponent_action
                                    self.player_tiles[opponent].do_goal(target)
                                    self.current_player.pop_extend_kong()
                                    winner = opponent
                                    losers = (self._current_pid,)
                                    game_result = self.game_result(winner, losers, extra_points=(PointType.EXTEND_KONG_GOAL,))
                                    self._current_pid = opponent  # move the turn to opponent
                                    state = GameState.END
                                    break
                            self._kong_goal_available = True

                        case Action.DISCARD:
                            if not self.current_player.do_discard(target):
                                continue
                            yield self._current_pid, GameState.ACTION_ACCEPTED, target, action
                            can_goal[self._current_pid] = True

                            # check if the rest 3 players have actions to this discarded tile
                            opponent_actions_in_sequence = []
                            for i in range(1, self.player_count):
                                opponent = (self._current_pid + i) % self.player_count

                                assert self.player_tiles[opponent].total_tiles == NUMBER_TILES_IN_HAND

                                owner = (self.player_count + self._current_pid - opponent) % self.player_count  # get_actions() assume owner in [1, 2, 3]
                                for action, _ in self.player_tiles[opponent].get_discard_actions(target, owner, can_goal[opponent]):
                                    opponent_actions_in_sequence.append((action, opponent))

                            # GOAL -> KONG/PONG -> CHOW, if multiple players can goal, the one who comes next does
                            opponent_actions_in_sequence.sort(key=lambda x: (x[0], (self._current_pid - x[1]) % self.player_count))
                            while opponent_actions_in_sequence:
                                _opponent_action, opponent = opponent_actions_in_sequence.pop(-1)
                                opponent_actions = [(_opponent_action, target)]
                                while opponent_actions_in_sequence and opponent_actions_in_sequence[-1][1] == opponent:
                                    _opponent_action, opponent = opponent_actions_in_sequence.pop(-1)
                                    opponent_actions.append((_opponent_action, target))
                                opponent_actions.append((Action.PASS, target))

                                _r = yield opponent, GameState.CHECK_DISCARD_ACTION, self._current_pid, opponent_actions
                                opponent_action, _ = _r
                                if (Action.GOAL, target) in opponent_actions and opponent_action != Action.GOAL:
                                    can_goal[opponent] = False

                                match opponent_action:
                                    case Action.GOAL:
                                        if (Action.GOAL, target) not in opponent_actions:
                                            continue  # TODO: allow opponent resending the action
                                        yield opponent, GameState.ACTION_ACCEPTED, target, opponent_action
                                        self.player_tiles[opponent].do_goal(target)
                                        self.current_player.pop_discard()
                                        winner = opponent
                                        losers = (self._current_pid,)
                                        game_result = self.game_result(winner, losers)
                                        self._current_pid = opponent  # move the turn to opponent
                                        state = GameState.END
                                        break

                                    case Action.KONG:
                                        if not self.player_tiles[opponent].do_kong(target):
                                            continue  # TODO: allow opponent resending the action
                                        yield opponent, GameState.ACTION_ACCEPTED, target, opponent_action
                                        self.current_player.pop_discard()
                                        self._current_pid = opponent  # move the turn to opponent
                                        state = GameState.SUPPLY
                                        self._kong_goal_available = True
                                        break

                                    case Action.PONG:
                                        if not self.player_tiles[opponent].do_pong(target):
                                            continue  # TODO: allow opponent resending the action
                                        yield opponent, GameState.ACTION_ACCEPTED, target, opponent_action
                                        self.current_player.pop_discard()
                                        self._current_pid = opponent  # move the turn to opponent
                                        self.current_player.recent_tile = self.current_player.hand[-1]
                                        state = GameState.CHECK_DRAW_ACTION
                                        break

                                    case Action.CHOW_LEFT:
                                        if not self.player_tiles[opponent].do_chow_left(target):
                                            continue  # TODO: allow opponent resending the action
                                        yield opponent, GameState.ACTION_ACCEPTED, target, opponent_action
                                        self.current_player.pop_discard()
                                        self._current_pid = opponent  # move the turn to opponent
                                        self.current_player.recent_tile = self.current_player.hand[-1]
                                        state = GameState.CHECK_DRAW_ACTION
                                        break

                                    case Action.CHOW_MIDDLE:
                                        if not self.player_tiles[opponent].do_chow_middle(target):
                                            continue  # TODO: allow opponent resending the action
                                        yield opponent, GameState.ACTION_ACCEPTED, target, opponent_action
                                        self.current_player.pop_discard()
                                        self._current_pid = opponent  # move the turn to opponent
                                        self.current_player.recent_tile = self.current_player.hand[-1]
                                        state = GameState.CHECK_DRAW_ACTION
                                        break

                                    case Action.CHOW_RIGHT:
                                        if not self.player_tiles[opponent].do_chow_right(target):
                                            continue  # TODO: allow opponent resending the action
                                        yield opponent, GameState.ACTION_ACCEPTED, target, opponent_action
                                        self.current_player.pop_discard()
                                        self._current_pid = opponent  # move the turn to opponent
                                        self.current_player.recent_tile = self.current_player.hand[-1]
                                        state = GameState.CHECK_DRAW_ACTION
                                        break

                                    case Action.PASS:
                                        yield opponent, GameState.ACTION_ACCEPTED, target, opponent_action

                                    case _:
                                        print("unexpected opponent_action", opponent_action)
                                        break
                            else:
                                state = GameState.DRAW
                                next_player()
                        case _:
                            print("unexpected action", action)
                            continue
                case _:
                    raise NotImplementedError

        banker = self.banker
        if winner not in [-1, self.banker]:
            if self.banker == self.player_count - 1:
                self.round = (self.round + 1) % 4
            self.running = 0
            self.banker = (self.banker + 1) % self.player_count
        else:
            self.running += 1

        # make sure this yield is at the end in case it ends before finalization
        yield banker, state, (winner, losers), game_result

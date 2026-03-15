import random

from apps.city.constants import (
    SIEGE_ADVANCE_ROUNDS,
    SIEGE_FUZZ_MAX,
    SIEGE_FUZZ_MIN,
    SIEGE_FUZZ_ROUND_TO,
    SIEGE_STRENGTH_MAX,
    SIEGE_STRENGTH_MIN,
)
from apps.city.services.siege.segment import WallSegmentService
from apps.savegame.models import PendingSiege, Savegame


class SiegeAnnouncementService:
    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def process(self) -> PendingSiege:
        actual_strength = self._roll_actual_strength()
        announced_strength = self._fuzz_strength(actual=actual_strength)
        direction = self._pick_direction()

        return PendingSiege.objects.create_pending_siege(
            savegame=self.savegame,
            attack_year=self.savegame.current_year + SIEGE_ADVANCE_ROUNDS,
            actual_strength=actual_strength,
            announced_strength=announced_strength,
            direction=direction,
        )

    def _roll_actual_strength(self) -> int:
        return random.randint(SIEGE_STRENGTH_MIN, SIEGE_STRENGTH_MAX)

    def _fuzz_strength(self, *, actual: int) -> int:
        fuzzed = actual * random.uniform(SIEGE_FUZZ_MIN, SIEGE_FUZZ_MAX)
        return round(fuzzed / SIEGE_FUZZ_ROUND_TO) * SIEGE_FUZZ_ROUND_TO

    def _pick_direction(self) -> str:
        segments = WallSegmentService(savegame=self.savegame).process()
        min_ratio = min(seg.hp_ratio for seg in segments.values())
        weakest = [direction for direction, seg in segments.items() if seg.hp_ratio == min_ratio]
        return random.choice(weakest)

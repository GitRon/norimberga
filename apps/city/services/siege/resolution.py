import random
from dataclasses import dataclass
from enum import Enum

from apps.city.constants import DIRECTION_NAMES, SIEGE_DAMAGED_THRESHOLD
from apps.city.events.effects.building.damage_wall import DamageWall
from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.models import Tile
from apps.city.services.siege.segment import WallSegment, WallSegmentService
from apps.savegame.models import PendingSiege, Savegame


@dataclass(kw_only=True)
class SiegeOutcome:
    class Result(str, Enum):
        REPELLED = "repelled"
        DAMAGED = "damaged"
        BREACHED = "breached"

    result: Result
    direction: str
    attacker_strength: int
    defense_score: int
    wall_damage: int
    buildings_damaged: int
    population_lost: int
    report_text: str


class SiegeResolutionService:
    def __init__(self, *, savegame: Savegame, pending_siege: PendingSiege):
        self.savegame = savegame
        self.pending_siege = pending_siege

    def process(self) -> SiegeOutcome:
        segment = self._get_target_segment()
        defense_score = self._calculate_defense_score(segment=segment)
        result = self._determine_outcome(
            defense_score=defense_score, attacker_strength=self.pending_siege.actual_strength
        )

        if result == SiegeOutcome.Result.REPELLED:
            return self._apply_repelled(segment=segment, defense_score=defense_score)
        elif result == SiegeOutcome.Result.DAMAGED:
            return self._apply_damaged(segment=segment, defense_score=defense_score)
        else:
            return self._apply_breached(segment=segment, defense_score=defense_score)

    def _get_target_segment(self) -> WallSegment:
        segments = WallSegmentService(savegame=self.savegame).process()
        return segments[self.pending_siege.direction]

    def _calculate_defense_score(self, *, segment: WallSegment) -> int:
        return segment.total_hp

    def _determine_outcome(self, *, defense_score: int, attacker_strength: int) -> SiegeOutcome.Result:
        if defense_score >= attacker_strength:
            return SiegeOutcome.Result.REPELLED
        elif defense_score >= attacker_strength * SIEGE_DAMAGED_THRESHOLD:
            return SiegeOutcome.Result.DAMAGED
        else:
            return SiegeOutcome.Result.BREACHED

    def _apply_repelled(self, *, segment: WallSegment, defense_score: int) -> SiegeOutcome:
        direction_name = DIRECTION_NAMES.get(self.pending_siege.direction, self.pending_siege.direction)
        attacker_strength = self.pending_siege.actual_strength

        tiles_to_damage = segment.tiles[: max(1, len(segment.tiles) // 5)]
        wall_damage = 0
        damage_per_tile = max(1, attacker_strength // 4)

        for tile in tiles_to_damage:
            if tile.wall_hitpoints is not None:
                actual = min(damage_per_tile, tile.wall_hitpoints)
                wall_damage += actual
                DamageWall(tile=tile, damage=damage_per_tile).process()

        report = (
            f"The enemy force of {attacker_strength} warriors was repelled at the {direction_name} wall. "
            f"Your defenses held strong with {defense_score} defense points. "
            f"Minor wall damage of {wall_damage} HP was sustained."
        )

        return SiegeOutcome(
            result=SiegeOutcome.Result.REPELLED,
            direction=self.pending_siege.direction,
            attacker_strength=attacker_strength,
            defense_score=defense_score,
            wall_damage=wall_damage,
            buildings_damaged=0,
            population_lost=0,
            report_text=report,
        )

    def _apply_damaged(self, *, segment: WallSegment, defense_score: int) -> SiegeOutcome:
        direction_name = DIRECTION_NAMES.get(self.pending_siege.direction, self.pending_siege.direction)
        attacker_strength = self.pending_siege.actual_strength

        tiles_to_damage = segment.tiles[: max(1, len(segment.tiles) * 2 // 5)]
        wall_damage = 0
        damage_per_tile = max(1, attacker_strength // 2)

        for tile in tiles_to_damage:
            if tile.wall_hitpoints is not None:
                actual = min(damage_per_tile, tile.wall_hitpoints)
                wall_damage += actual
                DamageWall(tile=tile, damage=damage_per_tile).process()

        buildings_damaged = self._remove_random_city_buildings(count=1)

        report = (
            f"The {direction_name} wall was damaged but held against the enemy force of {attacker_strength} warriors. "
            f"Defense score: {defense_score}. Wall damage: {wall_damage} HP. "
            f"{buildings_damaged} building{'s' if buildings_damaged != 1 else ''} destroyed in the fighting."
        )

        return SiegeOutcome(
            result=SiegeOutcome.Result.DAMAGED,
            direction=self.pending_siege.direction,
            attacker_strength=attacker_strength,
            defense_score=defense_score,
            wall_damage=wall_damage,
            buildings_damaged=buildings_damaged,
            population_lost=0,
            report_text=report,
        )

    def _apply_breached(self, *, segment: WallSegment, defense_score: int) -> SiegeOutcome:
        direction_name = DIRECTION_NAMES.get(self.pending_siege.direction, self.pending_siege.direction)
        attacker_strength = self.pending_siege.actual_strength

        tiles_to_destroy_count = random.randint(1, 3)
        available_tiles = [t for t in segment.tiles if t.wall_hitpoints is not None and t.wall_hitpoints > 0]
        tiles_to_destroy = random.sample(available_tiles, min(tiles_to_destroy_count, len(available_tiles)))

        wall_damage = 0
        for tile in tiles_to_destroy:
            wall_damage += tile.wall_hitpoints
            DamageWall(tile=tile, damage=tile.wall_hitpoints).process()

        buildings_to_remove = random.randint(1, 2)
        buildings_damaged = self._remove_random_city_buildings(count=buildings_to_remove)

        population_lost = random.randint(5, 20)
        from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute

        DecreasePopulationAbsolute(lost_population=population_lost).process(savegame=self.savegame)

        destroyed_count = len(tiles_to_destroy)
        report = (
            f"The {direction_name} wall was BREACHED by the enemy force of {attacker_strength} warriors! "
            f"Defense score: {defense_score}. "
            f"{destroyed_count} wall section{'s' if destroyed_count != 1 else ''} reduced to ruins. "
            f"{buildings_damaged} building{'s' if buildings_damaged != 1 else ''} destroyed. "
            f"{population_lost} inhabitants perished."
        )

        return SiegeOutcome(
            result=SiegeOutcome.Result.BREACHED,
            direction=self.pending_siege.direction,
            attacker_strength=attacker_strength,
            defense_score=defense_score,
            wall_damage=wall_damage,
            buildings_damaged=buildings_damaged,
            population_lost=population_lost,
            report_text=report,
        )

    def _remove_random_city_buildings(self, *, count: int) -> int:
        eligible_tiles = Tile.objects.get_random_city_buildings(savegame=self.savegame, count=count)

        for tile in eligible_tiles:
            RemoveBuilding(tile=tile).process()

        return len(eligible_tiles)

import typing

from django.db import models

if typing.TYPE_CHECKING:
    from apps.savegame.models import Savegame, SiegeChronicle


class SiegeChronicleManager(models.Manager):
    def create_chronicle(
        self,
        *,
        savegame: "Savegame",
        year: int,
        direction: str,
        attacker_strength: int,
        defense_score: int,
        result: str,
        report_text: str,
    ) -> "SiegeChronicle":
        return self.create(
            savegame=savegame,
            year=year,
            direction=direction,
            attacker_strength=attacker_strength,
            defense_score=defense_score,
            result=result,
            report_text=report_text,
        )

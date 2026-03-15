from apps.city.services.siege.resolution import SiegeOutcome, SiegeResolutionService
from apps.event.models import EventNotification
from apps.savegame.models import PendingSiege, Savegame, SiegeChronicle


class SiegePipelineService:
    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def process(self) -> SiegeOutcome | None:
        pending_siege = self._get_due_siege()
        if pending_siege is None:
            return None

        outcome = self._resolve(pending_siege=pending_siege)
        self._create_chronicle(outcome=outcome, pending_siege=pending_siege)
        self._create_notification(outcome=outcome)

        pending_siege.resolved = True
        pending_siege.save()

        return outcome

    def _get_due_siege(self) -> PendingSiege | None:
        return self.savegame.pending_sieges.filter(
            resolved=False,
            attack_year=self.savegame.current_year,
        ).first()

    def _resolve(self, *, pending_siege: PendingSiege) -> SiegeOutcome:
        return SiegeResolutionService(savegame=self.savegame, pending_siege=pending_siege).process()

    def _create_chronicle(self, *, outcome: SiegeOutcome, pending_siege: PendingSiege) -> SiegeChronicle:
        return SiegeChronicle.objects.create(
            savegame=self.savegame,
            year=pending_siege.attack_year,
            direction=outcome.direction,
            attacker_strength=outcome.attacker_strength,
            defense_score=outcome.defense_score,
            result=outcome.result.value,
            report_text=outcome.report_text,
        )

    def _create_notification(self, *, outcome: SiegeOutcome) -> EventNotification:
        result_labels = {
            SiegeOutcome.Result.REPELLED: "Enemy Repelled",
            SiegeOutcome.Result.DAMAGED: "Wall Damaged",
            SiegeOutcome.Result.BREACHED: "Wall Breached!",
        }
        title = f"Battle Report: {result_labels.get(outcome.result, 'Siege Resolved')}"

        return EventNotification.objects.create(
            savegame=self.savegame,
            year=self.savegame.current_year,
            title=title,
            message=outcome.report_text,
            acknowledged=False,
        )

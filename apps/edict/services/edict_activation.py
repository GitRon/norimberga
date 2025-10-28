from dataclasses import dataclass

from apps.edict.models import Edict, EdictLog
from apps.milestone.selectors.milestone import get_completed_milestone_ids
from apps.savegame.models import Savegame


@dataclass(kw_only=True)
class EdictActivationResult:
    """Result of edict activation attempt."""

    success: bool
    message: str


class EdictActivationService:
    """Service to handle edict activation logic."""

    def __init__(self, *, savegame: Savegame, edict: Edict):
        self.savegame = savegame
        self.edict = edict

    def process(self) -> EdictActivationResult:
        """
        Main entry point for edict activation.

        Returns:
            EdictActivationResult with success status and message
        """
        # Validate edict is active
        if not self.edict.is_active:
            return EdictActivationResult(success=False, message="This edict is not currently available.")

        # Check milestone requirement
        milestone_validation = self._validate_milestone_requirement()
        if not milestone_validation.success:
            return milestone_validation

        # Check prestige requirement
        prestige_validation = self._validate_prestige_requirement()
        if not prestige_validation.success:
            return prestige_validation

        # Check cooldown
        if not self._is_edict_available():
            return EdictActivationResult(
                success=False,
                message=f"This edict is on cooldown. Wait {self.edict.cooldown_years} years between uses.",
            )

        # Validate costs
        cost_validation = self._validate_costs()
        if not cost_validation.success:
            return cost_validation

        # Apply costs and effects
        self._apply_costs()
        self._apply_effects()

        # Create log entry
        EdictLog.objects.create(
            savegame=self.savegame,
            edict=self.edict,
            activated_at_year=self.savegame.current_year,
        )

        # Save savegame
        self.savegame.save()

        return EdictActivationResult(success=True, message=f"Edict '{self.edict.name}' has been activated!")

    def _validate_milestone_requirement(self) -> EdictActivationResult:
        """Validate that required milestone has been completed."""
        if self.edict.required_milestone_id is None:
            return EdictActivationResult(success=True, message="")

        completed_milestone_ids = get_completed_milestone_ids(savegame=self.savegame)
        if self.edict.required_milestone_id not in completed_milestone_ids:
            milestone_name = self.edict.required_milestone.name
            return EdictActivationResult(
                success=False,
                message=f"This edict requires the '{milestone_name}' milestone to be completed first.",
            )

        return EdictActivationResult(success=True, message="")

    def _validate_prestige_requirement(self) -> EdictActivationResult:
        """Validate that required prestige level has been reached."""
        if self.edict.required_prestige is None:
            return EdictActivationResult(success=True, message="")

        from apps.city.services.prestige import PrestigeCalculationService

        prestige_service = PrestigeCalculationService(savegame=self.savegame)
        current_prestige = prestige_service.process()

        if current_prestige < self.edict.required_prestige:
            return EdictActivationResult(
                success=False,
                message=f"This edict requires {self.edict.required_prestige} prestige. You have {current_prestige}.",
            )

        return EdictActivationResult(success=True, message="")

    def _is_edict_available(self) -> bool:
        """Check if edict is available based on cooldown."""
        if self.edict.cooldown_years is None:
            return True

        # Get last activation
        last_log = (
            EdictLog.objects.filter(savegame=self.savegame, edict=self.edict).order_by("-activated_at_year").first()
        )

        if last_log is None:
            return True

        years_since_last = self.savegame.current_year - last_log.activated_at_year
        return years_since_last >= self.edict.cooldown_years

    def _validate_costs(self) -> EdictActivationResult:
        """Validate that savegame has enough resources to pay costs."""
        if self.edict.cost_coins is not None and self.savegame.coins < self.edict.cost_coins:
            return EdictActivationResult(
                success=False,
                message=f"Not enough coins. Need {self.edict.cost_coins}, have {self.savegame.coins}.",
            )

        if self.edict.cost_population is not None and self.savegame.population < self.edict.cost_population:
            return EdictActivationResult(
                success=False,
                message=f"Not enough population. Need {self.edict.cost_population}, have {self.savegame.population}.",
            )

        # Note: cost_prestige is not validated here because prestige is calculated from buildings
        # and cannot be "spent". Use required_prestige for prestige requirements instead.

        return EdictActivationResult(success=True, message="")

    def _apply_costs(self) -> None:
        """Deduct costs from savegame."""
        if self.edict.cost_coins is not None:
            self.savegame.coins -= self.edict.cost_coins

        if self.edict.cost_population is not None:
            self.savegame.population -= self.edict.cost_population

    def _apply_effects(self) -> None:
        """Apply effects to savegame."""
        if self.edict.effect_unrest is not None:
            new_unrest = self.savegame.unrest + self.edict.effect_unrest
            # Clamp unrest between 0 and 100
            self.savegame.unrest = max(0, min(100, new_unrest))

        if self.edict.effect_coins is not None:
            self.savegame.coins += self.edict.effect_coins

        if self.edict.effect_population is not None:
            new_population = self.savegame.population + self.edict.effect_population
            # Ensure population doesn't go negative
            self.savegame.population = max(0, new_population)

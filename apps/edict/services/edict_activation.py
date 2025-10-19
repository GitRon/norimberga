from dataclasses import dataclass

from apps.city.models import Savegame
from apps.edict.models import Edict, EdictLog


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

from dataclasses import dataclass


@dataclass(kw_only=True)
class Choice:
    """
    Represents a user choice for an event.

    Attributes:
        label: The button text shown to the user (e.g., "Pay the ransom")
        description: Explanation of what this choice does and its consequences
        effects: List of effect instances to apply when this choice is selected
    """

    label: str
    description: str
    effects: list

    def apply_effects(self, *, savegame) -> None:
        """Apply all effects associated with this choice to the given savegame."""
        for effect in self.effects:
            if effect is not None:
                effect.process(savegame=savegame)

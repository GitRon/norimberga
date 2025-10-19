from apps.edict.models import Edict, EdictLog
from apps.savegame.models import Savegame


def get_available_edicts_for_savegame(*, savegame: Savegame) -> list[dict]:
    """
    Get all active edicts with availability information for a savegame.

    Returns:
        List of dicts containing edict and availability information
    """
    edicts = Edict.objects.filter(is_active=True).order_by("name")
    result = []

    for edict in edicts:
        availability_info = _get_edict_availability_info(savegame=savegame, edict=edict)
        result.append(
            {
                "edict": edict,
                "is_available": availability_info["is_available"],
                "unavailable_reason": availability_info["unavailable_reason"],
                "can_afford": availability_info["can_afford"],
            }
        )

    return result


def _get_edict_availability_info(*, savegame: Savegame, edict: Edict) -> dict:
    """Get availability information for a specific edict."""
    # Check cooldown
    if edict.cooldown_years is not None:
        last_log = EdictLog.objects.filter(savegame=savegame, edict=edict).order_by("-activated_at_year").first()

        if last_log is not None:
            years_since_last = savegame.current_year - last_log.activated_at_year
            if years_since_last < edict.cooldown_years:
                years_remaining = edict.cooldown_years - years_since_last
                return {
                    "is_available": False,
                    "unavailable_reason": f"Cooldown: {years_remaining} years remaining",
                    "can_afford": False,
                }

    # Check if can afford
    can_afford = True
    if edict.cost_coins is not None and savegame.coins < edict.cost_coins:
        can_afford = False

    if edict.cost_population is not None and savegame.population < edict.cost_population:
        can_afford = False

    return {
        "is_available": True,
        "unavailable_reason": None,
        "can_afford": can_afford,
    }

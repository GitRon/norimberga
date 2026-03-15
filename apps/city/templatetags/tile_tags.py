from django import template

from apps.city.models import Tile

register = template.Library()


@register.filter
def wall_hp_percent(tile: Tile) -> int | None:
    """Return current wall HP as a percentage (0-100), or None if not a wall."""
    if tile.wall_hitpoints is None or tile.wall_hitpoints_max is None:
        return None
    return int(tile.wall_hitpoints / tile.wall_hitpoints_max * 100)

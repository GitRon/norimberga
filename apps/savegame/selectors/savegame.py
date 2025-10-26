from collections import defaultdict

from apps.savegame.models import Savegame


def get_balance_data(*, savegame: Savegame) -> dict:
    """
    Calculate the balance per round for a savegame with detailed breakdown.

    Returns a dictionary containing:
    - savegame: The Savegame instance
    - taxes: Total tax income from buildings
    - maintenance: Total maintenance costs from buildings
    - balance: Net balance (taxes - maintenance)
    - tax_by_building_type: Dict mapping building type names to lists of building tax data
    - maintenance_by_building_type: Dict mapping building type names to lists of building maintenance data
    """

    # Use manager methods for aggregations
    taxes = Savegame.objects.aggregate_taxes(savegame=savegame)
    maintenance = Savegame.objects.aggregate_maintenance_costs(savegame=savegame)

    # Get detailed breakdown by building type and building
    tax_by_building_type = _get_tax_by_building_type(savegame=savegame)
    maintenance_by_building_type = _get_maintenance_by_building_type(savegame=savegame)

    # Calculate balance
    balance = taxes - maintenance

    return {
        "savegame": savegame,
        "taxes": taxes,
        "maintenance": maintenance,
        "balance": balance,
        "tax_by_building_type": tax_by_building_type,
        "maintenance_by_building_type": maintenance_by_building_type,
    }


def _get_tax_by_building_type(*, savegame) -> dict:
    """
    Get tax income grouped by building type and then by individual buildings.

    Returns a dict like:
    {
        "House": {
            "buildings": [
                {"name": "Small House", "level": 1, "count": 3, "taxes_per_building": 10, "total": 30},
                {"name": "Large House", "level": 2, "count": 1, "taxes_per_building": 20, "total": 20},
            ],
            "subtotal": 50
        },
        "Workshop": {...}
    }
    """
    tiles = savegame.tiles.select_related("building__building_type").filter(building__isnull=False)

    # Group by building type and building name
    grouped = defaultdict(lambda: defaultdict(lambda: {"count": 0, "taxes": 0, "level": 0}))

    for tile in tiles:
        building = tile.building
        if building.taxes > 0:
            building_type_name = building.building_type.name
            building_name = building.name
            grouped[building_type_name][building_name]["count"] += 1
            grouped[building_type_name][building_name]["taxes"] = building.taxes
            grouped[building_type_name][building_name]["level"] = building.level

    # Convert to final structure with subtotals
    result = {}
    for building_type_name, buildings in sorted(grouped.items()):
        buildings_data = []
        subtotal = 0
        for building_name, data in sorted(buildings.items()):
            total = data["count"] * data["taxes"]
            subtotal += total
            buildings_data.append(
                {
                    "name": building_name,
                    "level": data["level"],
                    "count": data["count"],
                    "taxes_per_building": data["taxes"],
                    "total": total,
                }
            )
        result[building_type_name] = {
            "buildings": buildings_data,
            "subtotal": subtotal,
        }

    return result


def _get_maintenance_by_building_type(*, savegame) -> dict:
    """
    Get maintenance costs grouped by building type and then by individual buildings.

    Returns a dict like:
    {
        "House": {
            "buildings": [
                {"name": "Small House", "level": 1, "count": 3, "maintenance_per_building": 5, "total": 15},
                {"name": "Large House", "level": 2, "count": 1, "maintenance_per_building": 10, "total": 10},
            ],
            "subtotal": 25
        },
        "Workshop": {...}
    }
    """
    tiles = savegame.tiles.select_related("building__building_type").filter(building__isnull=False)

    # Group by building type and building name
    grouped = defaultdict(lambda: defaultdict(lambda: {"count": 0, "maintenance": 0, "level": 0}))

    for tile in tiles:
        building = tile.building
        if building.maintenance_costs > 0:
            building_type_name = building.building_type.name
            building_name = building.name
            grouped[building_type_name][building_name]["count"] += 1
            grouped[building_type_name][building_name]["maintenance"] = building.maintenance_costs
            grouped[building_type_name][building_name]["level"] = building.level

    # Convert to final structure with subtotals
    result = {}
    for building_type_name, buildings in sorted(grouped.items()):
        buildings_data = []
        subtotal = 0
        for building_name, data in sorted(buildings.items()):
            total = data["count"] * data["maintenance"]
            subtotal += total
            buildings_data.append(
                {
                    "name": building_name,
                    "level": data["level"],
                    "count": data["count"],
                    "maintenance_per_building": data["maintenance"],
                    "total": total,
                }
            )
        result[building_type_name] = {
            "buildings": buildings_data,
            "subtotal": subtotal,
        }

    return result

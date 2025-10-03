from apps.city.models import Savegame


def get_balance_data(savegame_id: int) -> dict:
    """
    Calculate the balance per round for a savegame.

    Returns a dictionary containing:
    - savegame: The Savegame instance
    - taxes: Total tax income from buildings
    - maintenance: Total maintenance costs from buildings
    - balance: Net balance (taxes - maintenance)
    """
    savegame = Savegame.objects.get(id=savegame_id)

    # Use manager methods for aggregations
    taxes = Savegame.objects.aggregate_taxes(savegame)
    maintenance = Savegame.objects.aggregate_maintenance_costs(savegame)

    # Calculate balance
    balance = taxes - maintenance

    return {
        "savegame": savegame,
        "taxes": taxes,
        "maintenance": maintenance,
        "balance": balance,
    }

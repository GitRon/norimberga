# Edict Fixtures

This directory contains fixture data for the edict system.

## Available Fixtures

### edicts.json
Contains 5 predefined edicts that players can activate in their cities:

1. **Give Bread to the Poor** - Costs 100 coins, reduces unrest by 10, cooldown 2 years
2. **Grand Festival** - Costs 200 coins, reduces unrest by 15, cooldown 3 years
3. **Conscription** - Costs 50 population, grants 500 coins but increases unrest by 20, cooldown 5 years
4. **Tax Holiday** - Costs 300 coins, reduces unrest by 20, cooldown 4 years
5. **Public Works** - Costs 150 coins, reduces unrest by 12, cooldown 2 years

## Loading Fixtures

To load the edict fixtures into your database:

```bash
python manage.py loaddata apps/edict/fixtures/edicts.json
```

## Creating Custom Edicts

You can create custom edicts through:

1. **Django Admin** - Add edicts through the admin interface at `/admin/edict/edict/`
2. **Custom Fixtures** - Create your own JSON fixture files
3. **Direct Database** - Create edicts programmatically in the Django shell

### Example Custom Edict

```json
{
  "model": "edict.edict",
  "pk": 10,
  "fields": {
    "name": "Military Parade",
    "description": "Show off your military might to impress the populace and neighboring cities.",
    "cost_coins": 250,
    "cost_population": null,
    "effect_unrest": -8,
    "effect_coins": null,
    "effect_population": null,
    "cooldown_years": 3,
    "is_active": true
  }
}
```

## Edict Fields

- `name` - Display name of the edict
- `description` - Flavor text explaining what the edict does
- `cost_coins` - Coins required to activate (null if no coin cost)
- `cost_population` - Population required to activate (null if no population cost)
- `effect_unrest` - How much unrest changes (negative reduces, positive increases)
- `effect_coins` - How many coins are added/removed after activation
- `effect_population` - How much population changes after activation
- `cooldown_years` - Years before edict can be activated again (null if no cooldown)
- `is_active` - Whether the edict is available to players (admin toggle)

## Notes

- Edicts can have costs and effects on coins, population, and unrest
- Null values mean no cost/effect for that resource
- Unrest is clamped between 0 and 100 automatically
- Population cannot go below 0
- Players can only activate edicts they can afford
- Cooldowns are tracked per savegame in the EdictLog model
- Inactive edicts (is_active=false) are hidden from players

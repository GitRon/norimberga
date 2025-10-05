# Milestone Fixtures

This directory contains fixture data for the milestone system.

## Available Fixtures

### milestones.json
Contains 10 predefined milestones organized in two progression trees:

**Population Tree (Main progression towards Freie Reichsstadt):**
1. First Settlement (10 population)
2. Growing Village (50 population)
3. Prosperous Village (100 population)
4. Small Town (200 population)
5. Fortified Town (300 population)
6. Major City (500 population)
7. Trade Hub (750 population)
8. Freie Reichsstadt (1000 population + 10,000 coins + year 1200)

**Wealth Tree:**
9. First Coins (500 coins)
10. Wealthy City (5,000 coins + 200 population)

### milestone_conditions.json
Contains 13 milestone conditions that define the requirements for each milestone.

Each milestone can have multiple conditions (all must be met). The conditions use these classes:
- `MinPopulationCondition` - Requires minimum population
- `MinCoinsCondition` - Requires minimum treasury balance
- `MinYearCondition` - Requires reaching a certain year

## Loading Fixtures

To load the milestone fixtures into your database:

```bash
# Load milestones first (required before conditions)
python manage.py loaddata apps/milestone/fixtures/milestones.json

# Then load milestone conditions
python manage.py loaddata apps/milestone/fixtures/milestone_conditions.json
```

Or load both at once:
```bash
python manage.py loaddata apps/milestone/fixtures/milestones.json apps/milestone/fixtures/milestone_conditions.json
```

## Creating Custom Milestones

You can create custom milestones through:

1. **Django Admin** - Add milestones and conditions through the admin interface
2. **Custom Fixtures** - Create your own JSON fixture files
3. **Data Migrations** - Use Django data migrations for version-controlled milestones

### Available Condition Classes

- `apps.milestone.conditions.population.MinPopulationCondition` - Check population
- `apps.milestone.conditions.coins.MinCoinsCondition` - Check treasury balance
- `apps.milestone.conditions.year.MinYearCondition` - Check current year

### Example Custom Milestone

```json
{
  "model": "milestone.milestone",
  "pk": 99,
  "fields": {
    "name": "Medieval Metropolis",
    "description": "Build a city larger than any in the region",
    "parent": 8,
    "order": 100
  }
}
```

With conditions:
```json
{
  "model": "milestone.milestonecondition",
  "pk": 99,
  "fields": {
    "milestone": 99,
    "condition_class": "apps.milestone.conditions.population.MinPopulationCondition",
    "value": "2000"
  }
}
```

## Notes

- Milestones with `parent=null` are root milestones (available from the start)
- Child milestones are only available after their parent is completed
- The `order` field controls display order within the same tree level
- All conditions for a milestone must be met for it to be completed
- Conditions are checked automatically at the end of each round

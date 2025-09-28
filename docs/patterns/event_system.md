# Event System

The Norimberga game uses a sophisticated event system to create dynamic gameplay experiences. The system is built around two main concepts: **Events** and **Event Effects**.

## Architecture Overview

```
Event System
├── Events (apps/city/events/events/)           # Human-readable game events
├── Event Effects (apps/city/events/effects/)  # Reusable effect components
├── Event Selection Service (apps/event/)      # Event discovery and execution
└── Base Classes (apps/event/events/events/)   # Abstract base classes
```

## Core Components

### 1. Events

Events represent human-readable game occurrences with narrative context. Each event:
- Has a probability of occurring
- Contains descriptive text for the player
- Composes multiple effects to achieve its outcome
- Includes UI metadata (title, message level)

**Location**: `apps/city/events/events/`

**Base Class**: `BaseEvent` (`apps/event/events/events/base_event.py`)

#### Event Structure

```python
class Event(BaseEvent):
    PROBABILITY = 15                    # Base probability (0-100)
    LEVEL = messages.SUCCESS           # Django message level for UI
    TITLE = "Event Name"               # Display title

    def __init__(self):
        # Initialize event-specific data
        self.savegame = Savegame.objects.get(id=1)
        self.random_value = random.randint(1, 10)

    def get_probability(self):
        # Dynamic probability based on game state
        return super().get_probability() if self.condition_met() else 0

    def _prepare_effect_action_name(self):
        # Return effect instances (methods prefixed with "_prepare_effect")
        return SomeEffect(parameter=self.random_value)

    def get_verbose_text(self):
        # Return human-readable description of what happened
        return "A detailed description of the event outcome."
```

#### Key Event Methods

- **`get_probability()`**: Returns dynamic probability based on game state
- **`_prepare_effect_*`**: Methods that instantiate and configure effects
- **`get_verbose_text()`**: Provides narrative description after event execution
- **`process()`**: Inherited method that executes all effects and returns verbose text

### 2. Event Effects

Effects are reusable, single-purpose components that perform specific game state modifications. They follow the Single Responsibility Principle.

**Location**: `apps/city/events/effects/`

#### Effect Categories

##### Savegame Effects (`apps/city/events/effects/savegame/`)
Modify global game state:

- `DecreaseUnrestAbsolute` - Reduces unrest by absolute amount
- `IncreaseUnrestAbsolute` - Increases unrest by absolute amount
- `DecreasePopulationAbsolute` - Reduces population by absolute amount
- `DecreasePopulationRelative` - Reduces population by percentage
- `IncreasePopulationAbsolute` - Increases population by absolute amount
- `IncreasePopulationRelative` - Increases population by percentage
- `DecreaseCoins` - Reduces available coins
- `IncreaseCoins` - Increases available coins

##### Building Effects (`apps/city/events/effects/building/`)
Modify city infrastructure:

- `RemoveBuilding` - Removes a building from a tile

#### Effect Structure

```python
class EffectName:
    def __init__(self, parameter: int):
        self.parameter = parameter

    def process(self):
        # Perform the actual game state modification
        savegame = Savegame.objects.get(id=1)
        savegame.field = max(savegame.field - self.parameter, 0)
        savegame.save()
```

### 3. Event Selection Service

The `EventSelectionService` (`apps/event/services/selection.py`) handles automatic discovery and selection of events.

#### How It Works

1. **Discovery**: Scans all local apps for `events/events/` packages
2. **Import**: Dynamically imports all Python files containing `Event` classes
3. **Validation**: Ensures classes inherit from `BaseEvent`
4. **Probability Check**: Rolls against each event's probability
5. **Selection**: Returns list of events that passed probability checks

```python
service = EventSelectionService()
selected_events = service.process()  # Returns list[BaseEvent]

for event in selected_events:
    result_text = event.process()  # Execute event and get description
```

## Event Examples

### Simple Event: Alms
```python
class Event(BaseEvent):
    PROBABILITY = 15
    LEVEL = messages.SUCCESS
    TITLE = "Alms"

    def __init__(self):
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.initial_unrest = self.savegame.unrest
        self.lost_unrest = random.randint(3, 5)

    def get_probability(self):
        return super().get_probability() if self.savegame.unrest > 0 else 0

    def _prepare_effect_decrease_unrest(self):
        return DecreaseUnrestAbsolute(lost_unrest=self.lost_unrest)

    def get_verbose_text(self):
        self.savegame.refresh_from_db()
        return (
            f"Members of the city council decided to provide alms for the sick and poor. "
            f"The unrest drops by {self.initial_unrest - self.savegame.unrest}%."
        )
```

### Complex Event: Fire
```python
class Event(BaseEvent):
    PROBABILITY = 5
    LEVEL = messages.ERROR
    TITLE = "Fire"

    def __init__(self):
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.initial_population = self.savegame.population
        self.lost_population = random.randint(10, 50)
        self.affected_tile = self.savegame.tiles.filter(
            building__building_type__is_house=True
        ).first()

    def get_probability(self):
        return super().get_probability() if self.savegame.population > 0 else 0

    def _prepare_effect_decrease_population(self):
        return DecreasePopulationAbsolute(lost_population=self.lost_population)

    def _prepare_effect_remove_building(self):
        if self.affected_tile:
            return RemoveBuilding(tile=self.affected_tile)
        return None  # Effect can be conditional

    def get_verbose_text(self):
        self.savegame.refresh_from_db()
        message = (
            f"Due to general neglect, a fire raged throughout the city, killing "
            f"{self.initial_population - self.savegame.population} citizens."
        )
        if self.affected_tile:
            message += f" The fire started in building {self.affected_tile} and destroyed it."
        return message
```

## Best Practices

### Creating New Events

1. **Inherit from BaseEvent**: Always extend the base class
2. **Set Class Attributes**: Define `PROBABILITY`, `LEVEL`, and `TITLE`
3. **Initialize State**: Set up event-specific data in `__init__`
4. **Dynamic Probability**: Override `get_probability()` for conditional events
5. **Compose Effects**: Use `_prepare_effect_*` methods to combine reusable effects
6. **Descriptive Text**: Provide engaging narrative in `get_verbose_text()`

### Creating New Effects

1. **Single Responsibility**: Each effect should do exactly one thing
2. **Parameterized**: Accept configuration through constructor
3. **Idempotent**: Effects should be safe to run multiple times
4. **Validation**: Include bounds checking and error handling
5. **Atomic**: Keep database operations as atomic as possible

### File Organization

```
apps/
├── city/events/
│   ├── events/           # Game-specific events
│   │   ├── alms.py
│   │   ├── fire.py
│   │   └── ...
│   └── effects/          # Reusable effects
│       ├── savegame/     # Global state effects
│       │   ├── decrease_unrest_absolute.py
│       │   └── ...
│       └── building/     # Building-specific effects
│           ├── remove_building.py
│           └── ...
└── event/                # Core event system
    ├── events/events/    # Base classes
    │   └── base_event.py
    └── services/         # Event processing
        └── selection.py
```

## Integration Points

### With Game Loop
Events are typically triggered during round processing or specific game actions. The event system integrates with:

- **Round Management**: Events can be triggered each game turn
- **User Actions**: Events can be consequence of player decisions
- **State Monitoring**: Events can respond to specific game conditions

### With UI System
Events provide user feedback through:

- **Message Levels**: Using Django's message framework levels
- **Titles**: Short, descriptive event names
- **Verbose Text**: Detailed narrative descriptions
- **Icons/Graphics**: Can be associated with event types

### With Savegame System
Events modify persistent game state through:

- **Direct Model Updates**: Via effect classes
- **Transactional Safety**: Each effect should maintain data integrity
- **State Validation**: Effects should enforce game rules and constraints

## Technical Notes

### Effect Discovery
The `BaseEvent.get_effects()` method uses Python's `inspect` module to automatically discover all methods prefixed with `_prepare_effect`. This allows for flexible event composition without explicit effect registration.

### Dynamic Probability
Events can modify their probability based on game state by overriding `get_probability()`. Return `0` to prevent an event from occurring under certain conditions.

### Error Handling
- Events that fail to instantiate are silently ignored during discovery
- Effects that return `None` from `_prepare_effect_*` methods are skipped
- The system is designed to be resilient to individual event failures

This event system provides a flexible, extensible foundation for creating rich, dynamic gameplay experiences in Norimberga.

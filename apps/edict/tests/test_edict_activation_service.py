import pytest

from apps.city.tests.factories import SavegameFactory
from apps.edict.models import EdictLog
from apps.edict.services.edict_activation import EdictActivationService
from apps.edict.tests.factories import EdictFactory, EdictLogFactory


@pytest.mark.django_db
def test_process_activates_edict_successfully():
    savegame = SavegameFactory(coins=500, unrest=50, current_year=1200)
    edict = EdictFactory(cost_coins=100, effect_unrest=-10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True
    assert "activated" in result.message.lower()


@pytest.mark.django_db
def test_process_deducts_coins_from_savegame():
    savegame = SavegameFactory(coins=500)
    edict = EdictFactory(cost_coins=100)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.coins == 400


@pytest.mark.django_db
def test_process_deducts_population_from_savegame():
    savegame = SavegameFactory(population=100)
    edict = EdictFactory(cost_population=50)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.population == 50


@pytest.mark.django_db
def test_process_applies_unrest_effect():
    savegame = SavegameFactory(unrest=50)
    edict = EdictFactory(effect_unrest=-10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 40


@pytest.mark.django_db
def test_process_applies_coins_effect():
    savegame = SavegameFactory(coins=500)
    edict = EdictFactory(effect_coins=100)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.coins == 600


@pytest.mark.django_db
def test_process_applies_population_effect():
    savegame = SavegameFactory(population=100)
    edict = EdictFactory(effect_population=50)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.population == 150


@pytest.mark.django_db
def test_process_clamps_unrest_to_zero_minimum():
    savegame = SavegameFactory(unrest=5)
    edict = EdictFactory(effect_unrest=-10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 0


@pytest.mark.django_db
def test_process_clamps_unrest_to_100_maximum():
    savegame = SavegameFactory(unrest=95)
    edict = EdictFactory(effect_unrest=10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 100


@pytest.mark.django_db
def test_process_prevents_negative_population():
    savegame = SavegameFactory(population=10)
    edict = EdictFactory(effect_population=-50)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_process_creates_edict_log():
    savegame = SavegameFactory(current_year=1200)
    edict = EdictFactory()
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    log = EdictLog.objects.filter(savegame=savegame, edict=edict).first()
    assert log is not None
    assert log.activated_at_year == 1200


@pytest.mark.django_db
def test_process_fails_when_edict_is_inactive():
    savegame = SavegameFactory()
    edict = EdictFactory(is_active=False)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is False
    assert "not currently available" in result.message


@pytest.mark.django_db
def test_process_fails_when_not_enough_coins():
    savegame = SavegameFactory(coins=50)
    edict = EdictFactory(cost_coins=100)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is False
    assert "not enough coins" in result.message.lower()


@pytest.mark.django_db
def test_process_fails_when_not_enough_population():
    savegame = SavegameFactory(population=25)
    edict = EdictFactory(cost_population=50)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is False
    assert "not enough population" in result.message.lower()


@pytest.mark.django_db
def test_process_fails_when_edict_on_cooldown():
    savegame = SavegameFactory(current_year=1200)
    edict = EdictFactory(cooldown_years=3)
    EdictLogFactory(savegame=savegame, edict=edict, activated_at_year=1199)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is False
    assert "cooldown" in result.message.lower()


@pytest.mark.django_db
def test_process_succeeds_when_cooldown_period_passed():
    savegame = SavegameFactory(current_year=1203)
    edict = EdictFactory(cooldown_years=3)
    EdictLogFactory(savegame=savegame, edict=edict, activated_at_year=1200)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True


@pytest.mark.django_db
def test_process_succeeds_when_no_cooldown_defined():
    savegame = SavegameFactory(current_year=1200)
    edict = EdictFactory(cooldown_years=None)
    EdictLogFactory(savegame=savegame, edict=edict, activated_at_year=1199)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True


@pytest.mark.django_db
def test_process_succeeds_when_edict_has_cooldown_but_never_activated():
    """Test that edict with cooldown can be activated for the first time (no previous log)."""
    savegame = SavegameFactory(current_year=1200)
    edict = EdictFactory(cooldown_years=3)
    # No EdictLog created - this is the first time activation
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True
    # Verify log was created
    log = EdictLog.objects.filter(savegame=savegame, edict=edict).first()
    assert log is not None
    assert log.activated_at_year == 1200


@pytest.mark.django_db
def test_process_does_not_modify_savegame_when_validation_fails():
    initial_coins = 50
    savegame = SavegameFactory(coins=initial_coins, unrest=50)
    edict = EdictFactory(cost_coins=100, effect_unrest=-10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.coins == initial_coins
    assert savegame.unrest == 50


@pytest.mark.django_db
def test_process_does_not_create_log_when_validation_fails():
    savegame = SavegameFactory(coins=50)
    edict = EdictFactory(cost_coins=100)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    log_count = EdictLog.objects.filter(savegame=savegame, edict=edict).count()
    assert log_count == 0


@pytest.mark.django_db
def test_process_fails_when_required_milestone_not_completed():
    from apps.milestone.tests.factories import MilestoneFactory

    savegame = SavegameFactory(coins=500)
    milestone = MilestoneFactory(name="Small Town")
    edict = EdictFactory(cost_coins=100, required_milestone=milestone)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is False
    assert "Small Town" in result.message
    assert "milestone" in result.message.lower()


@pytest.mark.django_db
def test_process_succeeds_when_required_milestone_completed():
    from apps.milestone.tests.factories import MilestoneFactory, MilestoneLogFactory

    savegame = SavegameFactory(coins=500)
    milestone = MilestoneFactory(name="Small Town")
    MilestoneLogFactory(savegame=savegame, milestone=milestone)
    edict = EdictFactory(cost_coins=100, required_milestone=milestone)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True


@pytest.mark.django_db
def test_process_succeeds_when_no_milestone_required():
    savegame = SavegameFactory(coins=500)
    edict = EdictFactory(cost_coins=100, required_milestone=None)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True


@pytest.mark.django_db
def test_process_does_not_modify_savegame_when_milestone_not_completed():
    from apps.milestone.tests.factories import MilestoneFactory

    initial_coins = 500
    savegame = SavegameFactory(coins=initial_coins, unrest=50)
    milestone = MilestoneFactory(name="Small Town")
    edict = EdictFactory(cost_coins=100, effect_unrest=-10, required_milestone=milestone)
    service = EdictActivationService(savegame=savegame, edict=edict)

    service.process()

    savegame.refresh_from_db()
    assert savegame.coins == initial_coins
    assert savegame.unrest == 50

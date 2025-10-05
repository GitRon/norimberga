from apps.city.models import Savegame
from apps.milestone.models import Milestone, MilestoneLog


def get_all_milestones_with_conditions() -> list[Milestone]:
    """
    Get all milestones with related parent and conditions prefetched.
    """
    return list(Milestone.objects.select_related("parent").prefetch_related("milestone_conditions").all())


def get_completed_milestone_ids(*, savegame: Savegame) -> set[int]:
    """
    Get set of milestone IDs that have been completed for a savegame.
    """
    return set(MilestoneLog.objects.filter(savegame=savegame).values_list("milestone_id", flat=True))


def get_available_milestones(*, savegame: Savegame) -> list[Milestone]:
    """
    Get milestones that are available to check for a savegame.
    A milestone is available if:
    - Its parent milestone is completed OR it has no parent
    - It has not been completed yet
    """
    completed_milestone_ids = get_completed_milestone_ids(savegame=savegame)

    # Get root milestones (no parent) that aren't completed
    available_milestones = list(Milestone.objects.filter(parent__isnull=True).exclude(id__in=completed_milestone_ids))

    # Get milestones whose parents are completed but aren't completed themselves
    if completed_milestone_ids:
        child_milestones = Milestone.objects.filter(parent_id__in=completed_milestone_ids).exclude(
            id__in=completed_milestone_ids
        )
        available_milestones.extend(child_milestones)

    return available_milestones


def get_root_milestones() -> list[Milestone]:
    """
    Get all root milestones (milestones without a parent).
    """
    return list(Milestone.objects.filter(parent__isnull=True))


def get_child_milestones(*, parent_id: int) -> list[Milestone]:
    """
    Get all child milestones for a given parent milestone.
    """
    return list(Milestone.objects.filter(parent_id=parent_id))

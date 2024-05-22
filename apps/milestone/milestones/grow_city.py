from apps.milestone.conditions.population import MinPopulationCondition
from apps.milestone.milestones.abstract import AbstractMilestone


class GrowCityMilestone(AbstractMilestone):
    conditions = (MinPopulationCondition(min_population=15),)

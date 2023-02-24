from django.db import transaction
from rest_framework.serializers import ValidationError

from core.models import Ship
from vesselreporting.models.report_models import (
    Voyage,
    VoyageLeg,
    VoyageLegProgress,
)


@transaction.atomic
def create_new_voyage(
    ship: Ship,
    voyage_num: int,
) -> Voyage:
    try:
        previous_voyage = Voyage.objects.filter(ship=ship).latest('-created_at')
    except Voyage.DoesNotExist:
        # CASE: No previous voyages
        voyage = Voyage.objects.create(ship=ship, voyage_num=voyage_num)
        return voyage

    # CASE: Previous voyage exists
    try:
        previous_voyage_leg = previous_voyage.voyageleg_set.latest('-created_at')
    except VoyageLeg.DoesNotExist:
        # CASE: Previous voyage is empty
        raise ValidationError("Previous voyage is empty!")

    if not previous_voyage_leg.legprogress.arrival_fwe:
        # CASE: Previous Voyage leg is incomplete
        raise ValidationError("Previous leg is not complete!")

    # CASE: Previous Voyage and Leg is complete
    voyage = Voyage.objects.create(ship=ship, voyage_num=voyage_num)
    return voyage


@transaction.atomic
def create_new_voyage_leg(
    voyage: Voyage,
    leg_num: int,
) -> VoyageLeg:

    try:
        last_leg = VoyageLeg.objects.filter(
            voyage=voyage,
        ).latest(
            '-created_at'
        ).select_related(
            'voyagelegprogress'
        )
    except VoyageLeg.DoesNotExist:
        # CASE: Voyage has no legs
        leg = VoyageLeg.objects.create(voyage=voyage, leg_num=leg_num)
        VoyageLegProgress.objects.create(voyage_leg=leg, )
        return leg

    if not last_leg.arrival_fwe:
        # CASE: Last leg is incomplete
        raise ValidationError("😤")

    # CASE: Last leg is complete
    leg = VoyageLeg.objects.create(voyage=voyage, leg_num=leg_num)
    VoyageLegProgress.objects.create(voyage_leg=leg, )
    return leg

from datetime import date, timedelta

from management.models import (
    ClaimApplication,
    Contract,
    DeliveryOrder,
    Estate,
    Fee,
    GreeningMaintenance,
    LostItem,
    Repair,
    SafetyInspection,
    Unit,
    User,
    Vote,
)


def get_staff_dashboard_context():
    today = date.today()
    first_day_of_month = today.replace(day=1)
    sixty_days_later = today + timedelta(days=60)

    estate_count = Estate.objects.count()
    owner_count = User.objects.filter(role='owner').count()
    pending_repairs = Repair.objects.filter(status='pending').count()
    unpaid_fees = Fee.objects.filter(status='unpaid').count()
    monthly_greening_count = GreeningMaintenance.objects.filter(
        work_date__gte=first_day_of_month,
        work_date__lte=today,
    ).count()

    expiring_contracts = list(
        Contract.objects.filter(
            expire_date__gte=today,
            expire_date__lte=sixty_days_later,
        ).order_by('expire_date')
    )
    expiring_contracts_count = len(expiring_contracts)
    expiring_contracts_total_amount = sum(c.amount for c in expiring_contracts)
    for c in expiring_contracts:
        c.days_until_expire = (c.expire_date - today).days
    expiring_contracts_preview = expiring_contracts[:5]

    high_risk_open = list(
        SafetyInspection.objects.filter(
            risk_level='high', status='open',
        ).order_by('rectification_deadline')
    )
    high_risk_open_count = len(high_risk_open)
    for h in high_risk_open:
        h.overdue_flag = h.is_overdue()
        h.days_left = h.days_until_deadline()
    high_risk_open_preview = high_risk_open[:10]

    medium_risk_open_count = SafetyInspection.objects.filter(
        risk_level='medium', status='open',
    ).count()
    low_risk_open_count = SafetyInspection.objects.filter(
        risk_level='low', status='open',
    ).count()

    pending_lost_items_count = LostItem.objects.filter(status='pending').count()
    pending_claims_count = ClaimApplication.objects.filter(status='pending').count()

    rectifying_orders = DeliveryOrder.objects.filter(
        status='rectifying',
    ).select_related(
        'unit', 'unit__floor', 'unit__floor__building', 'unit__floor__building__estate',
    )
    rectifying_delivery_count = rectifying_orders.count()
    rectifying_delivery_orders = rectifying_orders[:10]

    pending_delivery_count = DeliveryOrder.objects.filter(status='pending').count()
    inspecting_delivery_count = DeliveryOrder.objects.filter(status='inspecting').count()

    return {
        'estate_count': estate_count,
        'owner_count': owner_count,
        'pending_repairs': pending_repairs,
        'unpaid_fees': unpaid_fees,
        'monthly_greening_count': monthly_greening_count,
        'expiring_contracts_count': expiring_contracts_count,
        'expiring_contracts': expiring_contracts_preview,
        'expiring_contracts_total_amount': expiring_contracts_total_amount,
        'high_risk_open_count': high_risk_open_count,
        'high_risk_open': high_risk_open_preview,
        'medium_risk_open_count': medium_risk_open_count,
        'low_risk_open_count': low_risk_open_count,
        'pending_lost_items_count': pending_lost_items_count,
        'pending_claims_count': pending_claims_count,
        'rectifying_delivery_count': rectifying_delivery_count,
        'rectifying_delivery_orders': rectifying_delivery_orders,
        'pending_delivery_count': pending_delivery_count,
        'inspecting_delivery_count': inspecting_delivery_count,
    }


def get_owner_dashboard_context(user):
    my_units = Unit.objects.filter(owner=user)
    my_repairs = Repair.objects.filter(owner=user).order_by('-submit_time')[:5]
    unpaid_fees = Fee.objects.filter(unit__owner=user, status='unpaid')
    active_unvoted = Vote.objects.filter(status='active').exclude(
        voter_records__voter=user,
    )
    pending_lost_items = LostItem.objects.filter(status='pending').order_by('-found_date')[:5]
    my_delivery_orders = DeliveryOrder.objects.filter(
        unit__owner=user,
    ).order_by('-created_at')

    return {
        'my_units': my_units,
        'my_repairs': my_repairs,
        'unpaid_fees': unpaid_fees,
        'active_unvoted': active_unvoted,
        'pending_lost_items': pending_lost_items,
        'my_delivery_orders': my_delivery_orders,
    }

# Controller Layer (Views & Tasks)

## Overview

The **controller layer** consists of Django views and Celery tasks. These are entry points responsible for
**orchestration only**—coordinating flow between the UI and business logic layer, without containing business logic or
database queries themselves.

**Responsibilities:** Orchestrate calls to services/selectors/managers, handle HTTP concerns, validate input via forms,
check permissions, and return responses.

---

## What Does NOT Belong in Controllers

### Business Logic → Use Services

```python
# BAD example - Business logic in view
class InvoiceCreateView(CreateView):
    def form_valid(self, form):
        invoice = form.save(commit=False)
        invoice.total = sum(item.price * item.quantity for item in self.get_items())
        invoice.tax = invoice.total * Decimal("0.19")
        invoice.due_date = timezone.now().date() + timedelta(days=30)
        invoice.save()
        return redirect("invoice-list")


# GOOD example - Delegate to service, pass IDs and values only
class InvoiceCreateView(CreateView):
    def form_valid(self, form):
        InvoiceCreationService(
            client_id=form.cleaned_data["client"].id,
            items=form.cleaned_data["items"],
            created_by_id=self.request.user.id,
        ).process()
        return redirect("invoice-list")
```

### Direct Model Queries → Use Selectors

```python
# BAD example - Direct model access in view
class ProjectListView(ListView):
    def get_queryset(self):
        return (
            Project.objects.filter(is_active=True, team__members=self.request.user)
            .select_related("team")
            .order_by("-created_at")
        )


# GOOD example - Use selector (registered on model as `Model.selectors`)
class ProjectListView(ListView):
    def get_queryset(self):
        return Project.selectors.get_active_for_user(user_id=self.request.user.id)
```

### Data Manipulation → Use Services/Managers

```python
# BAD example - Data manipulation in view
class UserDeactivateView(View):
    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        user.is_active = False
        user.deactivated_at = timezone.now()
        user.deactivated_by = request.user
        user.save()
        AuditLog.objects.create(action="deactivate", target=user, actor=request.user)
        return redirect("user-list")


# GOOD example - Delegate to service
class UserDeactivateView(View):
    def post(self, request, pk):
        UserDeactivationService(user_id=pk, actor_id=request.user.id).process()
        return redirect("user-list")
```

---

## Celery Tasks

Tasks follow the same principles—orchestrate, don't implement.

```python
# BAD example - Logic and queries in task
@shared_task
def process_monthly_billing():
    clients = Client.objects.filter(billing_enabled=True)
    for client in clients:
        hours = (
                TimeEntry.objects.filter(
                    client=client, date__month=timezone.now().month
                ).aggregate(total=Sum("hours"))["total"]
                or 0
        )
        if hours > 0:
            Invoice.objects.create(
                client=client, hours=hours, amount=hours * client.hourly_rate
            )


# GOOD example - Delegate to service
@shared_task
def process_monthly_billing():
    MonthlyBillingService().process()
```

---

## Allowed Patterns

- **Selectors** for filtered querysets: `Project.selectors.get_active_for_user(user_id=...)`
- **Managers** for simple lookups: `get_object_or_404(Project, pk=self.kwargs["pk"])`
- **Services** for any operation with side effects
- **Form validation** before passing cleaned data to services

---

## Summary

| Allowed in Controllers | Not Allowed in Controllers      |
|------------------------|---------------------------------|
| Call services          | Implement business logic        |
| Call selectors         | Direct `Model.objects.filter()` |
| Call managers          | Direct `Model.objects.create()` |
| Form/input validation  | Complex data transformations    |
| Permission checks      | Multi-step workflows            |
| HTTP response handling | Calculations and aggregations   |

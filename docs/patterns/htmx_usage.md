# HTMX Usage

## Overview

Norimberga uses HTMX for frontend interactivity to avoid writing custom JavaScript wherever possible. HTMX allows us to handle dynamic UI updates through HTML attributes and server responses.

## Core Principles

### 1. Prefer HTMX Over Custom JavaScript

Always attempt to solve interactivity needs with HTMX first. Only write custom JavaScript when HTMX cannot handle the requirement.

**Good:**
```html
<button hx-post="/api/build/" hx-target="#building-list">
    Build
</button>
```

**Avoid:**
```html
<button onclick="buildBuilding()">Build</button>
<script>
function buildBuilding() {
    fetch('/api/build/', {method: 'POST'})
        .then(response => response.text())
        .then(html => document.getElementById('building-list').innerHTML = html);
}
</script>
```

### 2. Simple Django Views with Data

Django views should return HTML fragments or trigger events. Keep the response simple and let HTMX handle the DOM updates.

**Example:**
```python
def build_building(request):
    # Process building creation
    building = create_building(...)

    # Return HTML fragment
    return render(request, 'city/partials/building_item.html', {
        'building': building
    })
```

### 3. Avoid Out-of-Band (OOB) Swaps

While HTMX supports OOB swaps (`hx-swap-oob`), avoid using them when possible. They add complexity and make the code harder to follow.

**Instead of OOB, use:**
- Target the correct element directly with `hx-target`
- Trigger custom events and listen with `hx-trigger`
- Page reloads when multiple areas need updates

### 4. Use HTMX Events for Coordination

When you need to update multiple parts of the page, use HTMX's event system:

**Backend (Django view):**
```python
from django.http import HttpResponse

def update_coins(request):
    # Process update
    response = render(request, 'city/partials/coin_display.html', {...})
    response['HX-Trigger'] = 'coinsUpdated'
    return response
```

**Frontend (HTML):**
```html
<div id="coin-display">...</div>

<div id="building-stats"
     hx-get="/buildings/stats/"
     hx-trigger="coinsUpdated from:body">
    ...
</div>
```

### 5. Page Reloads Are OK

Don't be afraid to use full page reloads when it simplifies the code. They can be triggered from the backend using the `HX-Redirect` or `HX-Refresh` headers.

**Redirect to another page:**
```python
from django.http import HttpResponse

def complete_action(request):
    # Process action
    response = HttpResponse()
    response['HX-Redirect'] = '/dashboard/'
    return response
```

**Refresh current page:**
```python
def complete_action(request):
    # Process action
    response = HttpResponse()
    response['HX-Refresh'] = 'true'
    return response
```

## Common Patterns

### Form Submission

```html
<form hx-post="/buildings/create/" hx-target="#building-list" hx-swap="beforeend">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Create Building</button>
</form>
```

### Delete with Confirmation

```html
<button hx-delete="/buildings/{{ building.id }}/delete/"
        hx-confirm="Are you sure you want to delete this building?"
        hx-target="closest .building-item"
        hx-swap="outerHTML swap:1s">
    Delete
</button>
```

### Loading States

```html
<button hx-get="/data/"
        hx-target="#content"
        hx-indicator="#spinner">
    Load Data
</button>

<div id="spinner" class="htmx-indicator">
    Loading...
</div>
```

### Polling for Updates

```html
<div hx-get="/status/"
     hx-trigger="every 5s"
     hx-target="this"
     hx-swap="innerHTML">
    Current status: ...
</div>
```

## Response Headers Reference

HTMX recognizes several response headers from the server:

- `HX-Redirect`: Redirect to a new URL (full page load)
- `HX-Refresh`: Refresh the current page
- `HX-Trigger`: Trigger client-side events (can be multiple, comma-separated)
- `HX-Retarget`: Change the target element
- `HX-Reswap`: Change the swap strategy

## When to Use Custom JavaScript

Use custom JavaScript only when HTMX cannot handle the requirement:

- Complex client-side calculations
- Canvas/WebGL rendering
- Third-party library integration that requires imperative code
- Performance-critical animations

When you do write JavaScript, keep it minimal and well-documented.

## Testing HTMX Interactions

Test HTMX interactions through Django's test client:

```python
def test_building_creation_htmx(client, savegame):
    response = client.post(
        '/buildings/create/',
        {'building_type': 1, 'tile': 1},
        headers={'HX-Request': 'true'}
    )

    assert response.status_code == 200
    assert 'HX-Trigger' in response.headers
```

## Resources

- [HTMX Documentation](https://htmx.org/docs/)
- [HTMX Examples](https://htmx.org/examples/)

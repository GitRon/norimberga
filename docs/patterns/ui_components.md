# UI Components with DaisyUI

## Overview

Norimberga uses [DaisyUI](https://daisyui.com/) as a component library for Tailwind CSS. DaisyUI provides pre-built, customizable UI components that maintain consistency across the application while reducing custom CSS code.

## Core Principles

### 1. Use DaisyUI Components First

Always use DaisyUI components instead of building custom UI elements. This ensures consistency and reduces maintenance overhead.

**Good:**
```html
<button class="btn btn-primary">Click me</button>
```

**Avoid:**
```html
<button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Click me</button>
```

### 2. Component Composition

DaisyUI components can be composed with utility classes for specific adjustments:

```html
<button class="btn btn-success gap-2">
    <svg>...</svg>
    <span>Save Changes</span>
</button>
```

### 3. Semantic Naming

Use semantic class names that convey meaning:
- `btn-primary` for main actions
- `btn-success` for positive actions (create, save, confirm)
- `btn-error` for destructive actions (delete, remove)
- `alert-warning` for warnings
- `badge-info` for informational badges

## Component Reference

### Buttons

DaisyUI provides a comprehensive button system with multiple variants.

#### Button Variants

```html
<!-- Primary action -->
<button class="btn btn-primary">Primary</button>

<!-- Success action (create, save) -->
<button class="btn btn-success">Create</button>

<!-- Error/Destructive action (delete, remove) -->
<button class="btn btn-error">Delete</button>

<!-- Ghost (minimal styling) -->
<button class="btn btn-ghost">Cancel</button>

<!-- Disabled state -->
<button class="btn btn-disabled" disabled>Disabled</button>
```

#### Button Sizes

```html
<button class="btn btn-sm">Small</button>
<button class="btn">Normal</button>
<button class="btn btn-lg">Large</button>
```

#### Button Shapes

```html
<!-- Circle (for icons) -->
<button class="btn btn-circle">×</button>

<!-- With icon and text -->
<button class="btn btn-success gap-2">
    <svg class="w-4 h-4">...</svg>
    <span>Finish Round</span>
</button>
```

#### Full Width

```html
<button class="btn btn-primary w-full">Full Width Button</button>
```

**Example from codebase:** `apps/core/templates/partials/_navbar_values.html:44`

### Cards

Cards are containers for grouped content with consistent styling.

#### Basic Card

```html
<div class="card bg-base-100 shadow-md">
    <div class="card-body">
        <h2 class="card-title">Card Title</h2>
        <p>Card content goes here</p>
    </div>
</div>
```

#### Card with Actions

```html
<div class="card bg-base-100 shadow-md">
    <div class="card-body">
        <h2 class="card-title">Card Title</h2>
        <p>Card content</p>
        <div class="card-actions justify-end">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
</div>
```

#### Card with Custom Borders

You can combine DaisyUI cards with Tailwind utilities:

```html
<div class="card bg-base-100 shadow-md border-l-4 border-green-500">
    <div class="card-body">
        <h3>Milestone Card</h3>
        <p>Custom left border for status indication</p>
    </div>
</div>
```

**Example from codebase:** `apps/milestone/templates/milestone/partials/_milestone_card.html:4`

### Badges

Badges are small status indicators or labels.

```html
<!-- Success badge -->
<span class="badge badge-success">Active</span>

<!-- Info badge -->
<span class="badge badge-info">Level 1</span>

<!-- Ghost badge (neutral) -->
<span class="badge badge-ghost">Locked</span>

<!-- Small badge -->
<span class="badge badge-info badge-sm">Lvl 2</span>
```

**Example from codebase:** `apps/milestone/templates/milestone/partials/_milestone_card.html:34`

### Alerts

Alerts display important messages to users.

```html
<!-- Success alert -->
<div class="alert alert-success">
    <span>Operation completed successfully!</span>
</div>

<!-- Error alert -->
<div class="alert alert-error">
    <span>An error occurred.</span>
</div>

<!-- Warning alert -->
<div class="alert alert-warning">
    <div>
        <p class="font-bold">Warning Title</p>
        <p>Warning message details</p>
    </div>
</div>

<!-- Info alert -->
<div class="alert alert-info">
    <span>Here's some information.</span>
</div>
```

**Example from codebase:** `apps/city/templates/city/partials/city/_messages.html:3`

### Forms

Form elements have consistent styling across the application.

#### Input Fields

```html
<!-- Text input -->
<input type="text" class="input input-bordered w-full" placeholder="Enter text" />

<!-- Input with error state -->
<input type="text" class="input input-bordered input-error w-full" />
```

#### Select Dropdowns

```html
<select class="select select-bordered w-full">
    <option>Option 1</option>
    <option>Option 2</option>
    <option>Option 3</option>
</select>

<!-- Select with error state -->
<select class="select select-bordered select-error w-full">
    <option>Option 1</option>
</select>
```

**Example from codebase:** `apps/core/templates/tailwind/layout/select.html:3`

#### Textarea

```html
<textarea class="textarea textarea-bordered w-full" placeholder="Enter text"></textarea>
```

#### Checkbox

```html
<input type="checkbox" class="checkbox" />
<input type="checkbox" class="checkbox checkbox-primary" />
```

### Navbar

Navigation bar with consistent layout and dropdown menus.

```html
<nav class="navbar bg-base-100">
    <div class="navbar-start">
        <a href="/" class="btn btn-ghost text-xl">Logo</a>
    </div>

    <div class="navbar-center">
        <ul class="menu menu-horizontal px-1">
            <li><a>Link 1</a></li>
            <li><a>Link 2</a></li>
        </ul>
    </div>

    <div class="navbar-end">
        <div class="dropdown dropdown-end">
            <div tabindex="0" role="button" class="btn btn-ghost">
                Menu
            </div>
            <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-50 w-52 p-2 shadow">
                <li><a>Item 1</a></li>
                <li><a>Item 2</a></li>
            </ul>
        </div>
    </div>
</nav>
```

**Example from codebase:** `apps/core/templates/partials/_navbar.html:2`

### Modal

Modals for overlay dialogs and forms.

```html
<!-- Modal trigger -->
<button onclick="document.getElementById('my-modal').classList.add('modal-open')">
    Open Modal
</button>

<!-- Modal -->
<div id="my-modal" class="modal">
    <div class="modal-box">
        <button onclick="document.getElementById('my-modal').classList.remove('modal-open')"
                class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
        <h3 class="font-bold text-lg">Modal Title</h3>
        <p class="py-4">Modal content goes here</p>
    </div>
</div>
```

**Key points:**
- Add/remove `modal-open` class to show/hide modal
- Click outside modal-box to close (built-in behavior)
- Use `btn-circle` for close button

**Example from codebase:** `apps/city/templates/city/landing_page.html:15`

### Tables

Tables with hover effects and consistent styling.

```html
<div class="overflow-x-auto">
    <table class="table table-sm table-hover">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
                <th class="text-right">Column 3</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
                <td class="text-right">Data 3</td>
            </tr>
        </tbody>
        <tfoot>
            <tr>
                <th colspan="2">Total</th>
                <th class="text-right">100</th>
            </tr>
        </tfoot>
    </table>
</div>
```

**Table variants:**
- `table-sm` - Compact table
- `table-hover` - Hover effects on rows
- `table-zebra` - Alternating row colors

**Example from codebase:** `apps/city/templates/city/balance.html:27`

### Dropdown Menu

Dropdown menus for navigation or actions.

```html
<div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="btn btn-ghost">
        Click me
    </div>
    <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-50 w-52 p-2 shadow">
        <li><a>Item 1</a></li>
        <li><a>Item 2</a></li>
        <li>
            <button onclick="doSomething()">Action</button>
        </li>
    </ul>
</div>
```

**Dropdown positions:**
- `dropdown-end` - Align to right
- `dropdown-start` - Align to left
- `dropdown-top` - Open upward
- `dropdown-bottom` - Open downward

**Example from codebase:** `apps/core/templates/partials/_navbar.html:33`

## Common Patterns

### Empty States

```html
<div class="card bg-base-100 shadow-md">
    <div class="card-body text-center">
        <p class="text-gray-600">No items found.</p>
    </div>
</div>
```

### List with Actions

```html
<div class="card bg-base-100 shadow-md overflow-hidden">
    <ul class="divide-y divide-gray-200">
        <li class="p-4 hover:bg-gray-50">
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <h3 class="text-lg font-semibold">Item Name</h3>
                    <p class="text-sm text-gray-600">Item description</p>
                </div>
                <div class="flex space-x-2">
                    <button class="btn btn-primary btn-sm">Edit</button>
                    <button class="btn btn-error btn-sm">Delete</button>
                </div>
            </div>
        </li>
    </ul>
</div>
```

**Example from codebase:** `apps/savegame/templates/savegame/savegame_list.html:14`

### Form Layout

```html
<div class="card bg-base-100 shadow-md">
    <div class="card-body">
        <form method="post">
            {% csrf_token %}
            <div class="form-control">
                <label class="label">
                    <span class="label-text">Field Name</span>
                </label>
                <input type="text" class="input input-bordered w-full" />
            </div>

            <div class="form-control mt-4">
                <label class="label">
                    <span class="label-text">Another Field</span>
                </label>
                <select class="select select-bordered w-full">
                    <option>Option 1</option>
                    <option>Option 2</option>
                </select>
            </div>

            <div class="form-control mt-6">
                <button type="submit" class="btn btn-success w-full">Submit</button>
            </div>
        </form>
    </div>
</div>
```

## Theme Configuration

The project uses DaisyUI's light theme by default. This is configured in `tailwind.config.js`:

```javascript
daisyui: {
    themes: ["light"], // Can add more themes like "dark", "cupcake", etc.
    base: true,
    styled: true,
    utils: true,
}
```

### Color System

DaisyUI uses semantic color names:
- `base-100` - Main background color
- `base-200` - Slightly darker background
- `base-300` - Even darker background
- `primary` - Primary brand color
- `secondary` - Secondary brand color
- `success` - Success/positive actions (green)
- `error` - Error/destructive actions (red)
- `warning` - Warning state (yellow/orange)
- `info` - Informational state (blue)

### Using Theme Colors

```html
<!-- Background colors -->
<div class="bg-base-100">Base background</div>
<div class="bg-primary">Primary color background</div>

<!-- Text colors -->
<p class="text-primary">Primary color text</p>
<p class="text-error">Error color text</p>
```

## Custom Styling

### When to Use Custom Classes

Use custom Tailwind utility classes when:
1. DaisyUI doesn't provide the specific styling needed
2. Layout-specific adjustments (grid, flex, spacing)
3. Project-specific elements like the tile map

**Example:**
```html
<!-- DaisyUI card with custom border for status -->
<div class="card bg-base-100 shadow-md border-l-4 border-green-500">
    <div class="card-body">
        <h3>Custom styled card</h3>
    </div>
</div>
```

### Combining with HTMX

DaisyUI components work seamlessly with HTMX:

```html
<button class="btn btn-primary"
        hx-post="/api/action/"
        hx-target="#result"
        hx-swap="innerHTML">
    Submit Action
</button>
```

## Component Guidelines

### 1. Consistency

Use the same component variant for the same purpose throughout the app:
- Create/Add actions → `btn-success`
- Load/View actions → `btn-primary`
- Delete/Remove actions → `btn-error`

### 2. Accessibility

DaisyUI components include built-in accessibility features:
- Proper ARIA attributes
- Keyboard navigation support
- Screen reader compatibility

Always maintain these features when customizing components.

### 3. Responsive Design

DaisyUI components are responsive by default. Add responsive utilities when needed:

```html
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="card bg-base-100 shadow-md">...</div>
    <div class="card bg-base-100 shadow-md">...</div>
</div>
```

## Resources

- [DaisyUI Documentation](https://daisyui.com/docs/)
- [DaisyUI Components](https://daisyui.com/components/)
- [DaisyUI Themes](https://daisyui.com/docs/themes/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)

## Migration from Custom Styles

When refactoring custom styles to DaisyUI:

1. **Identify the component type** (button, card, badge, etc.)
2. **Find the equivalent DaisyUI component** in the documentation
3. **Replace custom classes** with DaisyUI classes
4. **Test functionality** to ensure HTMX interactions still work
5. **Verify visual appearance** matches the design intent

**Example migration:**
```html
<!-- Before -->
<button class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
    Create
</button>

<!-- After -->
<button class="btn btn-success">
    Create
</button>
```

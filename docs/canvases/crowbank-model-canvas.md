# 📦 Crowbank Model Design – Summary Canvas

This canvas summarises recent architectural decisions around data models in the Crowbank intranet system.

---

## ✅ Naming Conventions

### Python (PEP8)
- Classes: `PascalCase` → `Customer`, `Contact`, `Vet`
- Variables & functions: `snake_case` → `customer_id`, `get_customer()`
- Constants: `UPPERCASE` → `MAX_DOGS`
- Files/modules: `lowercase` → `contact.py`, `vet.py`

### Database
- Tables: plural, `snake_case` → `customers`, `contacts`
- Columns: `snake_case` → `first_name`, `default_vet_id`
- Booleans: use `is_`, `has_` → `is_approved`, `has_deposit`
- Foreign keys: `xxx_id` → `customer_id`, `vet_id`
- Primary key: `id` (autoincremented integer)
- Enums: use string values, optionally typed with Python `Enum`

---

## 🧩 Address Handling

- Shared fields (`street`, `town`, `postcode`) exist on `Customer`, `Vet`, and eventually `Employee`.
- These are logically grouped as an **Address**, but implemented using **composite Python class**, not a separate DB table.
- Allows shared methods like `navigation_url()` without needing a join.

---

## 👥 Customer & Contact Relationship

### Key insight:
- A `Customer` is a **household**, not an individual.
- One `Contact` (e.g. Jane Smith) may be:
  - Primary for household A
  - Emergency contact for household B

### Implementation:
- Use a **many-to-many association table** with an enum `role` field:
  - Values: `primary`, `secondary`, `emergency`

```python
class ContactRole(str, enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    EMERGENCY = "emergency"
```

- `CustomerContact` association table includes:
  - `customer_id` (FK)
  - `contact_id` (FK)
  - `role` (enum)

---

## 🐾 Vet Model

- Separate `vets` table with:
  - `practice_name`, `street`, `town`, `postcode`, `phone`, `email`, `website`
- Each `Customer` can have a `default_vet_id` (FK → `vets.id`)
- Each `Pet` can override vet with its own `vet_id`

---

## 🔁 Legacy `no` Field Retention

### Customer:
- New `id` is the primary key
- Legacy `cust_no` is preserved in `legacy_cust_no` column

### Booking:
- Same strategy as above:
  - New `id` is primary key
  - `legacy_booking_no` used for:
    - Search
    - Display
    - External communications

```python
@property
def display_ref(self):
    return f"#{self.legacy_booking_no}" if self.legacy_booking_no else f"N{self.id}"
```

- Route aliases and searches support both ID types during transition

---

## 🎯 Strategy Summary

- Modern, normalized structure with Pythonic interfaces
- Preserves compatibility and traceability with legacy system
- Allows safe migration, clean UI, and future-proof extensibility
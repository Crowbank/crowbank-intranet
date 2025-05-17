from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from tqdm import tqdm

from .config import settings
from .lookup import lookup

CHUNK = 2_000

# ---------------------------------------------------------------------------
# Describe import order & FK translation rules
# ---------------------------------------------------------------------------
# Each item: (source_view_name, destination_table_name, {
#              'dest_fk_col': 'lookup_key_in_lookup_dict'
#           }, primary_key_column_name)
# Only declare FK columns that need translation; simple columns stay as-is.
IMPORT_PLAN = [
    ("v_vets", "vets", {}, "legacy_vet_no"),
    ("v_species", "species", {}, "legacy_spec_no"),
    ("v_breed_categories", "breed_categories", {"species_id": "species"}, "legacy_breedcat_no"),
    ("v_breeds", "breeds", {"species_id": "species", "category_id": "breed_categories"}, "legacy_breed_no"),
    ("v_customers", "customers", {"default_vet_id": "vets"}, "legacy_cust_no"),
    ("v_contacts", "contacts", {}, "legacy_contact_no"),
    ("v_customer_contacts", "customer_contacts",
        {"customer_id": "customers", "contact_id": "contacts"}, "legacy_assoc_no"),
    # add more tuples …
]

# ---------------------------------------------------------------------------
_engine_src = sa.create_engine(settings.mssql_url, fast_executemany=True)
_engine_dst = sa.create_engine(settings.pg_url)
_meta_dst   = sa.MetaData()


def stream_rows(view: str, pk_col: str):
    sql = sa.text(f"SELECT * FROM {view} ORDER BY {pk_col}")
    with _engine_src.connect() as conn:
        result = conn.execute(sql)
        return result.mappings().all()


def load_table(dest_name: str):
    return sa.Table(dest_name, _meta_dst, autoload_with=_engine_dst)


def translate_fk(record: dict, fk_map: dict[str, str]):
    """Replace legacy FK ints with new ones via lookup dicts."""
    for col, lookup_key in fk_map.items():
        legacy_val = record.pop(f"legacy_{col}")
        if legacy_val in (None, 0):
            record[col] = None
        else:
            try:
                record[col] = lookup[lookup_key][legacy_val]
            except KeyError as exc:
                raise KeyError(
                    f"No lookup value for {lookup_key}[{legacy_val}] while populating {col}"
                ) from exc


def import_table(view: str, dest_name: str, fk_map: dict[str, str], pk_col: str):
    dest_tbl = load_table(dest_name)
    pending: list[dict] = []
    legacy_ids: list[int] = []

    # Build map of already-imported legacy ids so reruns are safe / idempotent.
    with _engine_dst.connect() as conn:
        existing_rows = conn.execute(sa.select(dest_tbl.c[pk_col], dest_tbl.c.id)).all()
    existing_map = {row[0]: row[1] for row in existing_rows}
    lookup[dest_name].update(existing_map)

    for row in tqdm(stream_rows(view, pk_col), desc=f"{view}->{dest_name}"):
        rec = dict(row)
        legacy_id = rec.pop(pk_col)
        if legacy_id in existing_map:
            # already present, nothing to insert
            continue

        if fk_map:
            translate_fk(rec, fk_map)
        pending.append(rec)
        legacy_ids.append(legacy_id)
        if len(pending) >= CHUNK:
            flush(dest_name, dest_tbl, pending, legacy_ids)
            pending.clear(); legacy_ids.clear()

    if pending:
        flush(dest_name, dest_tbl, pending, legacy_ids)


def flush(dest_name: str, dest_tbl, rows: list[dict], legacy_ids: list[int]):
    with _engine_dst.begin() as conn:
        result = conn.execute(insert(dest_tbl).returning(dest_tbl.c.id), rows)
    new_ids = result.scalars().all()
    lookup[dest_name].update(dict(zip(legacy_ids, new_ids)))


# ---------------------------------------------------------------------------
def main():  # pragma: no cover
    for view, dest_tbl, fk_map, pk_col in IMPORT_PLAN:
        import_table(view, dest_tbl, fk_map, pk_col)


if __name__ == "__main__":
    main() 
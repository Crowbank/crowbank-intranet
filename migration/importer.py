from __future__ import annotations

import argparse, sys
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
    ("v_customer_contacts", "customer_contacts", {}, None),  # Handle FKs in custom code
]

# ---------------------------------------------------------------------------
_engine_src = sa.create_engine(settings.mssql_url, fast_executemany=True)
_engine_dst = sa.create_engine(settings.pg_url)
_meta_dst   = sa.MetaData()


def stream_rows(view: str, pk_col: str | None):
    sql = sa.text(f"SELECT * FROM {view} " + (f"ORDER BY {pk_col}" if pk_col else ""))
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


def import_table(view: str, dest_name: str, fk_map: dict[str, str], pk_col: str, *, force: bool = False):
    dest_tbl = load_table(dest_name)

    if force:
        # Truncate destination table cascade
        with _engine_dst.begin() as conn:
            conn.execute(sa.text(f"TRUNCATE TABLE {dest_name} CASCADE"))
        # Clear any lookup data we might have cached
        lookup[dest_name].clear()

    pending: list[dict] = []
    legacy_ids: list[int] = []

    # Build map of already-imported legacy ids so reruns are safe / idempotent.
    if pk_col and pk_col in dest_tbl.c:
        with _engine_dst.connect() as conn:
            existing_rows = conn.execute(sa.select(dest_tbl.c[pk_col], dest_tbl.c.id)).all()
        existing_map = {row[0]: row[1] for row in existing_rows}
        lookup[dest_name].update(existing_map)
    else:
        existing_map = {}

    for row in tqdm(stream_rows(view, pk_col), desc=f"{view}->{dest_name}"):
        rec = dict(row)
        if pk_col:
            legacy_id = rec[pk_col]
            if legacy_id is None:
                continue
            if legacy_id in existing_map:
                continue

        if fk_map:
            translate_fk(rec, fk_map)
            
        # Special case for customer_contacts to map legacy_contact_no to contact_id
        if dest_name == "customer_contacts" and "legacy_contact_no" in rec and "contact_id" in dest_tbl.c:
            legacy_contact_no = rec.pop("legacy_contact_no", None)
            if legacy_contact_no is not None:
                try:
                    rec["contact_id"] = lookup["contacts"][legacy_contact_no]
                except KeyError:
                    # Skip if contact not imported yet
                    continue
                    
        # Special case for customer_contacts to map legacy_customer_id to customer_id
        if dest_name == "customer_contacts" and "legacy_customer_id" in rec and "customer_id" in dest_tbl.c:
            legacy_customer_id = rec.pop("legacy_customer_id", None)
            if legacy_customer_id is not None:
                try:
                    rec["customer_id"] = lookup["customers"][legacy_customer_id]
                except KeyError:
                    # Skip if customer not imported yet
                    continue
                    
        pending.append(rec)
        if pk_col:
            legacy_ids.append(legacy_id)
        if len(pending) >= CHUNK:
            new_ids_batch = flush(dest_name, dest_tbl, pending, legacy_ids if pk_col else None)
            pending.clear(); legacy_ids.clear()

    if pending:
        new_ids_batch = flush(dest_name, dest_tbl, pending, legacy_ids if pk_col else None)


def flush(dest_name: str, dest_tbl, rows: list[dict], legacy_ids: list[int] | None):
    """Insert batch and return list of newly generated destination IDs (if any)."""
    with _engine_dst.begin() as conn:
        if 'id' in dest_tbl.c:
            # For tables with auto-increment IDs
            result = conn.execute(insert(dest_tbl).returning(dest_tbl.c.id), rows)
            new_ids = result.scalars().all()
            if legacy_ids is not None:
                lookup[dest_name].update(dict(zip(legacy_ids, new_ids)))
            return new_ids
        else:
            # For tables without auto-increment IDs (like association tables)
            # Use ON CONFLICT DO NOTHING to skip duplicates
            conn.execute(
                insert(dest_tbl)
                .on_conflict_do_nothing()
                .values(rows)
            )
            return []


# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None):  # pragma: no cover
    parser = argparse.ArgumentParser(description="Import legacy data into PostgreSQL")
    parser.add_argument(
        "--tables",
        nargs="*",
        help="Destination table names to import (default: all)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Truncate target table(s) (CASCADE) before importing",
    )
    args = parser.parse_args(argv)

    selected_tables = set(t.lower() for t in args.tables) if args.tables else None
    
    # Preload customer and contact mappings for FK resolution
    if selected_tables and 'customer_contacts' in selected_tables:
        with _engine_dst.connect() as conn:
            # Load customer mappings
            customer_rows = conn.execute(sa.text("SELECT legacy_cust_no, id FROM customers WHERE legacy_cust_no IS NOT NULL")).all()
            lookup['customers'] = {row[0]: row[1] for row in customer_rows}
            print(f"Preloaded {len(lookup['customers'])} customer mappings")
            
            # Load contact mappings
            contact_rows = conn.execute(sa.text("SELECT legacy_contact_no, id FROM contacts WHERE legacy_contact_no IS NOT NULL")).all()
            lookup['contacts'] = {row[0]: row[1] for row in contact_rows}
            print(f"Preloaded {len(lookup['contacts'])} contact mappings")

    for view, dest_tbl, fk_map, pk_col in IMPORT_PLAN:
        if selected_tables is not None and dest_tbl.lower() not in selected_tables:
            continue
        import_table(view, dest_tbl, fk_map, pk_col, force=args.force)


if __name__ == "__main__":
    main(sys.argv[1:])


# ---------------------------------------------------------------------------
def create_customer_contacts(contacts_batch: list[dict], new_ids: list[int]):
    """Insert rows into customer_contacts based on contacts batch."""
    # This function is no longer needed as v_customer_contacts will handle
    # the associations directly with the legacy_contact_no
    pass 
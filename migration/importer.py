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
    ("v_run_types", "run_types", {}, "run_type_legacy_no"),  # Run types - handle species_id separately
    ("v_boarding_runs", "boarding_runs", {}, "legacy_run_no"),  # Handle run_type_id FK separately
    ("v_services", "services", {}, "legacy_service_id"),  # Service catalog import
    ("v_pets", "pets", {"owner_id": "customers", "species_id": "species", "breed_id": "breeds", "vet_id": "vets"}, "legacy_pet_no"),  # Pets with FK mappings
    ("v_bookings", "bookings", {"customer_id": "customers"}, "legacy_bk_no"),  # Bookings with customer FK
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
                # Handle missing foreign keys gracefully for certain cases
                if col == 'owner_id' and lookup_key == 'customers':
                    print(f"⚠️  Orphaned pet: missing customer {legacy_val}, setting owner_id to NULL")
                    record[col] = None
                elif col == 'vet_id' and lookup_key == 'vets':
                    print(f"⚠️  Pet with missing vet {legacy_val}, setting vet_id to NULL")
                    record[col] = None
                elif col == 'species_id' and lookup_key == 'species':
                    print(f"⚠️  Pet with missing species {legacy_val}, setting species_id to NULL")
                    record[col] = None
                elif col == 'breed_id' and lookup_key == 'breeds':
                    print(f"⚠️  Pet with missing breed {legacy_val}, setting breed_id to NULL")
                    record[col] = None
                else:
                    raise KeyError(
                        f"No lookup value for {lookup_key}[{legacy_val}] while populating {col}"
                    ) from exc


def translate_run_type(record: dict):
    """Special handling for run_type records to map species_id FK correctly."""
    if 'species_id' in record and 'species' in lookup:
        legacy_species_id = record['species_id']
        if legacy_species_id is not None:
            # Map legacy species_id to new species id via lookup table
            record['species_id'] = lookup['species'].get(legacy_species_id, None)
        else:
            record['species_id'] = None


def translate_pet(record: dict):
    """Special handling for pet records to fix null values."""
    # Fix null neutered values (required field)
    if 'neutered' in record and record['neutered'] is None:
        record['neutered'] = False  # Default to False for null values
        
    # Fix null deceased values (required field) 
    if 'deceased' in record and record['deceased'] is None:
        record['deceased'] = False  # Default to False for null values
        
    # Fix null friends_allowed values (required field)
    if 'friends_allowed' in record and record['friends_allowed'] is None:
        record['friends_allowed'] = False  # Default to False for null values
        
    # Fix null daycare_approved values (required field)
    if 'daycare_approved' in record and record['daycare_approved'] is None:
        record['daycare_approved'] = False  # Default to False for null values


def translate_booking(record: dict):
    """Special handling for booking records to convert is_daycare 0/1 to boolean and fix timestamps."""
    if 'is_daycare' in record:
        # Convert 0/1 to boolean
        record['is_daycare'] = bool(record['is_daycare']) if record['is_daycare'] is not None else False
    
    # Map legacy status values to valid enum values (uppercase)
    if 'status' in record and record['status'] is not None:
        status_mapping = {
            'checked_in': 'CHECKED_IN',
            'checked_out': 'CHECKED_OUT', 
            'cancelled': 'CANCELLED',
            'confirmed': 'CONFIRMED',
            'pending': 'PENDING',
            'no_show': 'NO_SHOW',
            'standby': 'STANDBY',
            # Add other legacy mappings as needed
        }
        legacy_status = record['status'].lower()
        if legacy_status in status_mapping:
            record['status'] = status_mapping[legacy_status]
        else:
            print(f"⚠️  Unknown booking status '{record['status']}', mapping to 'PENDING'")
            record['status'] = 'PENDING'
    
    # Convert time-only values to proper timestamps for check-in/check-out
    from datetime import datetime, time, date
    
    # Fix checked_in_at: combine with arrival_date if it's a time object
    if 'checked_in_at' in record and record['checked_in_at'] is not None:
        if isinstance(record['checked_in_at'], time):
            # Combine time with arrival_date to create datetime
            arrival_date = record.get('arrival_date')
            if isinstance(arrival_date, date):
                record['checked_in_at'] = datetime.combine(arrival_date, record['checked_in_at'])
            else:
                # If no valid arrival_date, set to None
                record['checked_in_at'] = None
    
    # Fix checked_out_at: combine with departure_date if it's a time object
    if 'checked_out_at' in record and record['checked_out_at'] is not None:
        if isinstance(record['checked_out_at'], time):
            # Combine time with departure_date to create datetime
            departure_date = record.get('departure_date')
            if isinstance(departure_date, date):
                record['checked_out_at'] = datetime.combine(departure_date, record['checked_out_at'])
            else:
                # If no valid departure_date, set to None
                record['checked_out_at'] = None


def translate_boarding_run(record: dict):
    """Special handling for boarding run records to map legacy_runtype_no to run_type_id FK."""
    if 'legacy_runtype_no' in record:
        legacy_runtype = record.pop('legacy_runtype_no', None)
        if legacy_runtype is not None and 'run_types' in lookup:
            # Map legacy runtype number to run_type_id via lookup table
            record['run_type_id'] = lookup['run_types'].get(legacy_runtype, None)
        else:
            record['run_type_id'] = None


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
        
        # Special handling for run types
        if dest_name == "run_types":
            translate_run_type(rec)
        
        # Special handling for boarding runs
        if dest_name == "boarding_runs":
            translate_boarding_run(rec)
        
        # Special handling for pets
        if dest_name == "pets":
            translate_pet(rec)
        
        # Special handling for bookings
        if dest_name == "bookings":
            translate_booking(rec)
            
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
                    
        # Special case for boarding_runs to assign run_type_id
        if dest_name == "boarding_runs" and "legacy_runtype_no" in rec:
            legacy_runtype_no = rec.pop("legacy_runtype_no", None)
            # Since legacy runs have runtype_no = 0, assign default Standard Dog Run (id=1)
            rec["run_type_id"] = 1  # Default to DOG_STANDARD
            # Add is_active field if not present
            if "is_active" not in rec:
                rec["is_active"] = True
            
            # Fix codes that are too long (max 10 chars)
            if "code" in rec and len(rec["code"]) > 10:
                code_mapping = {
                    "AtHome (Cat)": "AtHomeCat"
                }
                original_code = rec["code"]
                if original_code in code_mapping:
                    rec["code"] = code_mapping[original_code]
                    print(f"Mapped long code '{original_code}' -> '{rec['code']}'")
                else:
                    # Fallback: truncate to 10 chars
                    rec["code"] = rec["code"][:10]
                    print(f"Truncated long code '{original_code}' -> '{rec['code']}')")
                    
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
    
    # Preload run_types mappings for boarding_runs FK resolution
    if selected_tables is None or 'boarding_runs' in selected_tables:
        with _engine_dst.connect() as conn:
            # Load run_types mappings (run_type_legacy_no -> id)
            try:
                run_type_rows = conn.execute(sa.text("SELECT run_type_legacy_no, id FROM run_types WHERE run_type_legacy_no IS NOT NULL")).all()
                lookup['run_types'] = {row[0]: row[1] for row in run_type_rows}
                print(f"Preloaded {len(lookup['run_types'])} run_type mappings")
            except Exception as e:
                # If run_types table is empty or doesn't exist yet, we'll populate it first
                print(f"Run types not yet loaded: {e}")
                lookup['run_types'] = {}
    
    # Preload FK mappings for pets migration
    if selected_tables is None or 'pets' in selected_tables or 'bookings' in selected_tables:
        with _engine_dst.connect() as conn:
            # Load customers mapping if not already loaded
            if 'customers' not in lookup or not lookup['customers']:
                customer_rows = conn.execute(sa.text("SELECT legacy_cust_no, id FROM customers WHERE legacy_cust_no IS NOT NULL")).all()
                lookup['customers'] = {row[0]: row[1] for row in customer_rows}
                print(f"Preloaded {len(lookup['customers'])} customer mappings for pets/bookings")
            
            # Load species mappings
            try:
                species_rows = conn.execute(sa.text("SELECT legacy_spec_no, id FROM species WHERE legacy_spec_no IS NOT NULL")).all()
                lookup['species'] = {row[0]: row[1] for row in species_rows}
                print(f"Preloaded {len(lookup['species'])} species mappings")
            except Exception as e:
                print(f"Could not load species mappings: {e}")
                lookup['species'] = {}
            
            # Load vets mappings
            try:
                vet_rows = conn.execute(sa.text("SELECT legacy_vet_no, id FROM vets WHERE legacy_vet_no IS NOT NULL")).all()
                lookup['vets'] = {row[0]: row[1] for row in vet_rows}
                print(f"Preloaded {len(lookup['vets'])} vet mappings")
            except Exception as e:
                print(f"Could not load vet mappings: {e}")
                lookup['vets'] = {}
            
            # Load breeds mappings
            try:
                breed_rows = conn.execute(sa.text("SELECT legacy_breed_no, id FROM breeds WHERE legacy_breed_no IS NOT NULL")).all()
                lookup['breeds'] = {row[0]: row[1] for row in breed_rows}
                print(f"Preloaded {len(lookup['breeds'])} breed mappings")
            except Exception as e:
                print(f"Could not load breed mappings: {e}")
                lookup['breeds'] = {}

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
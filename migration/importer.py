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
#           })
# Only declare FK columns that need translation; simple columns stay as-is.
IMPORT_PLAN = [
    ("v_vets", "vets", {}),
    ("v_customers", "customers", {"default_vet_id": "vets"}),
    ("v_contacts", "contacts", {}),
    ("v_customer_contacts", "customer_contacts",
        {"customer_id": "customers", "contact_id": "contacts"}),
    # add more tuples …
]

# ---------------------------------------------------------------------------
_engine_src = sa.create_engine(settings.mssql_url, fast_executemany=True)
_engine_dst = sa.create_engine(settings.pg_url)
_meta_dst   = sa.MetaData(bind=_engine_dst)


def stream_rows(view: str):
    sql = sa.text(f"SELECT * FROM {view} ORDER BY legacy_id")
    with _engine_src.connect() as conn:
        return conn.execution_options(stream_results=True).execute(sql)


def load_table(dest_name: str):
    return sa.Table(dest_name, _meta_dst, autoload_with=_engine_dst)


def translate_fk(record: dict, fk_map: dict[str, str]):
    """Replace legacy FK ints with new ones via lookup dicts."""
    for col, lookup_key in fk_map.items():
        legacy_val = record.pop(f"legacy_{col}")
        if legacy_val is None:
            record[col] = None
        else:
            try:
                record[col] = lookup[lookup_key][legacy_val]
            except KeyError as exc:
                raise KeyError(
                    f"No lookup value for {lookup_key}[{legacy_val}] while populating {col}"
                ) from exc


def import_table(view: str, dest_name: str, fk_map: dict[str, str]):
    dest_tbl = load_table(dest_name)
    pending: list[dict] = []
    legacy_ids: list[int] = []

    for row in tqdm(stream_rows(view), desc=f"{view}->{dest_name}"):
        rec = dict(row)
        legacy_id = rec.pop("legacy_id")
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
    result = _engine_dst.execute(insert(dest_tbl).returning(dest_tbl.c.id), rows)
    new_ids = result.scalars().all()
    lookup[dest_name].update(dict(zip(legacy_ids, new_ids)))


# ---------------------------------------------------------------------------
def main():  # pragma: no cover
    for view, dest_tbl, fk_map in IMPORT_PLAN:
        import_table(view, dest_tbl, fk_map)


if __name__ == "__main__":
    main() 
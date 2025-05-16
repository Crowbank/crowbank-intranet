from __future__ import annotations

"""Runtime lookup tables that map legacy primary keys to new PostgreSQL ids.

The importer populates these dicts as it goes; other tables can then
translate their legacy foreign-key columns.
"""

from collections import defaultdict
from typing import Dict

# lookup["customers"][legacy_id] == new_id
lookup: Dict[str, Dict[int, int]] = defaultdict(dict) 
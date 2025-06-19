#!/usr/bin/env python3
"""
Import script for daily allocations from legacy booking allocations.
"""

import sqlalchemy as sa
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import insert
from tqdm import tqdm
from migration.config import settings

def create_mappings():
    """Create booking, pet, and run mappings."""
    legacy_engine = sa.create_engine(settings.mssql_url)
    pg_engine = sa.create_engine(settings.pg_url)
    
    print("Creating mappings...")
    
    with legacy_engine.connect() as legacy_conn:
        # Get legacy booking numbers in order (same as booking-pet import)
        result = legacy_conn.execute(sa.text('SELECT legacy_bk_no FROM v_bookings ORDER BY legacy_bk_no'))
        legacy_bk_nos = [row[0] for row in result]
    
    with pg_engine.connect() as pg_conn:
        # Get PostgreSQL booking IDs in order
        result = pg_conn.execute(sa.text('SELECT id FROM bookings ORDER BY id'))
        pg_booking_ids = [row[0] for row in result]
        
        # Create booking mapping by position
        booking_map = dict(zip(legacy_bk_nos, pg_booking_ids))
        
        # Get pets mapping by name (since allocations use pet names)
        result = pg_conn.execute(sa.text('SELECT LOWER(name), id FROM pets'))
        pets_by_name = {row[0]: row[1] for row in result}
        
        # Get boarding runs mapping by name
        result = pg_conn.execute(sa.text('SELECT name, id FROM boarding_runs'))
        runs_by_name = {row[0]: row[1] for row in result}
        
        # Also map by description patterns
        run_mappings = {
            'Unalloc': 1,  # UNALLOC
            'Deluxe F': 51,  # Deluxe F
            'Deluxe R': 52,  # Deluxe R
            'South F1': 7,
            'South F2': 8,
            'South F3': 9,
            'South F4': 10,
            'South F5': 11,
            'South F6': 20,
            'South F7': 21,
            'South F8': 22,
            'South R1': 25,
            'South R2': 26,
            'South R3': 27,
            'South R4': 28,
            'South R5': 29,
            'South R6': 30,
            'South R7': 31,
            'South R8': 32,
            'North F1': 35,
            'North F2': 36,
            'North F3': 37,
            'North F5': 39,
            'North F6': 40,
            'North R1': 43,
            'North R2': 44,
            'North R3': 45,
            'North R4': 46,
            'North R5': 47,
            'North R6': 48,
            'Double F7': 41,
            'Double F8': 42,
            'Double R7': 49,
            'Double R8': 50,
        }
        
        print(f"✅ Created booking mapping for {len(booking_map)} bookings")
        print(f"✅ Created pet mapping for {len(pets_by_name)} pets")
        print(f"✅ Created run mapping for {len(run_mappings)} runs")
        
        return booking_map, pets_by_name, run_mappings

def parse_pets(pet_string):
    """Parse comma-separated pet names."""
    if not pet_string:
        return []
    return [name.strip() for name in pet_string.split(',')]

def generate_daily_allocations():
    """Generate daily allocation records from legacy data."""
    legacy_engine = sa.create_engine(settings.mssql_url)
    pg_engine = sa.create_engine(settings.pg_url)
    
    # Create mappings
    booking_map, pets_by_name, run_mappings = create_mappings()
    
    print("Importing daily allocations...")
    
    with legacy_engine.connect() as legacy_conn:
        # Get all booking allocations
        result = legacy_conn.execute(sa.text('''
            SELECT ba_bk_no, ba_start_date, ba_end_date, ba_pets, ba_run_desc
            FROM vwbookingallocation
            WHERE ba_start_date IS NOT NULL AND ba_end_date IS NOT NULL
            ORDER BY ba_bk_no
        '''))
        allocations = result.all()
    
    with pg_engine.begin() as pg_conn:
        # Clear existing daily allocations
        pg_conn.execute(sa.text('TRUNCATE TABLE daily_allocations'))
        
        daily_records = []
        skipped = 0
        
        for allocation in tqdm(allocations, desc="Processing allocations"):
            ba_bk_no, start_date, end_date, ba_pets, ba_run_desc = allocation
            
            # Map booking
            if ba_bk_no not in booking_map:
                print(f"⚠️  Skipping allocation: booking {ba_bk_no} not found")
                skipped += 1
                continue
            
            booking_id = booking_map[ba_bk_no]
            
            # Map run
            if ba_run_desc not in run_mappings:
                print(f"⚠️  Skipping allocation: run '{ba_run_desc}' not mapped")
                skipped += 1
                continue
            
            boarding_run_id = run_mappings[ba_run_desc]
            
            # Parse pets
            pet_names = parse_pets(ba_pets)
            pet_ids = []
            for pet_name in pet_names:
                pet_name_lower = pet_name.lower()
                if pet_name_lower in pets_by_name:
                    pet_ids.append(pets_by_name[pet_name_lower])
                else:
                    print(f"⚠️  Pet '{pet_name}' not found for booking {ba_bk_no}")
            
            if not pet_ids:
                print(f"⚠️  No valid pets found for booking {ba_bk_no}")
                skipped += 1
                continue
            
            # Generate daily records for each date in the range
            current_date = start_date
            while current_date <= end_date:
                for pet_id in pet_ids:
                    daily_records.append({
                        'allocation_date': current_date,
                        'booking_id': booking_id,
                        'pet_id': pet_id,
                        'boarding_run_id': boarding_run_id
                    })
                current_date += timedelta(days=1)
        
        # Insert daily allocations
        if daily_records:
            # Remove duplicates
            unique_records = []
            seen = set()
            for record in daily_records:
                key = (record['allocation_date'], record['booking_id'], record['pet_id'])
                if key not in seen:
                    unique_records.append(record)
                    seen.add(key)
            
            print(f"Inserting {len(unique_records)} daily allocation records...")
            
            # Load the daily_allocations table
            meta = sa.MetaData()
            daily_allocations_table = sa.Table('daily_allocations', meta, autoload_with=pg_engine)
            
            # Insert in batches
            batch_size = 1000
            for i in range(0, len(unique_records), batch_size):
                batch = unique_records[i:i + batch_size]
                stmt = insert(daily_allocations_table).values(batch)
                pg_conn.execute(stmt)
            
            print(f"✅ Imported {len(unique_records)} daily allocation records")
            if skipped:
                print(f"⚠️  Skipped {skipped} allocations due to missing mappings")
        else:
            print("❌ No daily allocations to import")

if __name__ == "__main__":
    generate_daily_allocations()
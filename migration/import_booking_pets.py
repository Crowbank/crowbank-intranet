#!/usr/bin/env python3
"""
Direct import script for booking-pet associations.
This handles the complex mapping between legacy bookings and pets.
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from tqdm import tqdm
from migration.config import settings

def create_booking_mapping():
    """Create mapping from legacy booking numbers to PostgreSQL booking IDs."""
    legacy_engine = sa.create_engine(settings.mssql_url)
    pg_engine = sa.create_engine(settings.pg_url)
    
    print("Creating booking mapping...")
    
    # Use a simpler approach: the bookings were imported in order, so map by position
    with legacy_engine.connect() as legacy_conn:
        # Get legacy booking numbers in order
        result = legacy_conn.execute(sa.text('SELECT legacy_bk_no FROM v_bookings ORDER BY legacy_bk_no'))
        legacy_bk_nos = [row[0] for row in result]
    
    with pg_engine.connect() as pg_conn:
        # Get PostgreSQL booking IDs in order
        result = pg_conn.execute(sa.text('SELECT id FROM bookings ORDER BY id'))
        pg_booking_ids = [row[0] for row in result]
        
        # Get pets mapping
        result = pg_conn.execute(sa.text('SELECT legacy_pet_no, id FROM pets WHERE legacy_pet_no IS NOT NULL'))
        pets_map = {row[0]: row[1] for row in result}
        
        # Create booking mapping by position
        if len(legacy_bk_nos) == len(pg_booking_ids):
            booking_map = dict(zip(legacy_bk_nos, pg_booking_ids))
            print(f"✅ Created mapping for {len(booking_map)} bookings by position")
        else:
            print(f"❌ Count mismatch: {len(legacy_bk_nos)} legacy vs {len(pg_booking_ids)} PostgreSQL")
            return {}, pets_map
        
        return booking_map, pets_map

def import_booking_pets():
    """Import booking-pet associations."""
    legacy_engine = sa.create_engine(settings.mssql_url)
    pg_engine = sa.create_engine(settings.pg_url)
    
    # Create mappings
    booking_map, pets_map = create_booking_mapping()
    
    print("Importing booking-pet associations...")
    
    with legacy_engine.connect() as legacy_conn:
        # Get all booking-pet relationships
        result = legacy_conn.execute(sa.text('''
            SELECT legacy_bk_no, legacy_pet_no 
            FROM v_booking_pets
            ORDER BY legacy_bk_no, legacy_pet_no
        '''))
        booking_pets = result.all()
    
    with pg_engine.begin() as pg_conn:
        # Clear existing booking_pets
        pg_conn.execute(sa.text('TRUNCATE TABLE booking_pets'))
        
        associations = []
        skipped = 0
        
        for legacy_bk_no, legacy_pet_no in tqdm(booking_pets, desc="Processing associations"):
            # Map legacy IDs to PostgreSQL IDs
            if legacy_bk_no not in booking_map:
                skipped += 1
                continue
                
            if legacy_pet_no not in pets_map:
                skipped += 1
                continue
                
            booking_id = booking_map[legacy_bk_no]
            pet_id = pets_map[legacy_pet_no]
            
            associations.append({
                'booking_id': booking_id,
                'pet_id': pet_id,
                'requires_medication': False  # Default value
            })
        
        # Batch insert associations
        if associations:
            # Remove duplicates (some bookings might have multiple entries)
            unique_associations = []
            seen = set()
            for assoc in associations:
                key = (assoc['booking_id'], assoc['pet_id'])
                if key not in seen:
                    unique_associations.append(assoc)
                    seen.add(key)
            
            print(f"Inserting {len(unique_associations)} unique associations...")
            
            # Load the booking_pets table
            meta = sa.MetaData()
            booking_pets_table = sa.Table('booking_pets', meta, autoload_with=pg_engine)
            
            # Insert in batches to avoid parameter limit
            batch_size = 2000
            for i in range(0, len(unique_associations), batch_size):
                batch = unique_associations[i:i + batch_size]
                stmt = insert(booking_pets_table).values(batch)
                stmt = stmt.on_conflict_do_nothing(index_elements=['booking_id', 'pet_id'])
                pg_conn.execute(stmt)
                
            print(f"✅ Inserted {len(unique_associations)} associations in batches")
            
            print(f"✅ Imported {len(unique_associations)} booking-pet associations")
            if skipped:
                print(f"⚠️  Skipped {skipped} associations due to missing mappings")
        else:
            print("❌ No associations to import")

if __name__ == "__main__":
    import_booking_pets()
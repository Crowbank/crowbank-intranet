"""
Simplified script to import legacy customer data directly using SQL.
This avoids ORM mapping issues by using direct SQL commands.
"""
import os
import sys
import logging
from decimal import Decimal
from pathlib import Path

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyodbc
import yaml
import psycopg
from tqdm import tqdm

from app.utils.yaml_config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_legacy_db():
    """Connect to the legacy MSSQL database using config from YAML."""
    config = load_config()
    legacy_db = config['nested']['legacy_database']
    
    # Build connection string
    conn_str = (
        f"DRIVER={{{legacy_db['driver']}}};"
        f"SERVER={legacy_db['server']};"
        f"DATABASE={legacy_db['database']};"
        f"UID={legacy_db['username']};"
        f"PWD={legacy_db['password']};"
        f"{legacy_db['options']}"
    )
    
    logger.info("Connecting to legacy database...")
    return pyodbc.connect(conn_str)

def connect_to_new_db():
    """Connect to the new PostgreSQL database using config from YAML."""
    config = load_config()
    
    # Get database configuration
    db = config['nested']['database']
    user = db.get('user', 'crowbank')
    # Use hardcoded password from config/dev.py
    password = "ZhV8Pk521j1Z"  # Override from config file
    host = db.get('host', '192.168.0.201')
    port = db.get('port', 54320)
    name = db.get('name', 'crowbank')
    
    logger.info("Connecting to new PostgreSQL database...")
    return psycopg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        dbname=name
    )

def get_vet_mapping(pg_conn):
    """Create a mapping from legacy vet IDs to new vet IDs."""
    with pg_conn.cursor() as cursor:
        cursor.execute("SELECT legacy_vet_no, id FROM vets WHERE legacy_vet_no IS NOT NULL")
        mapping = {row[0]: row[1] for row in cursor.fetchall()}
    
    logger.info(f"Found {len(mapping)} vet mappings")
    return mapping

def import_customers(chunk_size=1000):
    """Import customers from legacy view to new database."""
    legacy_conn = connect_to_legacy_db()
    pg_conn = connect_to_new_db()
    
    try:
        # Explicitly set to autocommit=False to manage our own transactions
        pg_conn.autocommit = False
        
        # Get vet mapping
        vet_mapping = get_vet_mapping(pg_conn)
        
        # Query the legacy view
        legacy_cursor = legacy_conn.cursor()
        legacy_cursor.execute("SELECT COUNT(*) FROM v_customers")
        total_rows = legacy_cursor.fetchone()[0]
        logger.info(f"Found {total_rows} customers to import")
        
        # Use a cursor to fetch chunks of data
        legacy_cursor.execute("SELECT * FROM v_customers")
        columns = [column[0] for column in legacy_cursor.description]
        
        imported = 0
        skipped = 0
        
        rows = legacy_cursor.fetchmany(chunk_size)
        
        with pg_conn.cursor() as pg_cursor:
            with tqdm(total=total_rows, desc="Importing customers") as pbar:
                while rows:
                    batch_size = 0
                    for row in rows:
                        # Convert row to dict
                        customer_data = dict(zip(columns, row))
                        
                        # Check if customer already exists
                        pg_cursor.execute(
                            "SELECT id FROM customers WHERE legacy_cust_no = %s", 
                            (customer_data['legacy_cust_no'],)
                        )
                        existing = pg_cursor.fetchone()
                        
                        if existing:
                            skipped += 1
                            pbar.update(1)
                            continue
                        
                        # Map legacy vet ID to new vet ID if possible
                        default_vet_id = None
                        legacy_vet_id = customer_data['legacy_default_vet_id']
                        if legacy_vet_id and legacy_vet_id in vet_mapping:
                            default_vet_id = vet_mapping[legacy_vet_id]
                        
                        # Handle null or empty stripe_id properly
                        stripe_id = customer_data['stripe_id']
                        if not stripe_id or stripe_id.strip() == '':
                            stripe_id = None
                        
                        # Insert new customer
                        pg_cursor.execute("""
                            INSERT INTO customers (
                                legacy_cust_no, street, town, postcode, 
                                notes, banned, opt_out, discount, 
                                stripe_id, default_vet_id
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            customer_data['legacy_cust_no'],
                            customer_data['street'],
                            customer_data['town'],
                            customer_data['postcode'],
                            customer_data['notes'],
                            bool(customer_data['banned']),
                            bool(customer_data['opt_out']),
                            Decimal(str(customer_data['discount'])),
                            stripe_id,
                            default_vet_id
                        ))
                        
                        imported += 1
                        batch_size += 1
                        pbar.update(1)
                        
                        # Commit every 100 records to avoid large transactions
                        if batch_size % 100 == 0:
                            pg_conn.commit()
                            logger.debug(f"Committed batch of {batch_size} records")
                    
                    # Commit any remaining records in this batch
                    pg_conn.commit()
                    logger.debug(f"Committed final {batch_size % 100} records in batch")
                    
                    # Get next chunk
                    rows = legacy_cursor.fetchmany(chunk_size)
        
        logger.info(f"Customer import completed: {imported} imported, {skipped} skipped")
        
        # Verify the import
        with pg_conn.cursor() as pg_cursor:
            pg_cursor.execute("SELECT COUNT(*) FROM customers")
            count = pg_cursor.fetchone()[0]
            logger.info(f"Verification: {count} customers found in database")
            
            if count == 0:
                logger.error("ERROR: No customers were saved to the database!")
                raise Exception("Customer import failed - no customers in database")
                
            pg_cursor.execute("SELECT COUNT(*) FROM customers WHERE legacy_cust_no IS NOT NULL")
            count_with_legacy = pg_cursor.fetchone()[0]
            logger.info(f"Verification: {count_with_legacy} customers have legacy_cust_no")
            
            # Also check a few records to make sure they have the correct data
            pg_cursor.execute("SELECT id, legacy_cust_no FROM customers LIMIT 5")
            sample_customers = pg_cursor.fetchall()
            logger.info(f"Sample customers: {sample_customers}")
        
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error importing customers: {e}")
        raise
    finally:
        legacy_conn.close()
        pg_conn.close()

def import_contacts_from_customers():
    """
    Import contacts from legacy customer data and establish relationships.
    
    Uses the v_contacts view which normalizes the contact data from customer records.
    """
    legacy_conn = connect_to_legacy_db()
    pg_conn = connect_to_new_db()
    
    try:
        # Explicitly set to autocommit=False to manage our own transactions
        pg_conn.autocommit = False
        
        # Query for normalized contact information using the v_contacts view
        legacy_cursor = legacy_conn.cursor()
        query = """
        SELECT role, legacy_customer_id, first_name, last_name, phone_number, email_address
        FROM v_contacts
        """
        legacy_cursor.execute(query)
        rows = legacy_cursor.fetchall()
        
        logger.info(f"Found {len(rows)} contact records from v_contacts view")
        
        # Get mapping of legacy customer numbers to new customer IDs
        with pg_conn.cursor() as pg_cursor:
            pg_cursor.execute("SELECT legacy_cust_no, id FROM customers WHERE legacy_cust_no IS NOT NULL")
            customer_mapping_rows = pg_cursor.fetchall()
            customer_mapping = {row[0]: row[1] for row in customer_mapping_rows}
        
        logger.info(f"Found {len(customer_mapping)} customer mappings")
        
        # Debug the first few mappings
        first_mappings = list(customer_mapping.items())[:5]
        logger.info(f"First few mappings: {first_mappings}")
        
        # Debug the first few legacy customer numbers from the query
        first_legacy_nos = [row[1] for row in rows[:5]]
        logger.info(f"First few legacy customer IDs from contacts: {first_legacy_nos}")
        
        # Track created contacts to avoid duplicates
        email_to_contact = {}  # Maps email to contact ID to avoid duplicates
        name_to_contact = {}   # Maps name to contact ID as fallback for contacts without email
        
        total_primary = 0
        total_secondary = 0
        total_emergency = 0
        
        with pg_conn.cursor() as pg_cursor:
            with tqdm(total=len(rows), desc="Processing contacts") as pbar:
                batch_size = 0
                
                for row in rows:
                    role, legacy_cust_no, first_name, last_name, phone_number, email_address = row
                    
                    # Skip if this customer wasn't imported
                    if legacy_cust_no not in customer_mapping:
                        pbar.update(1)
                        continue
                        
                    customer_id = customer_mapping[legacy_cust_no]
                    
                    # Skip if missing both name and contact info
                    if not ((first_name and first_name.strip()) or 
                            (last_name and last_name.strip()) or
                            (email_address and email_address.strip()) or
                            (phone_number and phone_number.strip())):
                        pbar.update(1)
                        continue
                    
                    # Normalize values
                    first_name = (first_name or '').strip()
                    last_name = (last_name or '').strip()
                    phone_number = (phone_number or '').strip()
                    email_address = (email_address or '').strip()
                    
                    # Create full name for matching
                    full_name = f"{first_name} {last_name}".strip().lower()
                    
                    # Find existing contact or create new one
                    contact_id = None
                    
                    # Check if contact exists by email
                    if email_address:
                        if email_address in email_to_contact:
                            contact_id = email_to_contact[email_address]
                        else:
                            pg_cursor.execute(
                                "SELECT id FROM contacts WHERE email_address = %s", 
                                (email_address,)
                            )
                            existing = pg_cursor.fetchone()
                            if existing:
                                contact_id = existing[0]
                                email_to_contact[email_address] = contact_id
                    
                    # If not found by email and we have a name, try by name
                    if not contact_id and full_name and full_name in name_to_contact:
                        contact_id = name_to_contact[full_name]
                    
                    # Create new contact if not found
                    if not contact_id:
                        pg_cursor.execute("""
                            INSERT INTO contacts (
                                first_name, last_name, phone_number, email_address
                            ) VALUES (%s, %s, %s, %s)
                            RETURNING id
                        """, (
                            first_name, 
                            last_name,
                            phone_number, 
                            email_address if email_address else None
                        ))
                        contact_id = pg_cursor.fetchone()[0]
                        
                        # Track by email and name for future reference
                        if email_address:
                            email_to_contact[email_address] = contact_id
                        if full_name:
                            name_to_contact[full_name] = contact_id
                    
                    # Create association with the correct role
                    pg_cursor.execute("""
                        INSERT INTO customer_contacts (
                            customer_id, contact_id, role
                        ) VALUES (%s, %s, %s)
                        ON CONFLICT (customer_id, contact_id) DO NOTHING
                    """, (
                        customer_id,
                        contact_id,
                        role.lower()  # Convert to lowercase to match the enum values
                    ))
                    
                    # Update counters
                    if role == 'PRIMARY':
                        total_primary += 1
                    elif role == 'SECONDARY':
                        total_secondary += 1
                    elif role == 'EMERGENCY':
                        total_emergency += 1
                    
                    batch_size += 1
                    pbar.update(1)
                    
                    # Commit every 100 records to avoid large transactions
                    if batch_size % 100 == 0:
                        pg_conn.commit()
                        batch_size = 0
                
                # Commit any remaining records
                if batch_size > 0:
                    pg_conn.commit()
        
        # Verify the import
        with pg_conn.cursor() as pg_cursor:
            pg_cursor.execute("SELECT COUNT(*) FROM contacts")
            contact_count = pg_cursor.fetchone()[0]
            logger.info(f"Verification: {contact_count} contacts found in database")
            
            pg_cursor.execute("SELECT COUNT(*) FROM customer_contacts")
            assoc_count = pg_cursor.fetchone()[0]
            logger.info(f"Verification: {assoc_count} customer-contact associations")
        
        logger.info(f"Contact import completed: {contact_count} contacts, {total_primary} primary, {total_secondary} secondary, {total_emergency} emergency relationships")
        
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error importing contacts: {e}")
        raise
    finally:
        legacy_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    # Import customers first
    import_customers()
    
    # Then import contacts from customer data
    import_contacts_from_customers() 
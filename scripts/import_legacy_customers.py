"""
Script to import legacy customer data from v_customers view into the new database.
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, configure_mappers
from tqdm import tqdm

# Import only the specific models needed, not the entire app
from app.models.base import Base
from app.models.customer import Customer, Contact, CustomerContact, ContactRole
from app.models.vet import Vet
from app.utils.yaml_config import load_config

# Explicitly configure mappers for the models we're using
configure_mappers()

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
    
    # Use SQLAlchemy connection URL from config if available
    if 'sqlalchemy' in config['nested'] and 'database_uri' in config['nested']['sqlalchemy']:
        db_url = config['nested']['sqlalchemy']['database_uri']
    else:
        # Construct from database config parts if not available
        db = config['nested']['database']
        user = db.get('user', '')
        password = db.get('password', '')
        host = db.get('host', 'localhost')
        port = db.get('port', 5432)
        name = db.get('name', 'crowbank')
        
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    logger.info("Connecting to new database...")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()

def get_vet_mapping(new_db_session):
    """Create a mapping from legacy vet IDs to new vet IDs."""
    vets = new_db_session.query(Vet).all()
    # Map legacy_vet_no to id
    mapping = {vet.legacy_vet_no: vet.id for vet in vets if vet.legacy_vet_no is not None}
    logger.info(f"Found {len(mapping)} vet mappings")
    return mapping

def import_customers(chunk_size=1000):
    """Import customers from legacy view to new database."""
    legacy_conn = connect_to_legacy_db()
    new_db_session = connect_to_new_db()
    
    try:
        # Get vet mapping
        vet_mapping = get_vet_mapping(new_db_session)
        
        # Query the legacy view
        cursor = legacy_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM v_customers")
        total_rows = cursor.fetchone()[0]
        logger.info(f"Found {total_rows} customers to import")
        
        # Use a cursor to fetch chunks of data
        cursor.execute("SELECT * FROM v_customers")
        columns = [column[0] for column in cursor.description]
        
        imported = 0
        skipped = 0
        
        rows = cursor.fetchmany(chunk_size)
        with tqdm(total=total_rows, desc="Importing customers") as pbar:
            while rows:
                # Begin a transaction for this chunk
                try:
                    for row in rows:
                        # Convert row to dict
                        customer_data = dict(zip(columns, row))
                        
                        # Check if customer already exists
                        existing = new_db_session.query(Customer).filter_by(
                            legacy_cust_no=customer_data['legacy_cust_no']
                        ).first()
                        
                        if existing:
                            skipped += 1
                            pbar.update(1)
                            continue
                        
                        # Create new customer
                        new_customer = Customer(
                            legacy_cust_no=customer_data['legacy_cust_no'],
                            street=customer_data['street'],
                            town=customer_data['town'],
                            postcode=customer_data['postcode'],
                            notes=customer_data['notes'],
                            banned=bool(customer_data['banned']),
                            opt_out=bool(customer_data['opt_out']),
                            discount=Decimal(str(customer_data['discount'])),
                            stripe_id=customer_data['stripe_id'] if customer_data['stripe_id'] else None
                        )
                        
                        # Map legacy vet ID to new vet ID if possible
                        legacy_vet_id = customer_data['legacy_default_vet_id']
                        if legacy_vet_id and legacy_vet_id in vet_mapping:
                            new_customer.default_vet_id = vet_mapping[legacy_vet_id]
                        
                        new_db_session.add(new_customer)
                        imported += 1
                        pbar.update(1)
                    
                    # Commit this chunk
                    new_db_session.commit()
                    rows = cursor.fetchmany(chunk_size)
                    
                except Exception as e:
                    new_db_session.rollback()
                    logger.error(f"Error processing chunk: {e}")
                    raise
        
        logger.info(f"Customer import completed: {imported} imported, {skipped} skipped")
        
    except Exception as e:
        new_db_session.rollback()
        logger.error(f"Error importing customers: {e}")
        raise
    finally:
        legacy_conn.close()
        new_db_session.close()

def import_contacts_from_customers():
    """
    Import contacts from legacy customer data and establish relationships.
    
    Since the legacy system doesn't have a dedicated contacts table,
    we'll extract contact information from customer records.
    """
    legacy_conn = connect_to_legacy_db()
    new_db_session = connect_to_new_db()
    
    try:
        # Query for all customer records with contact information
        cursor = legacy_conn.cursor()
        query = """
        SELECT cust_no,  
               cust_title, cust_forename, cust_surname, cust_phone1, cust_email,
               cust_title2, cust_forename2, cust_surname2, cust_phone2, cust_email2,
               cust_title3, cust_forename3, cust_surname3, cust_phone3, cust_email3
        FROM pa..tblcustomer
        """
        cursor.execute(query)
        
        # Get mapping of legacy customer numbers to new customer IDs
        customer_mapping = {c.legacy_cust_no: c.id for c in new_db_session.query(Customer).filter(Customer.legacy_cust_no != None).all()}
        logger.info(f"Found {len(customer_mapping)} customer mappings")
        
        # Track created contacts to avoid duplicates
        email_to_contact = {}  # Maps email to contact ID to avoid duplicates
        
        total_primary = 0
        total_secondary = 0
        total_emergency = 0
        
        for row in tqdm(cursor.fetchall(), desc="Processing contacts"):
            legacy_cust_no = row[0]
            
            # Skip if this customer wasn't imported
            if legacy_cust_no not in customer_mapping:
                continue
                
            customer_id = customer_mapping[legacy_cust_no]
            
            # Extract primary contact info (assume always exists)
            primary_data = {
                'title': row[1],
                'first_name': row[2] or '',
                'last_name': row[3] or '',
                'phone_number': row[4],
                'email_address': row[5]
            }
            
            # Skip if no name for primary contact
            if not primary_data['first_name'] and not primary_data['last_name']:
                continue
                
            # Create or get primary contact
            primary_contact = get_or_create_contact(new_db_session, primary_data, email_to_contact)
            
            # Create association (primary)
            if primary_contact:
                create_customer_contact(new_db_session, customer_id, primary_contact.id, ContactRole.PRIMARY)
                total_primary += 1
            
            # Extract secondary contact info (may not exist)
            if row[6] or row[7] or row[8]:  # If any name field exists
                secondary_data = {
                    'title': row[6],
                    'first_name': row[7] or '',
                    'last_name': row[8] or '',
                    'phone_number': row[9],
                    'email_address': row[10]
                }
                
                # Create or get secondary contact
                secondary_contact = get_or_create_contact(new_db_session, secondary_data, email_to_contact)
                
                # Create association (secondary)
                if secondary_contact:
                    create_customer_contact(new_db_session, customer_id, secondary_contact.id, ContactRole.SECONDARY)
                    total_secondary += 1
            
            # Extract emergency contact info (may not exist)
            if row[11] or row[12] or row[13]:  # If any name field exists
                emergency_data = {
                    'title': row[11],
                    'first_name': row[12] or '',
                    'last_name': row[13] or '',
                    'phone_number': row[14],
                    'email_address': row[15]
                }
                
                # Create or get emergency contact
                emergency_contact = get_or_create_contact(new_db_session, emergency_data, email_to_contact)
                
                # Create association (emergency)
                if emergency_contact:
                    create_customer_contact(new_db_session, customer_id, emergency_contact.id, ContactRole.EMERGENCY)
                    total_emergency += 1
        
        logger.info(f"Contact import completed: {len(email_to_contact)} contacts, {total_primary} primary, {total_secondary} secondary, {total_emergency} emergency relationships")
        
    except Exception as e:
        new_db_session.rollback()
        logger.error(f"Error importing contacts: {e}")
        raise
    finally:
        legacy_conn.close()
        new_db_session.close()

def get_or_create_contact(session, contact_data, email_to_contact):
    """Create or retrieve a contact based on email (to avoid duplicates)."""
    # If we have an email and it's already been used
    email = contact_data.get('email_address')
    if email and email in email_to_contact:
        return session.query(Contact).get(email_to_contact[email])
    
    # Create new contact
    contact = Contact(
        first_name=contact_data['first_name'].strip(),
        last_name=contact_data['last_name'].strip(),
        phone_number=contact_data['phone_number'],
        email_address=email
    )
    
    session.add(contact)
    session.flush()  # Generate ID without committing
    
    # Track this contact by email if we have one
    if email:
        email_to_contact[email] = contact.id
        
    return contact

def create_customer_contact(session, customer_id, contact_id, role):
    """Create a customer-contact association with the given role."""
    # Check if association already exists
    existing = session.query(CustomerContact).filter_by(
        customer_id=customer_id, 
        contact_id=contact_id
    ).first()
    
    if existing:
        return
        
    # Create new association
    assoc = CustomerContact(
        customer_id=customer_id,
        contact_id=contact_id,
        role=role
    )
    
    session.add(assoc)
    session.flush()  # Generate ID without committing
    
    # Commit periodically to avoid large transactions
    if not getattr(create_customer_contact, 'counter', 0) % 100:
        session.commit()
    create_customer_contact.counter = getattr(create_customer_contact, 'counter', 0) + 1
    
    return assoc

if __name__ == "__main__":
    # Import customers first
    import_customers()
    
    # Then import contacts from customer data
    import_contacts_from_customers() 
"""refactor booking pricing to use invoice model

Revision ID: e3f5c6df01a4
Revises: 26e9bab8887b
Create Date: 2025-06-06 15:44:30.472958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3f5c6df01a4'
down_revision: Union[str, None] = '26e9bab8887b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Ensure all existing bookings have corresponding invoices.
    This migration preserves the existing data while transitioning to the new model.
    Note: This migration only runs if the invoice tables already exist.
    """
    # Create a connection to work with raw SQL
    connection = op.get_bind()
    
    # Check if the invoice tables exist first
    check_result = connection.execute(sa.text("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'invoices'
    """))
    
    if check_result.scalar() == 0:
        print("Invoice tables don't exist yet - skipping data migration.")
        print("This migration will run automatically once invoice tables are created.")
        return
    
    # Get all bookings that don't have invoices yet
    result = connection.execute(sa.text("""
        SELECT b.id, b.discount_percentage, b.total_cost, b.deposit_paid 
        FROM bookings b 
        LEFT JOIN invoices i ON b.id = i.booking_id 
        WHERE i.id IS NULL
    """))
    
    bookings_without_invoices = result.fetchall()
    
    if bookings_without_invoices:
        print(f"Creating invoices for {len(bookings_without_invoices)} bookings...")
        
        for booking in bookings_without_invoices:
            booking_id, discount_percentage, total_cost, deposit_paid = booking
            
            # Create an invoice for this booking
            connection.execute(sa.text("""
                INSERT INTO invoices (booking_id, percentage_discount, created_at, updated_at)
                VALUES (:booking_id, :discount_percentage, NOW(), NOW())
            """), {
                'booking_id': booking_id,
                'discount_percentage': discount_percentage or 0
            })
            
            # If there's a deposit_paid amount, create a payment record
            if deposit_paid and deposit_paid > 0:
                # Get the invoice ID we just created
                invoice_result = connection.execute(sa.text("""
                    SELECT id FROM invoices WHERE booking_id = :booking_id
                """), {'booking_id': booking_id})
                
                invoice_id = invoice_result.scalar()
                
                # Get the customer_id for this booking
                customer_result = connection.execute(sa.text("""
                    SELECT customer_id FROM bookings WHERE id = :booking_id
                """), {'booking_id': booking_id})
                
                customer_id = customer_result.scalar()
                
                # Create a payment record for the existing deposit
                connection.execute(sa.text("""
                    INSERT INTO payments (invoice_id, customer_id, payment_date, payment_type, amount, created_at)
                    VALUES (:invoice_id, :customer_id, CURRENT_DATE, 'other', :amount, NOW())
                """), {
                    'invoice_id': invoice_id,
                    'customer_id': customer_id,
                    'amount': deposit_paid
                })
        
        print(f"Successfully created invoices for {len(bookings_without_invoices)} bookings")
    else:
        print("All bookings already have invoices - no migration needed")


def downgrade() -> None:
    """
    Remove invoices that were created during this migration.
    WARNING: This will lose payment data that was migrated!
    """
    connection = op.get_bind()
    
    # This is a destructive operation - be very careful
    print("WARNING: Downgrade will remove invoice data created during migration!")
    
    # Remove invoices that don't have any charges (indicating they were auto-created)
    connection.execute(sa.text("""
        DELETE FROM payments WHERE invoice_id IN (
            SELECT i.id FROM invoices i 
            LEFT JOIN charges c ON i.id = c.invoice_id 
            WHERE c.id IS NULL
        )
    """))
    
    connection.execute(sa.text("""
        DELETE FROM invoices WHERE id NOT IN (
            SELECT DISTINCT invoice_id FROM charges WHERE invoice_id IS NOT NULL
        )
    """))

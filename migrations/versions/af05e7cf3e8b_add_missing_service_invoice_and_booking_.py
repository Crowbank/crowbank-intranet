"""Add missing service invoice and booking intent tables

Revision ID: af05e7cf3e8b
Revises: 55365d6fefb9
Create Date: 2025-06-16 12:12:02.033257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af05e7cf3e8b'
down_revision: Union[str, None] = '55365d6fefb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing tables for services, invoices, and booking intents."""
    
    # Define enum types (they will be created automatically when referenced in tables)
    servicetype_enum = sa.Enum('BOARDING', 'TRANSPORT', 'GROOMING', 'DAYCARE', 'ADMIN', 'OTHER', name='servicetype')
    serviceapplicability_enum = sa.Enum('PER_BOOKING', 'PER_PET', 'PER_PET_DAY', 'PER_TRANSPORT', 'ADHOC', name='serviceapplicability')
    ratetype_enum = sa.Enum('BY_SPECIES', 'BY_BREED_TYPE', 'BY_RANGE', 'FIXED', name='ratetype')
    season_enum = sa.Enum('STANDARD', 'PEAK', 'LOW', 'HOLIDAY', name='season')
    paymenttype_enum = sa.Enum('CASH', 'BANK_TRANSFER', 'STRIPE', 'OTHER', 'CREDIT', 'VOUCHER', name='paymenttype')
    chargetype_enum = sa.Enum('BOOKING', 'TRANSPORT', 'BOARDING', 'ADHOC', 'ADJUSTMENT', 'VET_BILL', name='chargetype')
    bookingintentStatus_enum = sa.Enum('OPEN', 'APPROVED', 'REJECTED', 'WAIT_LIST', 'DUPLICATE', 'CANCELLED', name='bookingintentstatus')
    
    # Create peak_dates table
    op.create_table('peak_dates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date')
    )
    
    # Create services table
    op.create_table('services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('service_type', servicetype_enum, nullable=False),
        sa.Column('applicability', serviceapplicability_enum, nullable=False),
        sa.Column('rate_type', ratetype_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('peak_rate_multiplier', sa.Numeric(precision=5, scale=2), nullable=False, default=2.0),
        sa.Column('min_days_standard', sa.Integer(), nullable=True),
        sa.Column('min_days_peak', sa.Integer(), nullable=True),
        sa.Column('min_days_low', sa.Integer(), nullable=True),
        sa.Column('min_days_holiday', sa.Integer(), nullable=True),
        sa.Column('legacy_service_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('legacy_service_id')
    )
    
    # Create service_rates table
    op.create_table('service_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('category_legacy', sa.Integer(), nullable=True),
        sa.Column('category', sa.Integer(), nullable=True),
        sa.Column('rate', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('season', season_enum, nullable=False, default='STANDARD'),
        sa.Column('effective_from', sa.Date(), nullable=True),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['service_id'], ['services.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create invoices table
    op.create_table('invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('percentage_discount', sa.Numeric(precision=5, scale=2), nullable=False, default=0),
        sa.Column('absolute_discount', sa.Numeric(precision=10, scale=2), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_id')
    )
    
    # Create booking_intents table  
    op.create_table('booking_intents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('arrival_date', sa.Date(), nullable=False),
        sa.Column('departure_date', sa.Date(), nullable=False),
        sa.Column('arrival_period', sa.Enum('AM', 'PM', name='dayperiod'), nullable=True),
        sa.Column('departure_period', sa.Enum('AM', 'PM', name='dayperiod'), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('destination', sa.String(length=255), nullable=True),
        sa.Column('status', bookingintentStatus_enum, nullable=False, default='OPEN'),
        sa.Column('status_notes', sa.Text(), nullable=True),
        sa.Column('auto_approved', sa.Boolean(), nullable=False, default=False),
        sa.Column('gravity_form_id', sa.Integer(), nullable=True),
        sa.Column('gravity_entry_id', sa.Integer(), nullable=True),
        sa.Column('form_submission_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('duplicate_of_id', sa.Integer(), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('handled_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['duplicate_of_id'], ['booking_intents.id']),
        sa.ForeignKeyConstraint(['form_submission_id'], ['form_submissions.id']),
        sa.ForeignKeyConstraint(['handled_by_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create charges table
    op.create_table('charges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('charge_type', chargetype_enum, nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=5, scale=2), nullable=False, default=1),
        sa.Column('is_quantity_overridden', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_rate_overridden', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_peak', sa.Boolean(), nullable=False, default=False),
        sa.Column('minimum_days', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id']),
        sa.ForeignKeyConstraint(['service_id'], ['services.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_type', paymenttype_enum, nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('fees', sa.Numeric(precision=10, scale=2), nullable=False, default=0),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create booking_intent_pets association table
    op.create_table('booking_intent_pets',
        sa.Column('booking_intent_id', sa.Integer(), nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['booking_intent_id'], ['booking_intents.id']),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id']),
        sa.PrimaryKeyConstraint('booking_intent_id', 'pet_id')
    )
    
    # Add foreign key to bookings table for booking_intent connection
    op.add_column('bookings', sa.Column('booking_intent_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_bookings_booking_intent', 'bookings', 'booking_intents', ['booking_intent_id'], ['id'])


def downgrade() -> None:
    """Remove the added tables and columns."""
    
    # Drop foreign key and column from bookings table
    op.drop_constraint('fk_bookings_booking_intent', 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'booking_intent_id')
    
    # Drop tables in reverse order to avoid foreign key issues
    op.drop_table('booking_intent_pets')
    op.drop_table('payments')
    op.drop_table('charges')
    op.drop_table('booking_intents')
    op.drop_table('invoices')
    op.drop_table('service_rates')
    op.drop_table('services')
    op.drop_table('peak_dates')
    
    # Drop enum types (checking first to avoid errors if already dropped)
    sa.Enum(name='bookingintentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='chargetype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='paymenttype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='season').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='ratetype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='serviceapplicability').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='servicetype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='dayperiod').drop(op.get_bind(), checkfirst=True)

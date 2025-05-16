"""Add legacy id columns for reverse migration

Revision ID: 5d1be9c1c2f0
Revises: 86ca15789c6a
Create Date: 2025-05-16 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5d1be9c1c2f0'
down_revision: Union[str, None] = '86ca15789c6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add/rename legacy columns."""
    # Add new nullable legacy columns (unique constraints optional for now)
    op.add_column('boarding_runs', sa.Column('legacy_run_no', sa.Integer(), nullable=True))

    # bookings: rename existing column
    with op.batch_alter_table('bookings') as batch:
        batch.alter_column('legacy_booking_no', new_column_name='legacy_bk_no')
        # Ensure uniqueness
        batch.create_unique_constraint('uq_bookings_legacy_bk_no', ['legacy_bk_no'])

    op.add_column('breed_categories', sa.Column('legacy_breedcat_no', sa.Integer(), nullable=True))
    op.add_column('breeds', sa.Column('legacy_breed_no', sa.Integer(), nullable=True))
    op.add_column('employees', sa.Column('legacy_emp_no', sa.Integer(), nullable=True))
    op.add_column('pets', sa.Column('legacy_pet_no', sa.Integer(), nullable=True))
    op.add_column('species', sa.Column('legacy_spec_no', sa.Integer(), nullable=True))
    op.add_column('vaccinations', sa.Column('legacy_inn_no', sa.Integer(), nullable=True))
    op.add_column('vets', sa.Column('legacy_vet_no', sa.Integer(), nullable=True))

    # Unique constraints
    op.create_unique_constraint('uq_boarding_runs_legacy_run_no', 'boarding_runs', ['legacy_run_no'])
    op.create_unique_constraint('uq_breed_categories_legacy_breedcat_no', 'breed_categories', ['legacy_breedcat_no'])
    op.create_unique_constraint('uq_breeds_legacy_breed_no', 'breeds', ['legacy_breed_no'])
    op.create_unique_constraint('uq_employees_legacy_emp_no', 'employees', ['legacy_emp_no'])
    op.create_unique_constraint('uq_pets_legacy_pet_no', 'pets', ['legacy_pet_no'])
    op.create_unique_constraint('uq_species_legacy_spec_no', 'species', ['legacy_spec_no'])
    op.create_unique_constraint('uq_vaccinations_legacy_inn_no', 'vaccinations', ['legacy_inn_no'])
    op.create_unique_constraint('uq_vets_legacy_vet_no', 'vets', ['legacy_vet_no'])


def downgrade() -> None:
    """Revert legacy column changes."""
    op.drop_constraint('uq_vets_legacy_vet_no', 'vets', type_='unique')
    op.drop_constraint('uq_vaccinations_legacy_inn_no', 'vaccinations', type_='unique')
    op.drop_constraint('uq_species_legacy_spec_no', 'species', type_='unique')
    op.drop_constraint('uq_pets_legacy_pet_no', 'pets', type_='unique')
    op.drop_constraint('uq_employees_legacy_emp_no', 'employees', type_='unique')
    op.drop_constraint('uq_breeds_legacy_breed_no', 'breeds', type_='unique')
    op.drop_constraint('uq_breed_categories_legacy_breedcat_no', 'breed_categories', type_='unique')
    op.drop_constraint('uq_boarding_runs_legacy_run_no', 'boarding_runs', type_='unique')

    op.drop_column('vets', 'legacy_vet_no')
    op.drop_column('vaccinations', 'legacy_inn_no')
    op.drop_column('species', 'legacy_spec_no')
    op.drop_column('pets', 'legacy_pet_no')
    op.drop_column('employees', 'legacy_emp_no')
    op.drop_column('breeds', 'legacy_breed_no')
    op.drop_column('breed_categories', 'legacy_breedcat_no')
    op.drop_column('boarding_runs', 'legacy_run_no')

    # bookings rename back
    with op.batch_alter_table('bookings') as batch:
        batch.drop_constraint('uq_bookings_legacy_bk_no', type_='unique')
        batch.alter_column('legacy_bk_no', new_column_name='legacy_booking_no')
        batch.create_unique_constraint('uq_bookings_legacy_booking_no', ['legacy_booking_no']) 
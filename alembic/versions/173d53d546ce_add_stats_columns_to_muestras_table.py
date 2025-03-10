"""Add stats columns to muestras table

Revision ID: 173d53d546ce
Revises: 8f693bcec5e9
Create Date: 2025-02-11 21:40:07.873791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '173d53d546ce'
down_revision: Union[str, None] = '8f693bcec5e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("muestras", sa.Column("participants_no", sa.Integer, nullable=False, server_default="0"))
    op.add_column("muestras", sa.Column("indices_no", sa.Integer, nullable=False, server_default="0"))
    op.add_column("muestras", sa.Column("ni_no", sa.Integer, nullable=False, server_default="0"))
    op.add_column("muestras", sa.Column("ci_no", sa.Integer, nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("...", "...")

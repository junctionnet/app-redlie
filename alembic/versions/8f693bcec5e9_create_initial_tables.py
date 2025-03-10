from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '8f693bcec5e9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('username', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(100), nullable=False, unique=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('last_login_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Create muestras table (uploaded files)
    op.create_table(
        'muestras',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('uploaded_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Create participantes table
    op.create_table(
        'participantes',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('muestra_id', sa.String(255), sa.ForeignKey('muestras.id', ondelete='CASCADE'), nullable=False),
        sa.Column('posicion', sa.Integer, nullable=False),
        sa.Column('ni', sa.Integer, nullable=False),
        sa.Column('ci', sa.Integer, nullable=False),
        sa.Column('edad', sa.Integer, nullable=False),
        sa.Column('sexo', sa.Integer, nullable=False),
    )

    # Create vocablos table
    op.create_table(
        'vocablos',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('participante_id', sa.String(255), sa.ForeignKey('participantes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vocablo', sa.String(255), nullable=False),
        sa.Column('posicion', sa.Integer, nullable=False),
    )

    op.create_table(
        'indice_disponibilidad',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('muestra_id', sa.String(255), sa.ForeignKey('muestras.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ci', sa.Integer, nullable=False),
        sa.Column('sexo', sa.String(55), nullable=False),
        sa.Column('vocablo', sa.String(255), nullable=False),
        sa.Column('indice', sa.String(255), nullable=False)
    )

def downgrade():
    op.drop_table('indice_disponibilidad')
    op.drop_table('vocablos')
    op.drop_table('participantes')
    op.drop_table('muestras')
    op.drop_table('users')

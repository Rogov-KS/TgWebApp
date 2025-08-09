"""rm useless tabels - try2

Revision ID: 656bb7b8596a
Revises: e8bb634e6431
Create Date: 2025-08-09 14:19:53.309083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '656bb7b8596a'
down_revision: Union[str, Sequence[str], None] = 'e8bb634e6431'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

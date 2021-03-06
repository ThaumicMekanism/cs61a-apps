"""unified instance across courses

Revision ID: 1535e0a43842
Revises: 7141eb5952ee
Create Date: 2020-03-07 22:00:55.601998

"""

# revision identifiers, used by Alembic.
revision = "1535e0a43842"
down_revision = "7141eb5952ee"

from alembic import op
import sqlalchemy as sa
import oh_queue.models
from oh_queue.models import *


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "assignment", sa.Column("course", sa.String(length=255), nullable=False)
    )
    op.add_column(
        "config_entries", sa.Column("course", sa.String(length=255), nullable=False)
    )
    op.add_column(
        "location", sa.Column("course", sa.String(length=255), nullable=False)
    )
    op.add_column("ticket", sa.Column("course", sa.String(length=255), nullable=False))
    op.add_column(
        "ticket_event", sa.Column("course", sa.String(length=255), nullable=False)
    )
    op.add_column("user", sa.Column("course", sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "course")
    op.drop_column("ticket_event", "course")
    op.drop_column("ticket", "course")
    op.drop_column("location", "course")
    op.drop_column("config_entries", "id")
    op.drop_column("config_entries", "course")
    op.drop_column("assignment", "course")
    # ### end Alembic commands ###

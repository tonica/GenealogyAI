"""auditlog_reason_metadata

Afegeix els camps `reason` i `metadata_json` a la taula `audit_logs`
per a la traçabilitat (GEDCOM_IMPORT, MANUAL_EDIT, MERGE...).

Revision ID: a716f69206b5
Revises: 528e42e57fa9
Create Date: 2026-08-03 02:36:48.116450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a716f69206b5'
down_revision = '528e42e57fa9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'audit_logs',
        sa.Column(
            'reason',
            sa.String(length=50),
            nullable=True,
            comment='GEDCOM_IMPORT | MANUAL_EDIT | MERGE | AI_SUGGESTION | NORMALIZATION',
        ),
    )
    op.add_column(
        'audit_logs',
        sa.Column(
            'metadata_json',
            sa.Text(),
            nullable=True,
            comment="Informacio adicional de l'acció (JSON serialitzat)",
        ),
    )


def downgrade() -> None:
    op.drop_column('audit_logs', 'metadata_json')
    op.drop_column('audit_logs', 'reason')
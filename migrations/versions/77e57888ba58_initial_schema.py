from alembic import op
import sqlalchemy as sa

revision = '77e57888ba58'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('avatar', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=200), nullable=False),
    sa.Column('original_filename', sa.String(length=200), nullable=False),
    sa.Column('file_type', sa.String(length=10), nullable=False),
    sa.Column('file_mime', sa.String(length=100), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('file_hash', sa.String(length=64), nullable=True),
    sa.Column('storage_path', sa.String(length=400), nullable=True),
    sa.Column('file_data', sa.LargeBinary(), nullable=True),
    sa.Column('word_count', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('tz_name', sa.String(length=64), nullable=True),
    sa.Column('tz_offset', sa.Integer(), nullable=True),
    sa.Column('is_starred', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_documents_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_documents_file_hash'), ['file_hash'], unique=False)
        batch_op.create_index(batch_op.f('ix_documents_is_starred'), ['is_starred'], unique=False)
        batch_op.create_index(batch_op.f('ix_documents_user_id'), ['user_id'], unique=False)

    op.create_table('reading_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=True),
    sa.Column('filename', sa.String(length=200), nullable=False),
    sa.Column('total_words', sa.Integer(), nullable=False),
    sa.Column('words_read', sa.Integer(), nullable=True),
    sa.Column('speed', sa.Integer(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('tz_name', sa.String(length=64), nullable=True),
    sa.Column('tz_offset', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('reading_sessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reading_sessions_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_reading_sessions_user_id'), ['user_id'], unique=False)

def downgrade():
    with op.batch_alter_table('reading_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reading_sessions_user_id'))
        batch_op.drop_index(batch_op.f('ix_reading_sessions_created_at'))

    op.drop_table('reading_sessions')
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_documents_user_id'))
        batch_op.drop_index(batch_op.f('ix_documents_is_starred'))
        batch_op.drop_index(batch_op.f('ix_documents_file_hash'))
        batch_op.drop_index(batch_op.f('ix_documents_created_at'))

    op.drop_table('documents')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')

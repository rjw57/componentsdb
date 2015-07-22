"""create initial schema

Revision ID: 49e677d8cab
Revises: 
Create Date: 2015-07-20 12:43:53.913625

"""

# revision identifiers, used by Alembic.
revision = '49e677d8cab'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sapg

def upgrade():
    # Create tables
    op.create_table(
        'components',
        sa.Column('id', sa.BigInteger, primary_key=True, unique=True,
            nullable=False),
        sa.Column('code', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('datasheet_url', sa.Text),
        sa.Column('created_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger, primary_key=True, unique=True,
            nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'collections',
        sa.Column('id', sa.BigInteger, primary_key=True, unique=True,
            nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    permission_enum = sapg.ENUM(
        'create', 'read', 'update', 'delete',
        name='permission'
    )

    op.create_table(
        'user_collection_perms',
        sa.Column('id', sa.BigInteger, primary_key=True, unique=True, nullable=False),
        sa.Column('user_id', sa.BigInteger, sa.ForeignKey('users.id'),
            nullable=False),
        sa.Column('collection_id', sa.BigInteger, sa.ForeignKey('collections.id'),
            nullable=False),
        sa.Column('permission', permission_enum, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # If this were anything other than the base migration, this is how you'd
    # backfill rows.
    ## op.execute('UPDATE components SET updated_at=CURRENT_TIMESTAMP;')

    # Add a trigger to automatically update the updated_at column on update.
    op.execute('''
        CREATE FUNCTION update_updated_at_col() RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER update_components_updated_at_trigger
            BEFORE UPDATE ON components
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;

        CREATE TRIGGER update_collections_updated_at_trigger
            BEFORE UPDATE ON collections
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;

        CREATE TRIGGER update_users_updated_at_trigger
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;

        CREATE TRIGGER update_user_collection_perms_updated_at_trigger
            BEFORE UPDATE ON user_collection_perms
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
    ''')

    # Stored functions for some CRUD operations.
    op.execute('''
        -- Creates a collection owned by a user.
        --
        -- Arguments:
        --  user_id: the primary key corresponding to some user
        --  name: the name of the new collection
        --
        -- Returns: the primary key of the new collection
        --
        -- The collection is created with user_id having all -- permissions.
        CREATE FUNCTION
            collection_create(p_user_id bigint, p_name text)
        RETURNS bigint AS $$
        DECLARE
            v_collection_id bigint;
            v_perm permission;
        BEGIN
            -- create the new collection
            INSERT INTO collections (name)
            VALUES      (p_name)
            RETURNING   id INTO v_collection_id;

            -- add permissions
            FOREACH v_perm IN ARRAY enum_range(null::permission) LOOP
                PERFORM collection_add_permission(
                    v_collection_id, p_user_id, v_perm
                );
            END LOOP;

            RETURN v_collection_id;
        END
        $$ LANGUAGE plpgsql;

        -- Adds a permission for a user to a collection.
        --
        -- Arguments:
        --  collection_id: the primary key corresponding to the collection
        --  user_id: the primary key of the user whose permission should be
        --      added.
        --  permission: the permission to add
        --
        -- Returns: the primary key of the new permission.
        CREATE FUNCTION collection_add_permission(
            collection_id bigint, user_id bigint, permission permission
        )
        RETURNS bigint AS $$
            INSERT INTO user_collection_perms
                (collection_id, user_id, permission)
            VALUES ($1, $2, $3)
            RETURNING id;
        $$ LANGUAGE sql;

        -- Removes a permission for a user from a collection.
        --
        -- Arguments:
        --  collection_id: the primary key corresponding to the collection
        --  user_id: the primary key of the user whose permission should be
        --      remove.
        --  permission: the permission to remove
        --
        -- Returns: the number of rows which were deleted.
        CREATE FUNCTION collection_remove_permission(
            collection_id bigint, user_id bigint, permission permission
        )
        RETURNS bigint AS $$
            WITH deleted AS (
                DELETE FROM user_collection_perms
                WHERE
                    collection_id = $1 AND user_id = $2
                    AND permission = $3
                RETURNING *
            ) SELECT count(*) FROM deleted;
        $$ LANGUAGE sql;

        -- Determine if a user has a given permission on a collection.
        --
        -- Arguments:
        --  collection_id: the primary key corresponding to the collection
        --  user_id: the primary key of the user whose permissions should be
        --      examined.
        --  permission: the permission to query
        --
        -- Returns: a boolean indicating if the user has this permission
        CREATE FUNCTION collection_user_has_permission(
            collection_id bigint, user_id bigint, permission permission
        )
        RETURNS boolean AS $$
            SELECT  COUNT(id) > 0
            FROM    user_collection_perms
            WHERE   collection_id = $1 AND user_id = $2 AND permission = $3;
        $$ LANGUAGE sql;
    ''')


def downgrade():
    op.execute('''
        DROP FUNCTION collection_create(bigint, text) CASCADE;

        DROP FUNCTION
            collection_add_permission(bigint, bigint, permission)
        CASCADE;

        DROP FUNCTION
            collection_remove_permission(bigint, bigint, permission)
        CASCADE;

        DROP FUNCTION
            collection_user_has_permission(bigint, bigint, permission)
        CASCADE;
    ''')

    op.execute('DROP FUNCTION update_updated_at_col() CASCADE;')

    op.drop_table('user_collection_perms')
    op.drop_table('users')
    op.drop_table('components')
    op.drop_table('collections')

    op.execute('DROP TYPE permission;')

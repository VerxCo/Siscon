from app.core.security import get_password_hash
from app.db.connection import get_db_connection
from app.models.user import AppUserProfile, User


FAKE_USERS = [
    User(
        id=1,
        nome="Administrador",
        email="admin@admin.com",
        senha_hash=get_password_hash("123456"),
        role="admin",
        ativo=True,
    ),
    User(
        id=2,
        nome="Editor",
        email="editor@admin.com",
        senha_hash=get_password_hash("123456"),
        role="editor",
        ativo=True,
    ),
    User(
        id=3,
        nome="Viewer",
        email="viewer@admin.com",
        senha_hash=get_password_hash("123456"),
        role="viewer",
        ativo=True,
    ),
]


def get_user_by_email(email: str) -> User | None:
    normalized = email.strip().lower()
    for user in FAKE_USERS:
        if user.email.lower() == normalized:
            return user
    return None


def get_app_profile_by_user_id(user_id: str) -> AppUserProfile | None:
    query = '''
        select
            user_id::text,
            email,
            full_name,
            role,
            active
        from public.app_user_profiles
        where user_id = %s
        limit 1
    '''

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()

    if row is None:
        return None

    return AppUserProfile(
        user_id=row[0],
        email=row[1],
        full_name=row[2],
        role=row[3],
        active=row[4],
    )

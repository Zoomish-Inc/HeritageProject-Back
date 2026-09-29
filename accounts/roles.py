import os

from django.contrib.auth.models import Group, Permission, User

GROUP_EDITOR = 'Editor'
GROUP_PUBLISHER = 'Publisher'
GROUP_TOUR_ONLY = 'TourOnly'
GROUP_VIEWER = 'Viewer'

ROLE_GROUPS = (
    GROUP_EDITOR,
    GROUP_PUBLISHER,
    GROUP_TOUR_ONLY,
    GROUP_VIEWER,
)

ROLE_USERS = (
    {
        'username': 'editor',
        'group': GROUP_EDITOR,
        'password_env': 'ROLE_EDITOR_PASSWORD',
        'default_password': 'EditorHeritage2026!',
        'email': 'editor@heritage.local',
    },
    {
        'username': 'publisher',
        'group': GROUP_PUBLISHER,
        'password_env': 'ROLE_PUBLISHER_PASSWORD',
        'default_password': 'PublisherHeritage2026!',
        'email': 'publisher@heritage.local',
    },
    {
        'username': 'tour_only',
        'group': GROUP_TOUR_ONLY,
        'password_env': 'ROLE_TOUR_ONLY_PASSWORD',
        'default_password': 'TourHeritage2026!',
        'email': 'tour@heritage.local',
    },
    {
        'username': 'viewer',
        'group': GROUP_VIEWER,
        'password_env': 'ROLE_VIEWER_PASSWORD',
        'default_password': 'ViewerHeritage2026!',
        'email': 'viewer@heritage.local',
    },
)

HERITAGE_OBJECT = ('heritage', 'heritageobject')

NESTED_MODELS = (
    ('heritage', 'architecturedetail'),
    ('heritage', 'beforeafterpair'),
    ('heritage', 'historicalfigure'),
    ('heritage', 'photoitem'),
    ('heritage', 'audioguide'),
    ('heritage', 'audioguidetrack'),
    ('heritage', 'architectbio'),
    ('heritage', 'biographymilestone'),
)

VIEW_ONLY_MODELS = (HERITAGE_OBJECT,) + NESTED_MODELS


def user_in_group(user, group_name):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return group_name == GROUP_PUBLISHER
    return user.groups.filter(name=group_name).exists()


def is_publisher(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=GROUP_PUBLISHER).exists()


def is_editor(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=GROUP_EDITOR).exists()


def is_tour_only(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return False
    return user.groups.filter(name=GROUP_TOUR_ONLY).exists()


def is_viewer_only(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or is_publisher(user) or is_editor(user) or is_tour_only(user):
        return False
    return user.groups.filter(name=GROUP_VIEWER).exists()


def can_edit_content(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return is_publisher(user) or is_editor(user)


def can_edit_publish(user):
    return is_publisher(user)


def can_edit_tour(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return is_publisher(user) or is_tour_only(user)


def can_add_heritage_object(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return False


def can_delete_heritage_object(user):
    return can_add_heritage_object(user)


def can_mutate_inlines(user):
    return can_edit_content(user)


def _perms_for_model(app_label, model, actions):
    perms = []
    for action in actions:
        codename = f'{action}_{model}'
        try:
            perms.append(
                Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename,
                )
            )
        except Permission.DoesNotExist:
            continue
    return perms


def build_role_permissions():
    viewer = []
    for app_label, model in VIEW_ONLY_MODELS:
        viewer.extend(_perms_for_model(app_label, model, ('view',)))

    editor = list(viewer)
    editor.extend(_perms_for_model(*HERITAGE_OBJECT, ('change',)))
    for app_label, model in NESTED_MODELS:
        editor.extend(_perms_for_model(app_label, model, ('add', 'change', 'delete')))

    tour_only = list(viewer)
    tour_only.extend(_perms_for_model(*HERITAGE_OBJECT, ('change',)))

    publisher = list(editor)

    return {
        GROUP_VIEWER: viewer,
        GROUP_EDITOR: editor,
        GROUP_TOUR_ONLY: tour_only,
        GROUP_PUBLISHER: publisher,
    }


def setup_admin_roles():
    role_perms = build_role_permissions()
    created_groups = []
    for name in ROLE_GROUPS:
        group, created = Group.objects.get_or_create(name=name)
        group.permissions.set(role_perms[name])
        if created:
            created_groups.append(name)
    return {
        'created': created_groups,
        'updated': [name for name in ROLE_GROUPS if name not in created_groups],
    }


def ensure_role_users():
    """Create/update staff users for each role. Password from env or default."""
    setup_admin_roles()
    results = []
    for spec in ROLE_USERS:
        password = os.getenv(spec['password_env'], '').strip() or spec['default_password']
        group = Group.objects.get(name=spec['group'])
        user, created = User.objects.get_or_create(
            username=spec['username'],
            defaults={
                'email': spec['email'],
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
            },
        )
        user.email = spec['email']
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.set_password(password)
        user.save()
        user.groups.set([group])
        results.append({
            'username': user.username,
            'group': spec['group'],
            'created': created,
        })
    return results

from django.contrib.auth.models import Group, User
from django.test import TestCase

from accounts.roles import (
    GROUP_EDITOR,
    GROUP_PUBLISHER,
    GROUP_TOUR_ONLY,
    GROUP_VIEWER,
    can_edit_content,
    can_edit_publish,
    can_edit_tour,
    can_mutate_inlines,
    ensure_role_users,
    setup_admin_roles,
)


class AdminRolesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        setup_admin_roles()

    def _user(self, username, group_name):
        user = User.objects.create_user(username=username, password='x', is_staff=True)
        user.groups.add(Group.objects.get(name=group_name))
        return user

    def test_setup_creates_groups(self):
        for name in (GROUP_EDITOR, GROUP_PUBLISHER, GROUP_TOUR_ONLY, GROUP_VIEWER):
            self.assertTrue(Group.objects.filter(name=name).exists())

    def test_editor_matrix(self):
        user = self._user('u_editor', GROUP_EDITOR)
        self.assertTrue(can_edit_content(user))
        self.assertTrue(can_mutate_inlines(user))
        self.assertFalse(can_edit_publish(user))
        self.assertFalse(can_edit_tour(user))

    def test_tour_only_matrix(self):
        user = self._user('u_tour', GROUP_TOUR_ONLY)
        self.assertFalse(can_edit_content(user))
        self.assertFalse(can_mutate_inlines(user))
        self.assertFalse(can_edit_publish(user))
        self.assertTrue(can_edit_tour(user))

    def test_publisher_matrix(self):
        user = self._user('u_publisher', GROUP_PUBLISHER)
        self.assertTrue(can_edit_content(user))
        self.assertTrue(can_edit_publish(user))
        self.assertTrue(can_edit_tour(user))

    def test_viewer_matrix(self):
        user = self._user('u_viewer', GROUP_VIEWER)
        self.assertFalse(can_edit_content(user))
        self.assertFalse(can_edit_publish(user))
        self.assertFalse(can_edit_tour(user))
        self.assertFalse(can_mutate_inlines(user))

    def test_union_editor_and_tour_only(self):
        user = self._user('u_both', GROUP_EDITOR)
        user.groups.add(Group.objects.get(name=GROUP_TOUR_ONLY))
        self.assertTrue(can_edit_content(user))
        self.assertTrue(can_edit_tour(user))
        self.assertFalse(can_edit_publish(user))

    def test_ensure_role_users_creates_staff(self):
        ensure_role_users()
        passwords = {
            'editor': 'EditorHeritage2026!',
            'publisher': 'PublisherHeritage2026!',
            'tour_only': 'TourHeritage2026!',
            'viewer': 'ViewerHeritage2026!',
        }
        for username, group_name in (
            ('editor', GROUP_EDITOR),
            ('publisher', GROUP_PUBLISHER),
            ('tour_only', GROUP_TOUR_ONLY),
            ('viewer', GROUP_VIEWER),
        ):
            user = User.objects.get(username=username)
            self.assertTrue(user.is_staff)
            self.assertFalse(user.is_superuser)
            self.assertTrue(user.groups.filter(name=group_name).exists())
            self.assertTrue(user.check_password(passwords[username]))

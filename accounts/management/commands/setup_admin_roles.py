from django.core.management.base import BaseCommand

from accounts.roles import ROLE_GROUPS, ensure_role_users, setup_admin_roles


class Command(BaseCommand):
    help = 'Create/update Admin role groups and staff users (Editor, Publisher, TourOnly, Viewer).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            action='store_true',
            default=True,
            help='Also create/update role users from env passwords (default: on).',
        )
        parser.add_argument(
            '--no-users',
            action='store_true',
            help='Only sync groups, do not create users.',
        )

    def handle(self, *args, **options):
        if options.get('no_users'):
            result = setup_admin_roles()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Roles ready. created={result['created'] or '-'} "
                    f"updated={result['updated'] or '-'}"
                )
            )
            self.stdout.write('Groups: ' + ', '.join(ROLE_GROUPS))
            return

        users = ensure_role_users()
        self.stdout.write(self.style.SUCCESS('Roles + users ready.'))
        for row in users:
            state = 'created' if row['created'] else 'updated'
            self.stdout.write(f"  {row['username']} [{row['group']}] {state}")

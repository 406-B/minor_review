from django.core.management.base import BaseCommand

from login.models import User
from utils.jwt import encrypt_password


class Command(BaseCommand):
    help = "Create/update a load test user for k6 scripts (login/register)."

    def add_arguments(self, parser):
        parser.add_argument('--username', default='Perf01', help='Username to create/update')
        parser.add_argument('--password', default='Aa1-aaaa', help='Plaintext password (will be encrypted)')
        parser.add_argument('--nickname', default='性能压测', help='Nickname to set')
        parser.add_argument(
            '--reset-password',
            action='store_true',
            help='If set, always overwrite the stored password',
        )

    def handle(self, *args, **options):
        username = (options.get('username') or '').strip()
        password_plain = options.get('password') or ''
        nickname = (options.get('nickname') or username).strip()
        reset = bool(options.get('reset_password'))

        if not username:
            raise SystemExit('username is required')

        password_enc = encrypt_password(password_plain)

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'password': password_enc,
                'nickname': nickname,
            },
        )

        changed = False
        if created:
            changed = True
        else:
            updates = {}
            if reset and user.password != password_enc:
                updates['password'] = password_enc
            if nickname and user.nickname != nickname:
                updates['nickname'] = nickname

            if updates:
                for k, v in updates.items():
                    setattr(user, k, v)
                user.save(update_fields=list(updates.keys()))
                changed = True

        self.stdout.write(
            self.style.SUCCESS(
                f"loadtest user: username={user.username} id={user.id} created={created} changed={changed}"
            )
        )

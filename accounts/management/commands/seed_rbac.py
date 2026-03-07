from django.core.management.base import BaseCommand
from accounts.models import Permission, Role


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        permissions = [
            ("Create Agent", "create_agent"),
            ("Update Agent", "update_agent"),
            ("Delete Agent", "delete_agent"),
            ("View Agent", "view_agent"),
            ("Execute Workflow", "execute_workflow"),
            ("View Logs", "view_logs"),
            ("Manage Users", "manage_users"),
            ("Manage Roles", "manage_roles"),
        ]

        perm_objs = {}

        # Create permissions
        for name, code in permissions:
            perm, _ = Permission.objects.get_or_create(
                code=code,
                defaults={"name": name}
            )
            perm_objs[code] = perm

        # --------------------
        # Admin Role
        # --------------------

        admin_role, _ = Role.objects.get_or_create(name="Admin")
        admin_role.permissions.set(perm_objs.values())

        # --------------------
        # User Role
        # --------------------

        user_role, _ = Role.objects.get_or_create(name="User")
        user_role.permissions.set([
            perm_objs["create_agent"],
            perm_objs["update_agent"],
            perm_objs["delete_agent"],
            perm_objs["view_agent"],
            perm_objs["execute_workflow"],
        ])

        # --------------------
        # Operator Role
        # --------------------

        operator_role, _ = Role.objects.get_or_create(name="Operator")
        operator_role.permissions.set([
            perm_objs["view_agent"],
            perm_objs["execute_workflow"],
            perm_objs["view_logs"],
        ])

        # --------------------
        # Viewer Role
        # --------------------

        viewer_role, _ = Role.objects.get_or_create(name="Viewer")
        viewer_role.permissions.set([
            perm_objs["view_agent"],
            perm_objs["view_logs"],
        ])

        self.stdout.write(self.style.SUCCESS("RBAC roles seeded successfully"))
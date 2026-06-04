# Django modules
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# Project modules
from apps.users.models import CustomUser


@register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for the CustomUser model."""

    list_display = (
        "email",
        "full_name",
        "is_active",
        "is_staff",
    )
    search_fields = ("email", "full_name")
    list_filter = ("is_active", "is_staff")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name", "avatar")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password",
                    "full_name",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

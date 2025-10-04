from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Product,Order, CustomUser


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock")
    search_fields =("name", )
    list_filter = ("price", )



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id" , "user", "product", "amount", "is_paid", "created_at")
    search_fields = ("user__username", "product__name")
    list_filter = ("is_paid", "created_at")
    


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name")
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )

    ordering = ("email",)
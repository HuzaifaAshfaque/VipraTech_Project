from django.urls import path
from .views import signup, login, logout, ProductListView, checkout_view, success, cancel, CreatePaymentView ,StripeWebhookView

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path('', ProductListView.as_view(), name="product_list"),
    path("checkout/<int:product_id>/", checkout_view, name="checkout"),


    path("create-payment/<int:product_id>/", CreatePaymentView.as_view(), name="create_payment"),
    path("stripe-webhook/", StripeWebhookView.as_view(), name="stripe_webhook"),
        path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),

]
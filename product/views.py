from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from product.models import Product, Order, CustomUser
import stripe
from decouple import config
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password

from django.db.models import Prefetch

# Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

# ----------------- AUTH VIEWS -----------------

def signup(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # iterating clears old messages


    if request.method == "POST":
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")

        CustomUser.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password)
        )
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "product/signup.html")


def login(request):
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                request.session["user_id"] = user.id
                request.session["user_email"] = user.email
                messages.success(request, "Login successful!")
                return redirect("product_list")
            else:
                messages.error(request, "Incorrect password")
        except CustomUser.DoesNotExist:
            messages.error(request, "Email not registered")

    return render(request, "product/login.html")


def logout(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # iterating clears old messages

    
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect("login")


# ----------------- HELPER -----------------

def login_required_session(view_func):
    """Decorator to check session-based login"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            messages.warning(request, "You must login first")
            return redirect(f"{reverse('login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper


# ----------------- PRODUCT VIEWS -----------------

from django.db.models import Prefetch

class ProductListView(View):
    def get(self, request):
        user_id = request.session.get("user_id")

        if user_id:
            user = CustomUser.objects.get(id=user_id)
            # Get all paid orders of the user, latest first
            paid_orders = Order.objects.filter(user=user, is_paid=True).order_by('-id')
            total_paid = sum(order.amount for order in paid_orders)  # calculate in Python

        else:
            paid_orders = []
            total_paid = 0

        # Get all products for display
        products = Product.objects.all().order_by('id')

        return render(request, "product/product_list.html", {
            "total_paid" : total_paid,
            "products": products,
            "paid_orders": paid_orders,  # pass orders in sequence
        })



@login_required_session
def checkout_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product/checkout.html", {"product": product})



def success(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # iterating clears old messages

    
    messages.success(request, "Payment successful!")
    return redirect(reverse("product_list"))


def cancel(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # iterating clears old messages

    
    messages.warning(request, "Payment cancelled!")
    return redirect(reverse("product_list"))


# ----------------- STRIPE PAYMENT -----------------

@method_decorator(csrf_exempt, name="dispatch")
class CreatePaymentView(View):
    
    def post(self, request, product_id):
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # iterating clears old messages

        
        if not request.session.get("user_id"):
            messages.warning(request, "You must login first")
            return redirect(f"{reverse('login')}?next={request.path}")

        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get("quantity", 1))

        if quantity > product.stock:
            messages.error(request, f"Requested quantity exceeds available stock ({product.stock})")
            return redirect("checkout", product_id=product.id)

        try:
            user = CustomUser.objects.get(id=request.session["user_id"])

            checkout_session = stripe.checkout.Session.create(
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(product.price * 100),
                        "product_data": {"name": product.name}
                    },
                    "quantity": quantity
                }],
                mode="payment",
                customer_email=user.email,
                success_url=f'{config("YOUR_DOMAIN")}{reverse("success")}',
                cancel_url=f'{config("YOUR_DOMAIN")}{reverse("cancel")}',
            )

            # Create Order
            Order.objects.create(
                user=user,
                product=product,
                amount=product.price * quantity,
                quantity=quantity,
                stripe_checkout_session_id=checkout_session.id
            )

            return redirect(checkout_session.url)

        except Exception as e:
            messages.error(request, str(e))
            return redirect("checkout", product_id=product.id)


# ----------------- STRIPE WEBHOOK -----------------

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return JsonResponse({"error": f"Invalid payload: {str(e)}"}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({"error": f"Invalid signature: {str(e)}"}, status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            try:
                order = Order.objects.get(stripe_checkout_session_id=session["id"])
                if not order.is_paid:  # ensure idempotency
                    order.is_paid = True
                    order.save()

                    # Reduce stock here
                    product = order.product
                    product.stock = max(product.stock - order.quantity, 0)
                    product.save()
            except Order.DoesNotExist:
                print(f"Order not found for session {session['id']}")

        return JsonResponse({"status": "success"})

# Django Stripe Checkout Project

## Project Overview
This project is a simple e-commerce system built with Django. 
Users can browse products, 
purchase them via Stripe Checkout, 
and see their paid orders in the dashboard. 
Stock is updated only after successful payment.

---

## Assumptions
- Users must be logged in to make purchases.
- Stock is limited; users cannot purchase more than available quantity.
- Orders are considered paid **only after Stripe webhook confirmation**.
- Each product purchase generates a separate order.

---

## Payment Flow Chosen
- **Stripe Checkout Session**
  - Simple and secure for one-time payments.
  - Handles email receipts and session management automatically.
  - Protects against double charges or multiple submissions.

---

## Avoiding Double Charge / Inconsistent State
- Orders are **created after Succes response from Stripe**.
- Stock is **reduced only after Stripe confirms payment via webhook**.
- Webhook ensures **idempotency**, preventing repeated processing of the same session.

---


## Setup / Run Instructions (Docker)

1. Clone the repository:
   git clone "https://github.com/HuzaifaAshfaque/VipraTech_Project.git"
   cd VipraTech_Project


2. Create a .env file based on .env.example and fill in your keys.

3. **Make the entrypoint executable**:  
   ```bash
   chmod +x entrypoint.sh

4. Build and run the containers:
    docker-compose up -d --build or docker compose up -d --build (for debian)

5. Apply migrations:
    docker-compose exec django python manage.py migrate or docker compose exec django python manage.py migrate (for debian)

6. Create superuser:
    docker-compose exec web python manage.py createsuperuser or docker compose exec web python manage.py createsuperuser (for debian)
    email:-  admin@gmail.com
    password:- admin

7. Access the app in your browser:
    http://localhost:8000/

8. Add Products
    Go to Admin Panel and add some products



## Notes on Code Quality & Logic

- Views are mostly **class-based** (`View`) for main pages like product listing and Stripe payment.
- Session-based login checks are handled via a **custom decorator** (`login_required_session`).
- **Signup, login, and logout** use session-based authentication and password hashing for security.
- Stripe **checkout session creation** and **webhook handling** are separated for clarity and idempotency.
- The webhook ensures that:
  - Orders are marked as paid **only once**.
  - Product stock is reduced **only after successful payment**.
- Django **messages framework** is used for user feedback (success, error, warnings), displayed via **Bootstrap toasters**.
- **Paid orders** are displayed in purchase sequence order, with the latest orders shown first.
- Stock updates and total amounts are handled **server-side** to prevent client-side manipulation.



## AI Tools Used

- **ChatGPT**: Assisted in optimizing Django queries (`prefetch_related`) and fixing stripe webhook logic.
               ChatGPT also helped draft this `README.md`.

- **Claude**: After completing the project, assisted in enhancing frontend templates, as it provides strong recommendations for UI/UX 
              improvements compared to ChatGPT.


## Time Spent

- **Total hours** : 8 - 10 hours.
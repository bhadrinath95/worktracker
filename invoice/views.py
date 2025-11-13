from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Customer
import random
from datetime import date

@login_required(login_url='login')
def invoice_form(request):
    customers = Customer.objects.all()

    if request.method == "POST":
        company = {
            "name": "Bhadrinath Consultancy and Services (BCS)",
            "address": "#14, Third Cross North, Suriya Gandhi Nagar, Muthialpet, Puducherry - 605003",
            "phone": "7200948401",
            "email": "bhadrinath95@gmail.com"
        }

        invoice_number = random.randint(100000, 999999)
        items = []
        customer_id = request.POST.get("customer_id")
        selected_customer = Customer.objects.filter(id=customer_id).first()

        customer = {
            "name": selected_customer.name if selected_customer else "",
            "address": selected_customer.address if selected_customer else "",
            "phone": selected_customer.phone if selected_customer else "",
            "email": selected_customer.email if selected_customer else "",
        }

        descriptions = request.POST.getlist("description")
        quantities = request.POST.getlist("quantity")
        prices = request.POST.getlist("price")
        qty_totals = request.POST.getlist("qty_totals")
        overall_total = request.POST.get("overall_total")
        amount_received = request.POST.get("amount_received", None)
        balance = request.POST.get("balance", None)
        unit = request.POST.get("unit", "")
        date_today = date.today().strftime("%d-%m-%Y")

        for desc, qty, price, line_total in zip(descriptions, quantities, prices, qty_totals):
            if desc:
                items.append({
                    "description": desc,
                    "quantity": qty,
                    "price": f"{unit} {price}",
                    "line_total": f"{unit} {line_total}"
                })

        return render(request, "invoice/invoice_result.html", {
            "customer": customer,
            "company": company,
            "invoice_number": invoice_number,
            "items": items,
            "overall_total": f"{unit} {overall_total}",
            "amount_received": f"{unit} {amount_received}" if amount_received else amount_received,
            "balance": f"{unit} {balance}" if balance else balance,
            "date_today": date_today,
        })

    return render(request, "invoice/invoice_form.html", {"customers": customers})

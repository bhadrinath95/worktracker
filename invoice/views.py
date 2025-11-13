from django.shortcuts import render
import random
from datetime import date

def invoice_form(request):
    if request.method == "POST":
        company = {
            "name": "Bhadrinath Consultancy and Services (BCS)",
            "address": "#14, Third Cross North, Suriya Gandhi Nagar, Muthialpet, Puducherry - 605003",
            "phone": "7200948401",
            "email": "bhadrinath95@gmail.com"
        }
        invoice_number = random.randint(100000, 999999)
        items = []
        total = 0

        # Parse dynamic items
        descriptions = request.POST.getlist("description")
        quantities = request.POST.getlist("quantity")
        prices = request.POST.getlist("price")
        qty_totals = request.POST.getlist("qty_totals")
        overall_total = request.POST.get("overall_total")
        amount_received = request.POST.get("amount_received", "")
        balance = request.POST.get("balance", "")
        unit = request.POST.get("unit", "")
        date_today = date.today()
        formatted_date = date_today.strftime("%d-%m-%Y")


        for desc, qty, price, line_total in zip(descriptions, quantities, prices, qty_totals):
            if desc:
                items.append({"description": desc, "quantity": qty, "price": f"{unit} {price}", "line_total": f"{unit} {line_total}"})

        return render(request, "invoice/invoice_result.html", {
            "company": company,
            "invoice_number": invoice_number,
            "items": items,
            "overall_total": f"{unit} {overall_total}",
            "amount_received": f"{unit} {amount_received}",
            "balance": f"{unit} {balance}",
            "date_today": formatted_date,
        })
    return render(request, "invoice/invoice_form.html")

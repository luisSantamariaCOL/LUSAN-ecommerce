from django.shortcuts import render, redirect, get_object_or_404
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order


def payments(request):
    return render(request, 'orders/payments.html')

def place_order(request,  total = 0, quantity = 0):
    current_user = request.user

    # if cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    iva = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

        iva = round(0.19 * total, 2)
        grand_total = round(total + iva, 2)


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            # Store all the billing information inside Order Table
            data = Order()
            data.first_name     = form.cleaned_data['first_name']
            data.last_name      = form.cleaned_data['last_name']
            data.phone          = form.cleaned_data['phone']
            data.email          = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country        = form.cleaned_data['country']
            data.state          = form.cleaned_data['state']
            data.city           = form.cleaned_data['city']
            data.order_note     = form.cleaned_data['order_note']
            data.order_total    = grand_total
            data.tax            = iva
            data.ip = request.META.get('REMOTE_ADDR') # gives user's IP
            data.save()
            # Generate order number
            year = int(datetime.date.today().strftime('%Y'))
            month = int(datetime.date.today().strftime('%m'))
            day = int(datetime.date.today().strftime('%d'))
            d = datetime.date(year, month, day)
            current_date = d.strftime("%Y%m%d")
            data.order_number = current_date + str(data.id) # 2023112101
            data.save()

            return redirect('checkout')
        else: print(form.errors)
    else:
        return redirect('checkout')

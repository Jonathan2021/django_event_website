from django.shortcuts import render, HttpResponse, redirect, \
    get_object_or_404, reverse
from django.contrib import messages
from .models import Product, Order, LineItem
from .forms import CartForm, CheckoutForm
from . import cart
from event import views
from event import models
from django.db.models import ProtectedError
from django.db import models as models_email
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import qrcode
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import EmailMessage
from django.core import mail
from django.core.mail import get_connection
from django.core.mail import send_mail
from django.core.mail import EmailMessage

# Create your views here.
    
def index_shop(request):
    all_products = Product.objects.all()
    users = User.objects.all()
    user_type = "E"

    for user in users:
        at_pos = user.email.find("@")
        start_email = user.email[:at_pos]
        end_email = user.email[at_pos:]
       
        if start_email == str(request.user) and end_email[:9] == "@epita.fr":
            user_type = "I"         
        
        
    for event in views.EventListView.get_queryset(request):
        my_price = 0
        all_price = event.prices.all()
        try:
            my_price = all_price.get(ticket_type=user_type).price
        except models.Price.DoesNotExist:        
            my_price = 0

        try:
            product = all_products.get(id=event.id)
            product.price = my_price
            product.save()
        except Product.DoesNotExist:        
            product = Product(name = event.title,price = my_price,id = event.id)
            product.save()

    
    for product in all_products:
        try:
            event = views.EventListView.get_queryset(request).get(id=product.id)
        except models.Event.DoesNotExist:
            remove_product(request, product.id)

    
    all_products = Product.objects.all()
    return render(request, "index_shop.html", {
                                    'all_products': all_products,
                                    })


def send_mail_ticket(request):
    email = EmailMessage()
    email.subject = 'Ticket'
    email.body = 'Thanks for buying a ticket'
    email.to = ['romain.chuit@epita.fr']
    #email.attach_file("/home/romain/Downloads/clement.davin.jpeg")
    email.connection = get_connection()
    return email.send()

def show_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    event_prices = views.EventListView.get_queryset(request).get(id=product.id).prices.all()
    
    all_tickets = models.Ticket.objects.filter(event_id=product_id)
    external_left = 0
    internal_left = 0
    staff_left = 0
    for ticket in all_tickets:
        try:
            ticket.purchase
        except models.Purchase.DoesNotExist:
            if ticket.ticket_type == models.Ticket.EXTERN:
                external_left += 1
            if ticket.ticket_type == models.Ticket.INTERN:
                internal_left += 1
            if ticket.ticket_type == models.Ticket.STAFF:
                staff_left += 1

    ext = "Extern"
    inter = "Intern"
    staff = "Staff"

    if external_left == 0:
        ext = ""
    if internal_left == 0:
        inter = ""
    if staff_left == 0:
        ext = ""

    if request.method == 'POST':
        form = CartForm(request, request.POST, product_id)
        if form.is_valid():
            request.form_data = form.cleaned_data
            cart.add_item_to_cart(request)
            return redirect('show_cart')

    form = CartForm(request, initial={'product_id': product.id})
    return render(request, 'product_detail.html', {
                                            'product': product,
                                            'form': form,
                                            'prices':event_prices,
                                            'ext' : ext,
                                            'int' : inter,
                                            'staff' : staff
                                            })

 
def remove_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        product.delete()  
    except ProtectedError:
        error_message = "This object can't be deleted!!\n\n\n"

def show_cart(request):
    if request.method == 'POST':
        if request.POST.get('submit') == 'Update':
            cart.update_item(request)
        if request.POST.get('submit') == 'Remove':
            cart.remove_item(request)

    cart_items = cart.get_all_cart_items(request)
    cart_subtotal = cart.subtotal(request)
    return render(request, 'cart.html', {
                                            'cart_items': cart_items,
                                            'cart_subtotal': cart_subtotal,
                                            })


def checkout(request):
    price = cart.subtotal(request)
    #cart.qrcode(request)
    return render(request, 'checkout.html', {'price': price})

def info(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            o = Order(
                name = cleaned_data.get('name'),
                email = cleaned_data.get('email'),
                postal_code = cleaned_data.get('postal_code'),
                address = cleaned_data.get('address'),
            )
            o.save()

            all_items = cart.get_all_cart_items(request)
            for cart_item in all_items:
                li = LineItem(
                    product_id = cart_item.product_id,
                    price = cart_item.price,
                    quantity = cart_item.quantity,
                    order_id = o.id
                )

                li.save()

            cart.clear(request)

            request.session['order_id'] = o.id

            messages.add_message(request, messages.INFO, 'Order Placed!')
            return redirect('info')


    else:
        form = CheckoutForm()
        return render(request, 'info_checkout.html', {'form': form})

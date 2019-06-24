from .models import CartItem, Product
from django.shortcuts import get_object_or_404, get_list_or_404
from event import views
from event import models
import qrcode

def _cart_id(request):
    if 'cart_id' not in request.session:
        request.session['cart_id'] = _generate_cart_id()

    return request.session['cart_id']


def _generate_cart_id():
    import string, random
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(50)])


def get_all_cart_items(request):
    return CartItem.objects.filter(cart_id = _cart_id(request))


def add_item_to_cart(request):
    # cart_id = _cart_id(request)
    product_id = request.form_data['product_id']
    quantity = request.form_data['quantity']

    p = get_object_or_404(Product, id=product_id)

    type_chosen = request.form_data['price']
    price = 0
    fail = False
    if type_chosen == "0":
        try:
            price = views.EventListView.get_queryset(request).get(id=product_id).Prices.get(ticket_type="I").price
        except models.Price.DoesNotExist:
            fail = True
    if type_chosen == "1":
        try:
            price = views.EventListView.get_queryset(request).get(id=product_id).Prices.get(ticket_type="E").price
        except models.Price.DoesNotExist:
            fail = True
    if type_chosen == "2":
        try:
            price = views.EventListView.get_queryset(request).get(id=product_id).Prices.get(ticket_type="S").price
        except models.Price.DoesNotExist:
            fail = True

    if fail:
        return

    cart_items = get_all_cart_items(request)

    item_in_cart = False

    for cart_item in cart_items:
        if cart_item.product_id == product_id and cart_item.price == price:
            cart_item.update_quantity(quantity)
            # cart_item.save()
            item_in_cart = True

    if not item_in_cart:
        item = CartItem(
            cart_id = _cart_id(request),
            price = price,
            quantity = quantity,
            product_id = product_id,
        )

        # item.cart_id = cart_id
        item.save()


def item_count(request):
    return get_all_cart_items(request).count()


def subtotal(request):
    cart_item = get_all_cart_items(request)
    sub_total = 0
    for item in cart_item:
        sub_total += item.total_cost()

    return sub_total


def remove_item(request):
    item_id = request.POST.get('item_id')
    ci = get_object_or_404(CartItem, id=item_id)
    ci.delete()


def update_item(request):
    item_id = request.POST.get('item_id')
    quantity = request.POST.get('quantity')
    ci = get_object_or_404(CartItem, id=item_id)
    if quantity.isdigit():
        quantity = int(quantity)
        ci.quantity = quantity
        ci.save()


def clear(request):
    cart_items = get_all_cart_items(request)
    cart_items.delete()

def qrcode(request):                                                            
    qrc = qrcode.QRCode(box_size=8,border=0)                                    
    qrc.add_data(request.user)                                                  
    qrc.make()                                                                  
    qrc.save('qrcode/{}.png'.format(request.user), 'PNG')                       
    return render(request,'index.html')

from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
 
# This is a utility function to get or create a unique cart_id in the user's session. 
# It helps to track the user's cart without them needing to be logged in.
def _cart_id(request):

    # Check if the session has a session key already, if not, create a new one
    if not request.session.session_key:
        request.session.create()

    return request.session.session_key

# This view function adds items to the cart.
def add_cart(request, product_id):

    current_user = request.user

    # Retrieve the product instance with the given product_id
    product = get_object_or_404(Product, id=product_id)

    # If the user is authenticated
    if current_user.is_authenticated:
        # Retrieve any variations of the product (like size or color)
        product_variation = _get_product_variations_from_request(request, product) 


        # Check if there are any CartItem instances with this product and the current user
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists

        # If the CartItem already exists, update or create new variations as necessary
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            # This will hold the current variations and IDs for cart items
            ex_var_list = []
            id_list = []

            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id_list.append(item.id)

            # If the current variations already exist in the cart, increase quantity
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                # If not, create a new CartItem with the new variations
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear() # Clear any existing variations from the newly created CartItem
                    item.variations.add(*product_variation) # Add the new variations to the CartItem's many-to-many field for variations
                item.save()

        else:
            # If no CartItem exists, create a new CartItem instance with the given product and variations
            cart_item = CartItem.objects.create(product = product, quantity = 1, user = current_user)
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()

        # Redirect the user to the cart page
        return redirect('cart')

    # If the user is not authenticated
    else:

        # Retrieve any variations of the product (like size or color)
        product_variation = _get_product_variations_from_request(request, product) 

        # Try to get the Cart object for the current session, or create a new one if it doesn't exist
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        # Check if there are any CartItem instances with this product and cart
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists

        # If the CartItem already exists, update or create new variations as necessary
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            # This will hold the current variations and IDs for cart items
            ex_var_list = []
            id_list = []

            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id_list.append(item.id)

            # If the current variations already exist in the cart, increase quantity
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                # If not, create a new CartItem with the new variations
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear() # Clear any existing variations from the newly created CartItem
                    item.variations.add(*product_variation) # Add the new variations to the CartItem's many-to-many field for variations
                item.save()

        else:
            # If no CartItem exists, create a new CartItem instance with the given product and variations
            cart_item = CartItem.objects.create(product = product, quantity = 1, cart = cart)
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()

        # Redirect the user to the cart page
        return redirect('cart')

def _get_product_variations_from_request(request, product):
    """
    Extracts and returns product variations from a POST request.

    This function iterates through the submitted POST data to identify product variations
    (like size, color, etc.) associated with a specific product. It performs a case-insensitive
    match for each variation category and value against the submitted data. Only the first
    matching variation is considered. The function collects all matching variations and returns them.

    Parameters:
    - request (HttpRequest): The HttpRequest object containing POST data with potential product variations.
    - product (Product): The Product object for which variations are being searched.

    Returns:
    - list: A list of Variation objects that were submitted via POST request and matched to the product.
    """

    product_variation = []
    if request.method == 'POST':
        for key, value in request.POST.items():
            variation = Variation.objects.filter(product=product, variation_category__iexact=key, variation_value__iexact=value).first()
            if variation:
                product_variation.append(variation)
    return product_variation

# This view function handles the removal of items from the cart one at a time
def remove_cart(request, product_id, cart_item_id):
    # Retrieve the Cart and Product instances based on provided ids
    product = get_object_or_404(Product, id=product_id)
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            
            # Try to get the CartItem instance
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        # If the CartItem quantity is greater than one, reduce it by one
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # If only one item is left, delete the CartItem
            cart_item.delete() 
    except:
        # If CartItem doesn't exist, do nothing
        pass

    return redirect('cart')

# This view function completely removes a cart item regardless of quantity
def remove_cart_item(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        # Get the CartItem instance and delete it
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        # Get the CartItem instance and delete it
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

# This view displays the cart page with items the user has added
def cart(request, total=0, quantity=0, cart_items=None):
    # Initialize tax and grand total variables ('IVA' typically refers to a form of value-added tax).
    try:
        iva = 0
        grand_total = 0
    
        if request.user.is_authenticated:
            # Retrieve the cart items for the current active user
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            # Retrieve the cart items for the current session's cart
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Calculate total price and total quantity of items in the cart
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        # Calculate tax and grand total
        iva = round(0.19 * total, 2)
        grand_total = round(total + iva, 2)


    except ObjectDoesNotExist:
        # If the Cart does not exist, ignore and continue
        pass

    # Prepare the context with cart details
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'iva': iva,
        'grand_total' : grand_total,
    }

    # Render the cart page with the context
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    # Initialize tax and grand total variables ('IVA' typically refers to a form of value-added tax).
    iva = 0
    grand_total = 0
    
    try:
        # Retrieve the cart items for the current session's cart
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Calculate total price and total quantity of items in the cart
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        # Calculate tax and grand total
        iva = round(0.19 * total, 2)
        grand_total = round(total + iva, 2)


    except ObjectDoesNotExist:
        # If the Cart does not exist, ignore and continue
        pass

    # Prepare the context with cart details
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'iva': iva,
        'grand_total' : grand_total,
    }

    return render(request, 'store/checkout.html', context)
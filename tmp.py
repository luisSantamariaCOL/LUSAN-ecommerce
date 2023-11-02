def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Use get_object_or_404 for safety
    product_variation = _get_product_variations_from_request(request, product)

    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))  # Use get_or_create to simplify
    cart_item, created = _get_or_create_cart_item(cart, product, product_variation)

    if not created:
        cart_item.quantity += 1  # Increment the quantity if the cart item already exists
        cart_item.save()

    return redirect('cart')

def _get_product_variations_from_request(request, product):
    product_variation = []
    if request.method == 'POST':
        for key, value in request.POST.items():  # Use items() to iterate over key-value pairs
            variation = Variation.objects.filter(product=product, variation_category__iexact=key, variation_value__iexact=value).first()
            if variation:
                product_variation.append(variation)
    return product_variation

def _get_or_create_cart_item(cart, product, product_variation):
    cart_item = None
    created = False
    if product_variation:
        # Create a unique set of variations to identify a unique cart item
        variations_set = set(var.id for var in product_variation)
        cart_item_qs = CartItem.objects.filter(product=product, cart=cart)
        for item in cart_item_qs:
            if set(item.variations.values_list('id', flat=True)) == variations_set:
                cart_item = item
                break
        if not cart_item:
            cart_item = CartItem.objects.create(product=product, quantity=0, cart=cart)  # Quantity will be incremented after
            cart_item.variations.set(product_variation)  # Use set() to add variations in M2M
            created = True
    else:
        cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)
    return cart_item, created

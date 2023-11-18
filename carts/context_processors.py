from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0

    # Verifica si la palabra 'admin' está en la ruta de la petición
    # Si es así, no se realiza el conteo para las páginas del admin panel
    if 'admin' in request.path:
        return {}
    else:
        try:
            # Filtra el carrito de compras por el id del carrito obtenido de la sesión
            cart = Cart.objects.filter(cart_id=_cart_id(request))

            if request.user.is_authenticated:
                # Si el usuario está autenticado, obtiene los ítems del carrito asociados al usuario
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                # Si no está autenticado, obtiene los ítems del carrito asociados al carrito de la sesión
                cart_items = CartItem.objects.all().filter(cart=cart[:1])

            # Recorre todos los ítems del carrito y suma las cantidades al contador
            for cart_item in cart_items:
                cart_count = cart_count + cart_item.quantity

        except Cart.DoesNotExist:
            # Si el carrito no existe, establece cart_count en 0
            cart_count = 0
    
    # Retorna un diccionario que contiene el número total de ítems en el carrito
    # Este diccionario se puede usar en el contexto de las plantillas para mostrar la cantidad de ítems
    return dict(cart_count=cart_count)
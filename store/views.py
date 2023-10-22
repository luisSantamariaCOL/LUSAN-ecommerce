from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from django.http import HttpResponse

from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        number_of_paged_numbers = 3
    
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        number_of_paged_numbers = 6
    
    paginator = Paginator(products, number_of_paged_numbers) # second argument represents the number of items you want to show
    page = request.GET.get('page') # capture the number of the store page
    paged_products = paginator.get_page(page) # stores the number of items of paginator in the paged_products variable


    context = {
        'products': paged_products,
        'product_count': products.count(),
    }

    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):

    try:
        # single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }


    return render(request, 'store/product_detail.html', context)
from _csv import reader
import logging
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.db.models import Avg, Sum
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import OrderForm, UploadProductsForms
from .models import Product, ProductToShoppingCart, ShoppingCart, Order, ProductToOrder, ProductToShop, Shop
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from datetime import datetime
from .tools.check_sale import check_sale, FalsePromocode, NotFirstPurchase
from django.utils.translation import gettext as _


def for_post_add_in_basker(request: HttpRequest):
    if 'pk' in request.POST:
        ProductToShoppingCart.objects. \
            update_or_create(product=Product.objects.get(pk=request.POST['pk']),
                             shopping_card=ShoppingCart.objects.get(user=request.user.pk), count=1)


class TheMostPurchasedProductsView(ListView):
    template_name = "shopapp/the_most_purchased_products_list.html"
    queryset = Product.objects.prefetch_related('producttoorder_set').\
        filter(producttoorder__count__gt=0,).annotate(pc=Sum('producttoorder__count')).order_by('-pc', 'name')
    context_object_name = "products"


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    model = Product
    context_object_name = "product"

    def post(self, request: HttpRequest):
        for_post_add_in_basker(request)
        return redirect(request.path)


class ShopLictView(ListView):
    model = Shop


logger = logging.getLogger(__name__)


class ShoppingCartDetailsView(UserPassesTestMixin, DetailView):
    def test_func(self):
        return self.request.user == self.get_object().user

    template_name = "shopapp/shopping_cart_detail.html"
    queryset = ShoppingCart.objects.select_related('user').prefetch_related('products')\
        .prefetch_related('producttoshoppingcart_set')
    context_object_name = "sc"


    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.kwargs.update(pk=ShoppingCart.objects.select_related('user').get(user__username=kwargs["username"]).pk)

    def get_context_data(self, **kwargs):
        form_order = {"form1": OrderForm()}
        kwargs.update(form_order)
        return super().get_context_data(**kwargs)


    def post(self, request: HttpRequest, *args, **kwargs):
            try:
                if 'promocode' in request.POST and request.POST['promocode'] != '':
                    discount_coefficient = check_sale(request, request.POST['promocode'])
                else:
                    discount_coefficient = 1
                with transaction.atomic():
                    dict_for_loggs = {}
                    user = User.objects.select_related('profile').get(username=kwargs['username'])
                    if "delete_pr" in request.POST:
                        ShoppingCart.objects.get(user=user).products.\
                            remove(Product.objects.get(pk=request.POST["delete_pr"]))
                    elif 'error' not in request.POST and OrderForm(request.POST).is_valid() and "order_st" in request.POST:
                        opa = 0  # Order purchase amount
                        user_order = Order.objects.create(user=user,
                                                          delivery_address=request.POST['delivery_address'],
                                                          promocode=request.POST['promocode'])
                        dict_for_loggs['order'] = user_order.pk
                        user_cart = ShoppingCart.objects.prefetch_related('products').get(user=user)
                        for opp in user_cart.producttoshoppingcart_set.all():
                            ProductToOrder.objects.create(order=user_order,
                                                          product=opp.product,
                                                          count=opp.count)
                            opa += opp.product.price
                            pts = ProductToShop.objects.filter(product=opp.product).first()
                            pts.count -= 1
                            if pts.count == 0:
                                pts.delete()
                            else:
                                pts.save()
                        opa *= discount_coefficient
                        user.profile.balance -= opa
                        user.profile.purchase_amount += opa
                        dict_for_loggs['opa'] = opa
                        dict_for_loggs['status'] = ''
                        if user.profile.status != 'gold' and user.profile.purchase_amount > 10000:
                            dict_for_loggs['status'] = 'gold'
                            user.profile.status = 'gold'
                        elif user.profile.status not in ('silver', 'gold') and user.profile.purchase_amount > 2000:
                            dict_for_loggs['status'] = 'silver'
                            user.profile.status = 'silver'
                        dict_for_loggs['user'] = user.username
                        user.profile.save()
                        user_cart.products.clear()
            except IntegrityError:
                context = {'sc': ShoppingCart.objects.select_related('user').prefetch_related('products').
                prefetch_related('producttoshoppingcart_set').get(user__username=kwargs['username']),
                           'error': _("You havn't money"),
                           'form1': OrderForm(request.POST)}
                return render(request, "shopapp/shopping_cart_detail.html", context=context)
            except FalsePromocode as fp:
                context = {'sc': ShoppingCart.objects.select_related('user').prefetch_related('products').
                prefetch_related('producttoshoppingcart_set').get(user__username=kwargs['username']),
                           'error': _('Promocode "{}" not found').format(fp.promocode),
                           'form1': OrderForm(request.POST)}
                return render(request, "shopapp/shopping_cart_detail.html", context=context)
            except NotFirstPurchase as nfp:
                context = {'sc': ShoppingCart.objects.select_related('user').prefetch_related('products').
                prefetch_related('producttoshoppingcart_set').get(user__username=kwargs['username']),
                           'error': f"{nfp.message}",
                           'form1': OrderForm(request.POST)}
                return render(request, "shopapp/shopping_cart_detail.html", context=context)
            else:
                if dict_for_loggs:
                    user, status, opa, order = dict_for_loggs['user'],\
                        dict_for_loggs['status'], dict_for_loggs['opa'], dict_for_loggs['order']
                    time = datetime.now()
                    logger.info(f'{time}: {user} has placed an order # {order}')
                    logger.info(f'{time}: {opa} points have been deducted from the {user} account')
                    if status:
                        logger.info(f'{time}: {user} received the status of "{status}"')
                return redirect(reverse_lazy('shopapp:products_list'))


class ProductsListView(ListView):
    paginate_by = 15
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.prefetch_related('producttoshop_set')\
        .prefetch_related('shops')\
        .filter(archived=False,producttoshop__count__gt=0,)\
        .annotate(pc=Sum('producttoshop__count'))

    def post(self, request: HttpRequest):
        for_post_add_in_basker(request)
        return redirect(request.get_full_path())


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    model = Product
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        return response


class ProductUpdateView(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = "shopapp.change_product"
    model = Product
    fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"

    def test_func(self):
        return self.request.user == self.get_object().created_by or self.request.user.is_superuser

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


def update_products(request):
    if request.method == "POST":
        form = UploadProductsForms(request.POST, request.FILES)
        if form.is_valid():
            products_file = form.cleaned_data["file"].read()
            products_str = products_file.decode('utf-8').split('\n')
            csv_reader = reader(products_str[1:-1], delimiter=";", quotechar='"')
            user = User.objects.get(pk=1)
            for row in csv_reader:

                product, status = Product.objects.get_or_create(created_by=user, name=row[0], price=row[1])
                if status:
                    product.save()

            return redirect(reverse('shopapp:products_list'))
    else:
        form = UploadProductsForms()
    context = {"form": form}
    return render(request, 'shopapp/upload_products_file.html', context=context)


#
#
# class OrdersListView(ListView):
#     queryset = (
#         Order.objects
#         .select_related("user")
#         .prefetch_related("products")
#     )
#
#
# class OrderDetailView(DetailView):
#     queryset = (
#         Order.objects
#         .select_related("user")
#         .prefetch_related("products")
#     )

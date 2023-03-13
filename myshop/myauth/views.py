from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.views import LogoutView
import logging
from shopapp.models import ShoppingCart, Stocks, Product, Order
from shopapp.views import for_post_add_in_basker
from .forms import UpBalanceForm
from .models import Profile
from datetime import datetime
from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login
from django.db.models import F, ExpressionWrapper, FloatField
from django.core.cache import cache


class PersonalAccountView(UserPassesTestMixin, DetailView):
    def test_func(self):
        return self.request.user.pk == self.get_object().pk and self.request.user.is_authenticated

    template_name = "myauth/personal_account.html"
    queryset = User.objects.prefetch_related('orders').all()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.kwargs.update(pk=User.objects.get(username=kwargs["username"]).pk)

    def get_context_data(self, **kwargs):
        promotions_cache_key = 'promotions:{}'.format(kwargs['object'].username)
        offers_cache_key = 'offers:{}'.format(kwargs['object'].username)
        promotions = cache.get_or_set(promotions_cache_key, Stocks.objects.only('code', 'short_description'), 600)
        offers = cache.get_or_set(offers_cache_key, Product.objects.only('pk', 'name', 'price', 'discount')
                                  .filter(discount__gt=0)
                                  .annotate(new_price=ExpressionWrapper(F('price') * 0.01 * (100 - F('discount')),
                                            output_field=FloatField())), 600)

        new_kwargs = {"promotions": promotions,
                      "offers": offers, }
        kwargs.update(new_kwargs)
        return super().get_context_data(**kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        for_post_add_in_basker(request)
        return redirect(request.path, *args, **kwargs)


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        ShoppingCart.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)

        login(request=self.request, user=user)
        return response

    def get_success_url(self):
        return reverse("myauth:personal_account",
                       kwargs={'username': self.object.username})


logger = logging.getLogger(__name__)


class MyLoginView(LoginView):

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        user = form.get_user()
        auth_login(self.request, user)
        logger.info(f'{datetime.now()}: {user.username} log in')
        return HttpResponseRedirect(self.get_success_url())


class UpBalanceView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def get(self, request: HttpRequest, username: str):
        context = {'form': UpBalanceForm(),
                   'username': username}
        return render(request, 'myauth/balance_update_form.html', context=context)
    def post(self, request: HttpRequest, username: str):
        user = User.objects.select_related('profile').get(username=username)
        user.profile.balance += int(request.POST['up_balance_count'])
        logger.info(f'{datetime.now()}: {user.username} replenished the balance by {request.POST["up_balance_count"]}')
        user.profile.save()
        return redirect(reverse("myauth:personal_account",
                        kwargs={'username': username}))


  



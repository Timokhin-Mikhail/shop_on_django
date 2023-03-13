from django.http import HttpRequest
from django.utils.translation import gettext as _
from shopapp.models import Stocks


class NotFirstPurchase(Exception):
    def __init__(self):
        self.message = _('This promo code is valid only for the first order')
        super().__init__(self.message)

    def __str__(self):
        return self.message


class FalsePromocode(Exception):
    def __init__(self, promocode):
        self.promocode = promocode
        self.message = 'promocode not found'
        super().__init__(self.message)

    def __str__(self):
        return f'{self.promocode}: {self.message}'


def check_for_the_first_purchase(request: HttpRequest):
    flag = request.user.orders.all().first()
    if flag:
        raise NotFirstPurchase
    return True


str_if_func = {'check_for_the_first_purchase': check_for_the_first_purchase}


def check_sale(request: HttpRequest, code):
    stock = Stocks.objects.filter(code=code.lower()).first()
    if stock is None:
        raise FalsePromocode(code)
    elif stock.name_of_func_to_check != '':
        str_if_func[stock.name_of_func_to_check](request)
    return stock.discount_coefficient

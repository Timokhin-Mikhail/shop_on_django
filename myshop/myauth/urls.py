from django.urls import path
from .views import (
    PersonalAccountView, MyLogoutView, RegisterView, UpBalanceView, MyLoginView
)

app_name = "myauth"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path('login/',
         MyLoginView.as_view(template_name="myauth/login.html",
                           redirect_authenticated_user=True,),
         name="login"),
    path('logout/', MyLogoutView.as_view(), name="logout"),
    path("<str:username>/", PersonalAccountView.as_view(), name="personal_account"),
    path("<str:username>/up_balance", UpBalanceView.as_view(), name="up_balance"),

]

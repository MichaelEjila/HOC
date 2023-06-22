from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.index, name='index_view'),
    # path('login/', views.login_view, name='login_view'),
    path('trivia/', views.trivia_view, name='trivia_view'),
    path('account/', views.account_view, name='account_view'),
    path('transaction/', views.transaction_view, name='transaction_view'),
    path('task/', views.task_view, name='task_view'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
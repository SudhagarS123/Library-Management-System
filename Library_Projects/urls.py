"""
URL configuration for Library_Projects project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from Library_App import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('book_read/',views.Book_read,name='book_view'),
    path('register/',views.register,name="student_register"),
    path('login/',views.login,name='student_login'),
    path('borrow/<int:book_id>/',views.borrow_book, name="borrow_book"),
    path('return/<int:book_id>/',views.return_book,name='return_book'),
    path('issued_books/',views.issued_books, name = 'issued_books'),
    path('send_reminder/',views.send_reminder),
]
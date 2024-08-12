from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('student-register/',views.register_student,name='student_register'),
    path('student-login/',views.login_student,name='student_login'),
    path('admin-login',views.login_admin,name='admin_login'),
    path('home-student',views.student_home,name='student_home'),
    path('borrow_book/<int:book_id>/',views.borrow_book,name='borrow_book'),
    path('admin-dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('student-info',views.student_info,name='student_info'),
    path('add-book',views.add_book,name='add_book'),
    path('all-pending-books',views.all_pending_books,name='all_pending_books'),
    path('all-borrowed-books',views.all_borrowed_books,name='all_borrowed_books'),
    path('all-book-list',views.all_book_list,name='all_book_list'),
    path('admin-list',views.admin_list,name='admin_list'),
    path('student-profile',views.student_profile,name='student_profile'),
    path('student-borrowed-books',views.student_borrowed_books,name='student_borrowed_books'),
    path('borrow-book-list',views.borrow_book_list,name='borrow_book_list'),
    path('return-books/', views.return_book_list, name='return_book_list'),
    path('return-book/<int:book_id>/', views.return_book, name='return_book'),
    path('return-success/', views.return_success, name='return_success'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

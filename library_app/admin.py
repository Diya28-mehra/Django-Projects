from django.contrib import admin
from .models import Student, Book, Transaction, Category

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('library_id', 'username', 'email', 'name', 'standard', 'books_pending', 'total_fine')
    list_filter = ('standard',)
    search_fields = ('library_id', 'username', 'email', 'name', 'standard')
    ordering = ('library_id',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available_copies')
    list_filter = ('author',)
    search_fields = ('title', 'author', 'isbn')
    ordering = ('title',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'borrow_date', 'return_date', 'fine')
    list_filter = ('borrow_date', 'return_date')
    search_fields = ('student__username', 'book__title')
    ordering = ('-borrow_date',)

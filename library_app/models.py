from django.db import models
from datetime import timedelta
import uuid
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    library_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    standard = models.CharField(max_length=10)
    image = models.ImageField(upload_to='images/')
    books_pending = models.PositiveIntegerField(default=0)
    total_fine = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return self.username


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set available_copies on creation
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Transaction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.return_date:
            self.return_date = self.borrow_date + timedelta(days=14)
        if not self.category:
            self.category = self.book.category
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student.username} - {self.book.title}'

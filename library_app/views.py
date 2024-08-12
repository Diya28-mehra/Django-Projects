from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
import uuid
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Student, Book ,Category,Transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login 
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

# Create your views here.

def home(request):
    return render(request, 'home.html')

@login_required
def student_home(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    books = Book.objects.all()

    if query:
        books = books.filter(title__icontains=query)

    if category_id:
        books = books.filter(category_id=category_id)

    categories = Category.objects.all()
    return render(request, 'student_home.html', {'books': books, 'categories': categories, 'query': query, 'category_id': category_id})


def admin_check(user):
    return user.is_staff  

@login_required
@user_passes_test(admin_check)
def admin_dashboard(request):
    books = Book.objects.all()
    students = Student.objects.all()
    pending_books = Transaction.objects.filter(return_date__isnull=True)
    borrowed_books = Transaction.objects.filter(return_date__isnull=False)

    context = {
        'books': books,
        'students': students,
        'pending_books': pending_books,
        'borrowed_books': borrowed_books,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def borrow_book_list(request):
    books = Book.objects.all()
    context = {
        'books': books,
    }
    return render(request, 'borrow_book_list.html', context)

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    student = get_object_or_404(Student, username=request.user.username)

    borrowed_books_count = Transaction.objects.filter(student=student, return_date__isnull=True).count()
    if borrowed_books_count >= 10:
        messages.error(request, 'You cannot borrow more than 10 books.')
        return redirect('borrow_book_list')

    
    if request.method == 'POST':
        if book.available_copies > 0:
            transaction = Transaction.objects.create(
                student=student,
                book=book,
                category=book.category,
                borrow_date=timezone.now(),
                return_date=timezone.now() + timedelta(days=14)
            )
            transaction.save()
            book.available_copies -= 1
            book.save()
            messages.success(request, 'You have successfully borrowed the book.')
            return redirect('student_home')
        else:
            messages.error(request, 'This book is no longer available.')
    
    context = {
        'book': book,
        'instructions': 'Hey, You can borrow it and return it within 14 days, otherwise, you will be charged 5 rupees daily.'
    }
    return render(request, 'borrow_book.html', context)

@login_required
def student_borrowed_books(request):
    student = get_object_or_404(Student, username=request.user.username)
    borrowed_books = Transaction.objects.filter(student=student)
    today = timezone.now().date() 
    
    for transaction in borrowed_books:
        transaction.time_gone = (today- transaction.borrow_date).days 
        transaction.is_overdue = transaction.time_gone >= 14
        
    context = {
        'student': student,
        'borrowed_books': borrowed_books,
    }
    
    return render(request, 'student_borrowed_books.html', context)

@login_required
def student_profile(request):
    student = get_object_or_404(Student,username=request.user.username)
    borrowed_books = Transaction.objects.filter(student=student)
    overdue_books = borrowed_books.filter(return_date__lt=timezone.now())

    pending_books = borrowed_books.count()
    total_fine = sum([(timezone.now()-book.return_date).days * 5 for book in overdue_books])
    
    context = {
        'student':student,
        'borrowed_books': borrowed_books,
        'overdue_books' : overdue_books,
        'pending_books': pending_books,
        'total_fine': total_fine,
    }
    

    return render(request, 'student_profile.html', context)

@login_required
def return_success(request):
    return render(request, 'return_success.html')


@login_required
def return_book(request, book_id):
    book_transaction = get_object_or_404(Transaction, id=book_id, student__username=request.user.username)
    
    if request.method == 'POST':
        fine = (timezone.now().date() - book_transaction.borrow_date).days - 14
        fine = fine * 5 if fine > 0 else 0
        
        book_transaction.delete()
        return redirect('return_success')

    context = {
        'book_transaction': book_transaction,
        'fine': fine
    }
    return render(request, 'return_book.html', context)


@login_required
def return_book_list(request):
    student = get_object_or_404(Student, username=request.user.username)
    borrowed_books = Transaction.objects.filter(student=student)
    
    books_with_fines = []
    today = timezone.now().date()

    for book in borrowed_books:
        days_overdue = (today - book.borrow_date).days - 14  # Assuming a 14-day borrow period
        fine = days_overdue * 5 if days_overdue > 0 else 0
        books_with_fines.append({
            'book': book,
            'fine': fine,
            'is_overdue': days_overdue > 0
        })
    
    context = {
        'books_with_fines': books_with_fines
    }
    return render(request, 'return_book_list.html', context)

def register_student(request):
    try:
        if request.method=="POST":
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            name = request.POST.get('name')
            standard = request.POST.get('standard') 
            profile_image = request.FILES.get('image')

            hashed_password = make_password(password)

            user =  User.objects.create_user(username=username, email=email, password=password)
            student = Student(library_id=uuid.uuid4(), username = username, email = email, password = hashed_password, name = name, standard = standard, image = profile_image)
            user.save()
            student.save()
            messages.success(request, 'Registration successful! Please log in to continue.')
            return redirect('student_home')
    except Exception as e:
        messages.error(request, f'Registration failed: {e}')
        return redirect(reverse('student_login'))

    return render(request,'student_register.html')


def login_student(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_superuser:
                messages.error(request, 'Admins cannot log in through this page.')
                return redirect('admin_login')
            else:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('student_home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('student_login')  
        
    return render(request, 'login_student.html')


def login_admin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')  
        else:
            messages.error(request, 'Invalid username or password or not an admin.')
    return render(request, 'admin_login.html')

@login_required
@user_passes_test(admin_check)
def add_book(request):
    if request.method=="POST":
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        total_copies = request.POST.get('total_copies')
        category_id = request.POST.get('category')
        try:
            category = Category.objects.get(id=category_id)
            book = Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                total_copies=total_copies,
                available_copies=total_copies,
                category=category
            )
            book.save()
            messages.success(request, 'Book added successfully.')
            return redirect('all_book_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
    else:
        messages.error(request,'Not Able to add the book, Invalid Details')
    categories = Category.objects.all()
    return render(request, 'add_book.html', {'categories': categories})

@login_required
@user_passes_test(admin_check)
def student_info(request):
    students = Student.objects.all()
    return render(request, 'student_info.html', {'students': students})

@login_required
@user_passes_test(admin_check)
def all_pending_books(request):
    now = timezone.now().date()
    overdue_books = Transaction.objects.filter(return_date__lt=now)
    return render(request, 'all_pending_books.html', {'overdue_books': overdue_books})

@login_required
@user_passes_test(admin_check)
def all_borrowed_books(request):
    borrowed_books = Transaction.objects.all()
    return render(request, 'all_borrowed_books.html', {'borrowed_books': borrowed_books})

@login_required
@user_passes_test(admin_check)
def all_book_list(request):
    categories = Category.objects.all()
    books_by_category = {category: Book.objects.filter(category = category) for category in categories}
    return render(request, 'all_book_list.html',{'books_by_category':books_by_category})

@login_required
@user_passes_test(admin_check)
def admin_list(request):
    admins = User.objects.filter(is_staff=True)
    return render(request, 'admin_list.html',{'admins':admins})


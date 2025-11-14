from django.shortcuts import render,redirect,HttpResponse,get_object_or_404

from .models import Book,Student,Issue

from django.utils import timezone

from django.core.mail import send_mail

from django.conf import settings

from datetime import timedelta

from threading import Thread

## Configuration of apscheduler because the Crontab doesn't support directly windows so we need to use the package

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

# Create your views here.

def home(request):
    return render(request,"home.html")

def Book_read(request):
    book = Book.objects.all()
    
    ## Search Option
    query = request.GET.get('q', '').strip()
    if query:
        book = Book.objects.filter(title__icontains = query)  |  Book.objects.filter(author__icontains = query)
    else:
        book = Book.objects.all()
        
        
    return render(request,'book.html',{'data':book , 'query': query})

def register(request):
    if request.method == "POST":
        s_name = request.POST.get("name")
        s_rollNumber = request.POST.get("roll_number")
        s_email = request.POST.get("email")
        s_password = request.POST.get("password")
        s_con_password = request.POST.get("confirm_password")
        s_department = request.POST.get("department")
        
        if s_password == s_con_password:
            Student.objects.create(name=s_name,roll_number=s_rollNumber,email=s_email,password=s_password,confirm_password=s_con_password,department=s_department) 
            
            ## Email Configuration
            try:
                subject = "Regidtration Successful - Library Management System"
                message = (
                    f"Hello {s_name},\n\n"
                    "Welcome to our Library Management System!\n"
                    "Your registration was successful.\n\n"
                    "You can now log in ans start borrowing books.\n\n"
                    "best Regards,\nLibrary Team"
                )
                recipient_list = [s_email]
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
                
                
            except Exception as e:
                print("Error during registration:", e)
                  
            return redirect('/login')
        return redirect ('/register')
    
    return render(request,'register.html')

def login(request):
    if request.method == "POST":
        s_rollNumber = request.POST.get('roll_number')
        s_password = request.POST.get('password')
        try:
            data = Student.objects.get(roll_number=s_rollNumber)
            if data.password == s_password:
                request.session["student_id"] = data.id
                request.session.modified = True      
                return redirect('book_view')
            return redirect('/login')         
        except Student.DoesNotExist:
            print("Hello")
            return redirect('/login')
    return render(request,'login.html')

def borrow_book(request,book_id):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect('/login')
    
    try:
        student = Student.objects.get(id=student_id)
        book = Book.objects.get(id=book_id)
        
        if not book.available:
            return HttpResponse("<h3> This book is Currently Unavailable.</h3>")
        
        Issue.objects.create(student = student, book=book,returned=False)
        
        book.available = False
        book.save()
        
        ## Send Email Notification
        
        try:
            subject = f"Book Borrowed: {book.title}"
            message = (
                f"Hello {student.name},\n\n"
                f"You have succesfully borrowed the book {book.title} by {book.author}.\n\n"
                "Please return the book within 7 days.\n\n"
                "Thank you,\nLibrary Management"  
            )
            recipient_list = [student.email]
            send_mail(subject,message, settings.EMAIL_HOST_USER, recipient_list)
        except Exception as e:
            print(f"Email Send Failed: {e}")
                
        return redirect('book_view')
    
    except Book.DoesNotExist:
        return HttpResponse("<h3>Book not found!</h3>")
    
    except Student.DoesNotExist:
        return HttpResponse("<h3>Student not found!</h3>")


def return_book(request,book_id):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect('student_login')

    try:
        student = get_object_or_404(Student, id=student_id)
        book = get_object_or_404(Book, id=book_id)
        issue = Issue.objects.filter(student=student, book=book, returned=False).first()
        
        if issue:
            issue.returned = True
            issue.return_date = timezone.now()
            issue.save()
            
            book.available = True
            book.save()
            
            try:
                subject = f"Book returned: {book.title}"
                message = (
                    f"Hello {student.name},\n\n"
                    f"You have successfully returned the book {book.title} by {book.author}.\n\n"
                    f"Return Date: {timezone.localtime(issue.return_date).strftime('%d %b %Y, %I:%M %p')}\n\n"
                    "Thank you for using the library.\n\n"
                    "library Management Team"
                )  
                recipient_list = [student.email]
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            except Exception as e:
                print(f"Email sending failed : {e}")
            
            return redirect('book_view')
        
        else:
            return HttpResponse("<h3> This book wasnot borrowed or already returned.</h3>")
    
    except Book.DoesNotExist:
        return HttpResponse("<h3> Book Not found!</h3>")
    
    except Student.DoesNotExist:
        return HttpResponse("<h3> Student not Found!</h3>")
        

def issued_books(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect('/login')
    
    try:
        student = Student.objects.get(id=student_id)
        issues = Issue.objects.filter(student=student)
        
    except Student.DoesNotExist:
        return redirect('/login')
    
    return render(request,'issued_books.html',{'student': student , 'issues':issues})
    
    
def send_reminder_background():
    try:
        seven_days_ago = timezone.now() - timedelta(days=7)
        issues = Issue.objects.filter(borrow_date__lte = seven_days_ago, returned = False)
        if not issues:
            return HttpResponse("<h3>No reminders to send - All books are on time</h3>")
        
        for issue in issues:
            student = issue.student
            book = issue.book
            due_date = issue.borrow_date+timedelta(days=7)
            
            subject = "Library Book Return Remainder"
            message = (
                f"\nDear {student.name},\n\n"
                f"This is a reminder that the book you Borrowed from our library is due for return.\n"
                f"Book Title : {book.title}\n"
                f"Author : {book.author}\n"
                f"borrowed date : {issue.borrow_date.strftime('%d %B %Y')}\n"
                f"Due Date : {due_date.strftime('%d %B %Y')}\n"
                f"Please return the book soon.\n\n"
                f"Regards,\n\n"
                f"Library Management System"
            )
            recipient_list = [student.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
    except Exception as e:
        print(f"Error in background reminder: {e}")
    
def send_reminder(reqest):
    Thread(target=send_reminder_background).start()
    return HttpResponse("<h3>Reminder emails are being sent in background!</h3>")


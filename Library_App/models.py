from django.db import models

from django.utils import timezone

# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13,unique=True)
    category = models.CharField(max_length=100)
    published_date = models.DateField(null=True,blank=True) ## Null=True means don't involve the date the field will be automaticall field by null.
    available = models.BooleanField(default=True)  ## deafault=True Every added book is there so put in True..
    
    def __str__(self):
        return self.title

    
class Student(models.Model):
    name = models.CharField(max_length=200)
    roll_number = models.CharField(max_length=20,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    confirm_password = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Issue(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.student.name} borrowed {self.book.title}"
    




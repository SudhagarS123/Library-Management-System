from django.contrib import admin

from .models import Book, Student, Issue

# Register your models here.


@admin.register(Book)
class Bookadmin(admin.ModelAdmin):
    list_display = ('title','author','isbn','category','published_date','available')
    list_filter = ('category','available')
    search_fields = ('title','author','isbn')    
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name','roll_number','email','department')
    search_fields = ('name','roll_number','email')
    
@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('student','book','issue_date','return_date','returned')
    list_filter = ('returned','issue_date')
    search_fields = ('student__name','book__title')



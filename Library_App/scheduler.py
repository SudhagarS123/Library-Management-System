from apscheduler.schedulers.background import BackgroundScheduler

from django.shortcuts import render,redirect,HttpResponse,get_object_or_404


from django.utils import timezone

from datetime import timedelta

from django.core.mail import send_mail

from django.conf import settings

from .models import Issue

def send_reminder():
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
        print("Error in Sending remainder:",e)
        
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminder,'interval', hours=24)
    scheduler.start()
    
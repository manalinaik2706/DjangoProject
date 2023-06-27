from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from todoapp.forms import RegisterForm
from django.contrib.auth.models import User
from django.db.models import Q
from todoapp.models import Task
import datetime
from django.contrib.auth import authenticate,login,logout
import random
from django.core.mail import send_mail
# Create your views here.

def dashboard(request):
    content={}
     #fetch data from form
   
    if request.method=="POST":
        name=request.POST['tname']
        det=request.POST['tdetails']
        c=request.POST['cat']
        s=request.POST['status']
        dt=request.POST['duedate']

        #validation
        u=User.objects.filter(id=request.user.id) #fetch auth_user objects
        # print(u)
        # print(u[0])
        t=Task.objects.create(name=name,detail=det,cat=c,status=s,enddate=dt, created_on=datetime.datetime.now(),uid=u[0])
        t.save()
        return redirect('/dashboard')
    else:
        q1=Q(uid=request.user.id)
        q2=Q(is_deleted=False)
        t=Task.objects.filter(q1 & q2)
        # print(t)
        sendpendingemail(t)
        content['data']=t
        return render(request,'todoapp/dashboard.html',content)


def user_register(request):
    content={}
    if request.method=="POST":
        un=request.POST['uname']
        p=request.POST['upass']
        cp=request.POST['ucpass']
        # print(un)
        # print(p)
        # print(cp)
        #validation 
        if un=='' or p=='' or cp=='':
            content['errmsg']="fields cannot be empty"
        elif p!=cp:
            content['errmsg']="password n confirm password didnt matched"
        elif len(p)<8:
            content['errmsg']="password must be at least 8 character"
        else:
            # content['success']="User register successfull please login"
            try:
                u=User.objects.create(username=un,email=un,password=p)
                u.set_password(p)
                u.save()
                content['success']="User register successfull please login"
            except Exception:
                content['errmsg']="User with same username already exists"

        return render(request,'accounts/register.html',content)
        
    else:
      
        return render(request,'accounts/register.html')
    
def user_login(request):
    content={}
    if request.method=="POST":
         un=request.POST['uname']
         up=request.POST['upass']
         u=authenticate(username=un,password=up)
        #  print(u)
         if u is not None:
             login(request,u)
             return redirect('/dashboard')
         else:
             content['errmsg']="invalid username or password"  
             return render(request,"accounts/login.html",content)         
           

    else:
        return render(request,'accounts/login.html')
    
def user_logout(request):
    logout(request) # destroy ession.delete all data from session
    return redirect('/login')

def delete(request,rid):
   print("Id:",rid)
   t=Task.objects.filter(id=rid)
   t.update(is_deleted=True)
   return redirect('/dashboard')

def edit(request,rid):
    if request.method=="POST":
        uname=request.POST['tname']
        udet=request.POST['tdetails']
        uc=request.POST['cat']
        us=request.POST['status']
        udt=request.POST['duedate']
       
        t=Task.objects.filter(id=rid)
        t.update(name=uname,detail=udet,cat=uc,status=us,enddate=udt)
        


        return redirect('/dashboard')

       
    else:
        t=Task.objects.filter(id=rid)
        content={}
        content['data']=t
        return render(request,'todoapp/edit.html',content)
    
def catfilter(request,cv):
    q1=Q(uid=request.user.id)
    q2=Q(is_deleted=False)
    q3=Q(cat=cv)

    t=Task.objects.filter(q1 & q2 & q3)
    content={}
    content['data']=t
    return render(request,'todoapp/dashboard.html',content)

    
def statusfilter(request,sv):
    q1=Q(uid=request.user.id)
    q2=Q(is_deleted=False)
    q3=Q(status=sv)

    t=Task.objects.filter(q1 & q2 & q3)
    content={}
    content['data']=t
    return render(request,'todoapp/dashboard.html',content)


def datefilter(request):
    frm=request.GET['from']
    to=request.GET['to']
    # print(frm)
    # print(to)

    q1=Q(uid=request.user.id)
    q2=Q(is_deleted=False)
    q3=Q(enddate__gte=frm)
    q4=Q(enddate__lte=to)
    t=Task.objects.order_by('-enddate').filter(q3 & q4).filter(q1 & q2)
    content={}
    content['data']=t
    
    return render(request,'todoapp/dashboard.html',content)

def datesort(request,dv):
    q1=Q(is_deleted=False)
    q2=Q(uid=request.user.id)
    if dv=='0':
        col="-enddate"
    else:
        col="enddate"

    t=Task.objects.order_by(col).filter(q1 & q2)

    content={}
    content['data']=t

    return render(request,'todoapp/dashboard.html',content)
    
    
def sendpendingemail(t):
   
    for x in t:
        if x.status==0:
            d=x.enddate.day
            curdt=datetime.datetime.now().day
            # print(curdt)
            # print(type(d))
            diff=d-curdt
            # print(diff)
            if diff==1:
               rec=x.uid.email
               print(rec)
               subject="REMINDER"
               msg=x.name+"Task is due for 1 day"
               sender='naikmanali1208@gmail.com'
               send_mail(
               subject,
               msg,
               sender,
               [rec],
               fail_silently=False
               )
        

               

            

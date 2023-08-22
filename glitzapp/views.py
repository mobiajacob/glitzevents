from django.shortcuts import render

# Create your views here.from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import uuid
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth import update_session_auth_hash
from .forms import *
import random
import string
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime,date, timedelta
import pywhatkit
from django.db.models import Q
from xhtml2pdf import pisa
from django.template.loader import get_template
from openpyxl import Workbook
######################################################################### <<<<<<<<<< LANDING MODULE >>>>>>>>>>>>>>

def ind(request):
    item_det = item.objects.all().order_by('-buying_count')[:10]

    return render(request, 'index.html',{"item_det":item_det})
def index(request):
    
    return render(request, 'index/index.html')

def index_search_feature(request):
        
        if request.method == 'POST':
            # Retrieve the search query entered by the user
            search_query = request.POST['search_query']
            # Filter your model by the search query
            items = item.objects.filter(Q(offer_price__contains=search_query) | Q(name__contains=search_query) | Q(under_category__contains=search_query) | Q(title_description__contains=search_query) | Q(description__contains=search_query))
            return render(request, 'index/index_all_item.html', { 'items':items})
        else:
            return redirect('index')



def login_main(request):
    if request.method == 'POST':
        username  = request.POST['username']
        password = request.POST['password']
        print(username)
        user = authenticate(username=username, password=password)
        
        try:
            if User_Registration.objects.filter(username=request.POST['username'], password=request.POST['password'],role="user1").exists():

                member = User_Registration.objects.get(username=request.POST['username'],password=request.POST['password'])
                
                request.session['userid'] = member.id
                if Profile_User.objects.filter(user_id=member.id).exists():
                    return redirect('staff_home')
                else:
                    return redirect('profile_staff_creation')
                
                
            elif User_Registration.objects.filter(username=request.POST['username'], password=request.POST['password'],role="user2", status="active").exists():
                member = User_Registration.objects.get(username=request.POST['username'],password=request.POST['password'])
                request.session['userid'] = member.id
                if Profile_User.objects.filter(user_id=member.id).exists():
                    return redirect('home')
                else:
                    return redirect('profile_user_creation')

            elif user.is_superuser:
                    request.session['userid'] = request.user.id
                    return redirect('admin_home')
            else:
                messages.error(request, 'Invalid username or password')
        except:
            messages.error(request, 'Invalid username or password')
    return render(request,'index/login.html')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if  User_Registration.objects.filter(email=email).exists():
            user =  User_Registration.objects.get(email=email)

        

            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string('index/forget-password/reset_password_email.html',{
                'user':user,
                'domain' :current_site,
                'user_id' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            }) 

            to_email = email
            send_email = EmailMessage(mail_subject,message,to = [to_email])
            send_email.send()

            messages.success(request,"Password reset email has been sent your email address.")
            return redirect('login_main')
        else:
            messages.error(request,"This account does not exists !")
            return redirect('forgotPassword')
    return render(request,'index/forget-password/forgotPassword.html')


def resetpassword_validate(request,uidb64,token):
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user =  User_Registration._default_manager.get(pk=user_id)  
    except(TypeError,ValueError,OverflowError, User_Registration.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['user_id'] = user_id 
        messages.success(request,"Please reset your password.")
        return redirect('resetPassword')
    else:
        messages.error(request,"The link has been expired !")
        return redirect('login_main')
    
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('user_id') 
            user =  User_Registration.objects.get(pk=uid)
            user.password = password
            user.save()
            messages.success(request,"Password reset successfull.")
            return redirect('login_main')

        else:
            messages.error(request,"Password do not match")
            return redirect('resetPassword')
    else:
        return render(request,'index/forget-password/resetPassword.html')

def logout(request):
    if 'userid' in request.session:  
        request.session.flush()
        return redirect('/')
    else:
        return redirect('/')


########################################################## <<<<<<<<<< USER MODULE >>>>>>>>>>>>>>>>

def base_sub(request):
    ids=request.session['userid']
    usr=Profile_User.objects.get(user=ids)
    lk=category.objects.get(id=1)
    crt_cnt=cart.objects.filter(user=ids).count()
 
    context={
        'user':usr,
        "lk":lk,
        "crt_cnt":2
    }
    return render(request, 'user/base_sub.html',context)

def user_base(request):
    ids=request.session['userid']
    usr=Profile_User.objects.get(user=ids)
    lk=category.objects.get(id=1)
    crt_cnt=cart.objects.filter(user=ids).count()
 
    context={
        'user':usr,
        "lk":lk,
        "crt_cnt":crt_cnt
    }
    return render(request, 'user/user_base.html',context)



def user_registration(request):
    
    if request.method =='POST':
        
        form = User_RegistrationForm(request.POST)
        if form.is_valid():
            print("haiiissss")
            email = form.cleaned_data['email']
            if User_Registration.objects.filter(email=email).exists():
                messages.error(request, 'Email Id already exists')
                return redirect('user_registration')
            else:
                user_model=form.save()
            user_id = user_model.pk

            udr=User_Registration.objects.get(id=user_id)
            digits = string.digits
            otp = ''.join(random.choices(digits, k=6))
            subject = "Greetings From Nataliya"
            message =f'Hi {email},\nYour Email Verification OTP is: {otp},\n Thank You \n Nataliya Team'
            udr.otp=otp
            udr.save()
            recipient = form.cleaned_data['email']    #  recipient =request.POST["inputTagName"]
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])
            messages.error(request, 'Otp Send To Given Email id')

            return redirect('index_user_confirmation',user_id=user_id)
        return redirect("user_registration")
    else:
        form = User_RegistrationForm()
        form.initial['role'] = 'user2'
    return render(request,'index/index_user/index_user_registraion.html',{'form':form})


def index_user_confirmation(request,user_id):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            
            if User_Registration.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('index_user_confirmation', user_id=user_id)
            else:
                artist_object = get_object_or_404(User_Registration, pk=user_id)
                otps=request.POST.get('otp')
                if str(artist_object.otp) == str(otps):
                    artist_object.username=username
                    artist_object.password = password
                    artist_object.save()
                    messages.success(request, 'Thank you for registering with us.')
                else:
                    messages.success(request, 'Invalid OTP')
                    return redirect('index_user_confirmation',user_id)
                return redirect('login_main')
        else:
            messages.error(request, ' Password and Confirm Password are not matching. Please verify it.')
            return redirect('index_user_confirmation', user_id=user_id)

    return render(request,'index/index_user/index_user_confirmation.html',{'user_id':user_id})

def profile_user_creation(request):
    if request.session.has_key('userid'):
        pass
    else:
        return redirect('/')
    ids=request.session['userid']
    usr=User_Registration.objects.get(id=ids)
    if request.method =="POST":
        
        firstname = request.POST.get('firstname',None)
        lastname = request.POST.get('lastname',None)
        phonenumber = request.POST.get('phonenumber',None)
        email = request.POST.get('email',None)
        gender = request.POST.get('gender',None)
        address = request.POST.get('address',None)
        date_of_birth= request.POST.get('date_of_birth',None)
        pro_pics = request.FILES.get('propic',None)
        secondnumb = request.POST.get('secondnumb',None)
        profile_artist = Profile_User(
            firstname=firstname,
            lastname=lastname,
            phonenumber=phonenumber,
            email=email,
            gender=gender,
            date_of_birth=date_of_birth,
            address=address,
            pro_pic=pro_pics,
            user=usr,
            secondnumber=secondnumb,
            joindate=date.today()
        )
        profile_artist.save()


        return redirect('home')
    context={
        'user':usr
    }
    return render(request,'index/index_user/profile_user_creation.html', context)



def search_feature(request):
    
        ids=request.session['userid']
        usr=Profile_User.objects.get(user=ids)
        crt_cnt=cart.objects.filter(user=ids).count()
        
        if request.method == 'POST':
            # Retrieve the search query entered by the user
            search_query = request.POST['search_query']
            # Filter your model by the search query
            items = item.objects.filter(Q(offer_price__contains=search_query) | Q(name__contains=search_query) | Q(under_category__contains=search_query) | Q(title_description__contains=search_query) | Q(description__contains=search_query))
            return render(request, 'user/all_item.html', {'user':usr,"crt_cnt":crt_cnt, 'items':items})
        else:
            return redirect('home')
            
            

  
def user_profile(request):
    if request.session.has_key('userid'):
        pass
    else:
        return redirect('/')
    

    ids=request.session['userid']
    usr=User_Registration.objects.get(id=ids)
    pro=Profile_User.objects.get(user=ids)
    crt_cnt=cart.objects.filter(user=ids).count()
    return render(request, 'user/user_profile.html',{'usr':usr,'pro':pro, 'user':pro,"crt_cnt":crt_cnt})

def edit_user_profile(request,id):

    if request.method == "POST":
        form = User_Registration.objects.get(id=id)
        eml=form.email
        usr_nm=form.username
        form.name = request.POST.get('name',None)
        form.lastname = request.POST.get('lastname',None)
        form.nickname = request.POST.get('nickname',None)
        form.gender = request.POST.get('gender',None)
        form.date_of_birth = request.POST.get('date_of_birth',None)
        form.phone_number = request.POST.get('phone_number',None)
        form.email = request.POST.get('email',None)
       
        form.username = request.POST.get('username',None)
        if request.POST.get('password',None) == "":
            form.password == form.password
        else:
            if request.POST.get('password',None) == request.POST.get('con_password',None):
                form.password == request.POST.get('password',None)
            else:
                messages.error(request,"Passwords do not match!")
                return redirect ("user_profile")
       
        if str(request.POST.get('email',None)) == str(eml):
            if str(request.POST.get('username',None)) == str(usr_nm):
                form.save()
            else:
                if User_Registration.objects.filter(username=form.username).exists():
                    messages.error(request,"Username already exists.")
                    return redirect ("user_profile")
                else:
                        form.save()
        else: 
           
            if User_Registration.objects.filter(email=form.email).exists():
                messages.error(request,"Email already exists.")
                return redirect ("user_profile")
            else:
                if str(request.POST.get('username',None)) == str(usr_nm):
                    form.save()
                else:
                    if User_Registration.objects.filter(username=form.username).exists():
                        messages.error(request,"Username already exists.")
                        return redirect ("user_profile")
                    else:
                        form.save()
                    
            
        prop=Profile_User.objects.get(user_id=id)
        prop.firstname = request.POST.get('name',None)
        prop.lastname = request.POST.get('lastname',None)
        prop.gender = request.POST.get('gender',None)
        prop.date_of_birth = request.POST.get('date_of_birth',None)
        prop.phonenumber = request.POST.get('phonenumber',None)
        prop.secondnumber = request.POST.get('second_number',None)

        prop.email = request.POST.get('email',None)
        prop.address = request.POST.get('address',None)
        if request.POST.get('image') == "":
            prop.pro_pic == prop.pro_pic

        else:
            prop.pro_pic = request.FILES.get('image')
        
        prop.save()
   
        
        return redirect ("user_profile")
    return redirect ("user_profile")

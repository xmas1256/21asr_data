import datetime
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.db.models import Sum
from base.forms import AuctionCreation, JismoniyCreation, ServiceCreation, TanirovkaCreation, TaskCreation, TeacherCreation, UploadForm, YaTTCreation, YuridikCreation
from .models import SMS, Access, Client, Notes, Profile, Service, Task, Upload, SMStext, telegramPost, subscriptions
from django.db.models.query import Q
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from aiogram import types
from loader import dp

# Create your views here.
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']

            try:
                user = User.objects.get(username=username)
            except:
                print("Foydalanuvchi topilmadi")

            user = authenticate(request,username=username, password=password)

            if user is not None:
                login(request, user)
                profile = Profile.objects.get(user=user)
                return redirect("home")
            else:
                print("Login yoki Parol xato")
    return render(request, 'login.html')

def  logoutPage(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def homePage(request):
    profile = Profile.objects.get(user=request.user)
    if profile.status == 'admin':
        uploads  = Upload.objects.all()
        uploads_uncompleted = Upload.objects.filter(status='5')
        uploads_unpriced = Upload.objects.filter(status='0')
        tasks_completed  = Task.objects.filter(status='10')
        tasks_uncompleted = Task.objects.filter(Q(status='0') | Q(status='5'))
    elif profile.status == 'superuser':
        uploads  = Upload.objects.all()
        uploads_uncompleted = Upload.objects.filter(Q(status='5') & Q(office=profile.office))
        uploads_unpriced = Upload.objects.filter(Q(status='0') & Q(office=profile.office))
        tasks_completed  = Task.objects.filter(Q(status='5') & Q(user=profile))
        tasks_uncompleted = Task.objects.filter(Q(user=profile) & Q(status='0') | Q(status='5'))
    elif profile.status == 'user':
        uploads = ""
        uploads_uncompleted = Upload.objects.filter(Q(status='5') & Q(reciever=profile))
        uploads_unpriced = Upload.objects.filter(Q(status='0') & Q(reciever=profile))
        tasks_completed  = Task.objects.filter(Q(status='5') & Q(user=profile))
        tasks_uncompleted = Task.objects.filter(Q(status='0') | Q(status='5'))
        tasks_uncompleted = tasks_uncompleted.filter(Q(user=profile))
    notes_process = Notes.objects.filter(Q(status='5') | Q(user=profile))
    notes_uncompleted = Notes.objects.filter(Q(status='0') | Q(user=profile))
    context = {'uploads':uploads, 'uploads_uncompleted':uploads_uncompleted,'uploads_unpriced':uploads_unpriced,'tasks_completed':tasks_completed,'tasks_uncompleted':tasks_uncompleted, 'profile':profile, 'notes_process':notes_process, 'notes_uncompleted':notes_uncompleted}
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def monitoringPage(request):
    profile = Profile.objects.get(user=request.user)
    if profile.status == 'admin' or profile.status == 'superuser':
        result = Upload.objects.filter(Q(status=5) | Q(status=0))
        context = {'profile':profile, 'result':result}
        return render(request, 'base/monitoring.html', context)
    elif profile.status == 'user':
        uncompleted = Upload.objects.filter(Q(status=5) | Q(status=0))
        result = uncompleted.filter(reciever=profile)
        context = {'profile':profile, 'result':result}
        return render(request, 'base/monitoring.html', context)
    else:
        return render(request, 'error-404.html')

@login_required(login_url='login')
def uploadPage(request):
    form = UploadForm()
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        profile = Profile.objects.get(id=request.POST['reciever'])
        admins = Profile.objects.filter(Q(status='admin') | Q(status='superuser'))
        sender = Profile.objects.get(user=request.user)
        form = UploadForm(request.POST, request.FILES)
        try:
            client = Client.objects.get(id=request.POST['client'])
        except:
            client = ""
        if form.is_valid():
            upload = form.save(commit=False)
            upload.office = profile.office
            upload.sender = sender
            upload.save()
            shablon1 = SMStext.objects.get(id=4).text
            text1=shablon1.replace("**nom", client.name)
            rephone = client.phone1.replace(" ", "")
            rephone = rephone.replace("-","")
            rephone = rephone.replace(".","")
            rephone = rephone.replace(")","")
            rephone = rephone.replace("(","")
            if len(rephone) == 13:
                rephone = rephone
            elif len(rephone) == 9:
                rephone = '+998' + str(rephone)
            elif len(rephone) == 12 and rephone[0] == '9':
                rephone = '+' + str(rephone)
            elif len(rephone) == 0 or len(rephone) == 1:
                rephone = False
            else:
                rephone = False

            if rephone:
                numberid = rephone
            
            url = 'http://91.204.239.44/broker-api/send'
            headers = {'Content-type': 'application/json',  # Определение типа данных
                    'Accept': 'text/plain',
                    'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
            data = {
            "messages":
            [
            {
            "recipient":numberid,
            "message-id":"prime000019953",

                "sms":{

                "originator": "21ASR",
                "content": {
                "text": text1
                }
                }
                    }
                ]
            } 
            
            requests.post(url, json=data, headers=headers)
            
         
            return redirect('upload')

    context = {'form':form, 'profile':profile}
    return render(request, 'base/upload.html', context)

@login_required(login_url='login')
def createService(request):
    form = ServiceCreation()
    profile = Profile.objects.get(user=request.user)
    services = Service.objects.all()
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1
    result = 10
    paginator = Paginator(services, result)

    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        page=1
        services = paginator.page(page)
    except:
        page = paginator.num_pages
        services = paginator.page(page)
    leftIndex = int(page)-1
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page)+2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1
    page_range = range(leftIndex, rightIndex)

    if request.method == "POST":
        form = ServiceCreation(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Muvaffaqiyatli ro`yxatga olindi ')
            return redirect('create-service')
        else:
            messages.error(request, 'Qandaydir xatolik :( ')
            return redirect('create-service')
    context = {'form':form, 'services':services, 'paginator':paginator, 'page_range':page_range, 'profile':profile}
    return render(request, 'base/createservice.html', context)

@login_required(login_url='login')
def editService(request, pk):
    service = Service.objects.get(id=pk)
    services = Service.objects.all()
    profile = Profile.objects.get(user=request.user)
    form = ServiceCreation(instance=service)
    if request.method == "POST":
        form = ServiceCreation(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Muvaffaqiyatli yangilandi ')
            return redirect('create-service')
        else:
            messages.error(request, 'Qandaydir xatolik :( ')
            return redirect('create-service')
    context = {'form':form, 'services':services, 'profile':profile}
    return render(request, 'base/createservice.html', context)

@login_required(login_url='login')
def deleteService(request, pk):
    service = Service.objects.get(id=pk)
    profile = Profile.objects.get(user=request.user)
    obj = service
    if request.method == "POST":
        service.delete()
        messages.success(request, 'Muvaffaqiyatli o`chirildi ')
        return redirect("create-service")
    return render(request, 'base/delete.html', {'obj':obj, 'profile':profile})

@login_required(login_url='login')
def taskPage(request):
    form = TaskCreation()
    profile = Profile.objects.get(user=request.user)
    
    if profile.status == 'admin':
        tasks = Task.objects.all()
    elif profile.status == 'superuser':
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(user=profile)
     
    date = datetime.date.today()
    
    if request.method == "POST":
        form = TaskCreation(request.POST, request.FILES)
        
        reciever = Profile.objects.get(id=request.POST['user'])
        shablon = SMStext.objects.get(id=5).text
        text = shablon.replace("**nom", reciever.name)
        rephone = reciever.phone
        numberid = rephone
        url = 'http://91.204.239.44/broker-api/send'
        headers = {'Content-type': 'application/json',  # Определение типа данных
                'Accept': 'text/plain',
                'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
        data = {
        "messages":
        [
        {
        "recipient":numberid,
        "message-id":"prime000019953",

            "sms":{

            "originator": "21ASR",
            "content": {
            "text": text
            }
            }
                }
            ]
        } 
                    
        requests.post(url, json=data, headers=headers)
        if form.is_valid():
            ts = form.save(commit=False)
            ts.sender = profile.phone
            ts.save()
            messages.success(request, 'Muvaffaqiyatli yuborildi ')
            return redirect('task')
        else:
            messages.error(request, 'Qandaydir xatolik :( ')
            return redirect('task')
    
    if 'to' and 'from' in request.GET:
        date_from = request.GET['from']
        date_to = request.GET['to']
        username = request.GET['users']
        if profile.status == 'admin' or profile.status == 'superuser':
            if username != "":
                try:
                    user = Profile.objects.get(id=username)
                except:
                    user = ""
                
        else:
            user = profile
        status = request.GET['type']
        pagType = False
        
        if username == "":
            tasks = Task.objects.filter(Q(duration__range=(date_from, date_to)))
    
        elif username != "":
            tasks = Task.objects.filter(Q(duration__range=(date_from, date_to))  & Q(user=user))
            
        if status != "":
            tasks = tasks.filter(status=status)
        else:
            tasks=tasks
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1

    pagType = True

    result = 5
    paginator = Paginator(tasks, result)

    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        page=1
        tasks = paginator.page(page)
    except:
        page = paginator.num_pages
        tasks = paginator.page(page)
    leftIndex = int(page)-1
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page)+2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1
    page_range = range(leftIndex, rightIndex)
    getContext = ""

    
    users = Profile.objects.all()
    context = {'form':form, 'tasks':tasks, 'date':date, 'paginator':paginator, 'page_range':page_range, 'users':users, 'pagType':pagType, 'profile':profile}    
    return render(request, 'base/task.html', context)       

@login_required(login_url='login')
def deleteTask(request, pk):
    service = Task.objects.get(id=pk)
    profile = Profile.objects.get(user=request.user)
    obj = service
    if request.method == "POST":
        service.delete()
        messages.success(request, 'Muvaffaqiyatli o`chirildi ')
        return redirect("task")
    return render(request, 'base/delete.html', {'obj':obj, 'profile':profile})

@login_required(login_url='login')
def viewTaskPage(request, pk):
    profile = Profile.objects.get(user=request.user)
    task = Task.objects.get(id=pk)
    return render(request, 'base/viewtask.html', {'task':task, 'profile':profile})

@login_required(login_url='login')
def finishTask(request, pk):
    try:
        task = Task.objects.get(id=pk)
    except:
        task = ""
    profile = Profile.objects.get(user=request.user)
    if profile == task.user:
        if request.method == "POST":
            shablon = SMStext.objects.get(id=6).text
            text = shablon.replace("**nom", task.user.name)
            print(text)
            rephone = task.sender
            numberid = rephone
            url = 'http://91.204.239.44/broker-api/send'
            headers = {'Content-type': 'application/json',  # Определение типа данных
                    'Accept': 'text/plain',
                    'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
            data = {
            "messages":
            [
            {
            "recipient":numberid,
            "message-id":"prime000019953",
        
                "sms":{
        
                "originator": "21ASR",
                "content": {
                "text": text
                }
                }
                    }
                ]
            } 
                        
            requests.post(url, json=data, headers=headers)
            task.answer = request.POST['answer']
            try:
                task.answer_file = request.FILES['file']
            except:
                task.answer_file = ""
            task.status = request.POST['status']
            task.save()
            messages.success(request, "Jarayon yakunlandi :)")
            return redirect('task')
        return render(request, 'base/finish.html', {'task':task, 'profile':profile})
    else:
        return render(request, 'error-404.html')
    

@login_required(login_url='login')
def serviceHistoryPage(request):
    profile = Profile.objects.get(user=request.user)
    if profile.status == 'admin':
        users = Profile.objects.all()
        context = {'users':users, 'view':False, 'profile':profile}
        if 'from' and 'to' in request.GET:
            date_to = request.GET['to']
            date_from = request.GET['from']
            try:
                office = request.GET['office']
            except:
                office = ""
            try:
                status = request.GET['type']
            except:
                status = ""
            try:
                user = request.GET['users']
            except:
                user = ""

            if user != "":
                uploads = Upload.objects.filter(Q(loaded_date__range=(date_from, date_to)) & Q(office__contains=office) & Q(status__contains=status) & Q(reciever_id=user))
            else:
                uploads = Upload.objects.filter(Q(loaded_date__range=(date_from, date_to)) & Q(office__contains=office) & Q(status__contains=status))
            sum = uploads.aggregate(Sum('payment'))
            context = {'users':users, 'uploads':uploads, 'view':True, 'sum':sum, 'profile':profile} 
        return render(request, 'base/servicehistory.html', context)
    else:
        return render(request, 'error-404.html')

@login_required(login_url='login')
def createClient(request):
    profile=Profile.objects.get(user=request.user)
    context = {'view':False, 'profile':profile}
    if 'type' in request.GET:
        type = request.GET['type']
        if type == 'ytt':
            form = YaTTCreation()
            if request.method == "POST":
                form = YaTTCreation(request.POST, request.FILES)
                print(form.errors)
                if form.is_valid():
                        client = form.save(commit=False)
                        client.type = 'ytt'
                        client.save()
                        messages.success(request, 'YaTT ro\'yxatga olindi')

        if type == 'yuridik':
            form = YuridikCreation()
            if request.method == "POST":
                form = YuridikCreation(request.POST, request.FILES)
                if form.is_valid():
                        client = form.save(commit=False)
                        client.type = 'yuridik'
                        client.save()
                        messages.success(request, 'Yuridik ro\'yxatga olindi')
                else:
                    messages.error(request, 'Qandaydir xatolik')

        if type == 'jismoniy':
            form = JismoniyCreation()
            if request.method == "POST":
                form = JismoniyCreation(request.POST, request.FILES)
                if form.is_valid():
                        client = form.save(commit=False)
                        client.type = 'jismoniy'
                        client.save()
                        messages.success(request, 'Jismoniy shaxs ro\'yxatga olindi')
        
        if type == 'tanirovka':
            form = TanirovkaCreation()
            if request.method == "POST":
                form = YaTTCreation(request.POST, request.FILES)
                if form.is_valid():
                        client = form.save(commit=False)
                        client.type = 'tanirovka'
                        client.owner = request.POST['owner']
                        client.tex_number = request.POST['tex_number']
                        client.text_series = request.POST['text_series']
                        try:
                            if request.POST['given_date'] != "":
                                g_date = datetime.datetime.strptime(request.POST['given_date'], '%d.%m.%Y')
                                client.given_date = g_date.strftime('%Y-%m-%d')
                        except:
                            client.given_date = None
                        
                        try:
                            if request.POST['expiry_date'] != "":
                                e_date = datetime.datetime.strptime(request.POST['expiry_date'], '%d.%m.%Y')
                                client.expiry_date = e_date.strftime('%Y-%m-%d')
                        except:
                            client.expiry_date = None
                    
                        try:
                            client.ruxsatnoma = request.FILES['ruxsatnoma']
                        except:
                            client.ruxsatnoma = ""
                        try:
                            client.texpas = request.FILES['texpas']
                        except:
                            client.texpas = ""
                        
                        client.save()
                        messages.success(request, f'Mijoz ro\'yxatga olindi')

        if type == 'auction':
            form = AuctionCreation()
            if request.method == "POST":
                form = AuctionCreation(request.POST, request.FILES)
                if form.is_valid():
                        client = form.save(commit=False)
                        client.type = 'auction'
                        client.save()
                        messages.success(request, 'Mijoz ro\'yxatga olindi')

        if type == 'teacher':
            form = TeacherCreation()
            if request.method == "POST":
                form = TeacherCreation(request.POST, request.FILES)
                print(form.errors)
                if form.is_valid():
                        client = form.save(commit=False)
                        client.type = 'teacher'
                        client.save()
                        messages.success(request, 'Mijoz ro\'yxatga olindi')
        context = {'view':True, 'form':form, 'profile':profile}
        
    if 'check' in request.GET:
        try:
            c_name = request.GET['name']
        except:
            c_name = ""
            
        try:
            j = request.GET['j']
        except:
            j = ""
            
        try:
            tin = request.GET['tin']
        except:
            tin = ""
            
        if c_name !="":
            checked = Client.objects.filter(name__icontains=c_name)
        else:
            checked = Client.objects.all()
        
        if j != "":
            checked = checked.filter(jshshir__contains=j)
        else:
            checked = checked
            
        if tin !="":
            checked = checked.filter(tin__contains=tin)
        else:
            checked = checked
            
        context = {'checked':True, 'clients':checked, 'profile':profile}

            
        
    return render(request, 'base/createclient.html', context)

@login_required(login_url='login')
def YaTTPage(request):
    profile = Profile.objects.get(user=request.user)
    clients = Client.objects.filter(type='ytt')
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1
    pagType = True

    result = 20
    try:
        paginator = Paginator(clients, result)
    except:
        paginator = Paginator(clients, result)
    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        page=1
        clients = paginator.page(page)
    except:
        page = paginator.num_pages
        clients = paginator.page(page)
    leftIndex = int(page)-1
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page)+2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1
    page_range = range(leftIndex, rightIndex)
    key_access = Access.objects.get(name="key")
    if profile in key_access.user.all():
        access = True
    else:
        access = False
    context = {'clients':clients, 'page_range':page_range, 'paginator':paginator, 'pagType':pagType, 'access':access, 'profile':profile}

    if 'filter' in request.GET:
        try:
            name = request.GET['name']
        except:
            name = ""
        try:
            stir = request.GET['stir']
        except:
            stir = ""
        try:
            tin = request.GET['tin']
        except:
            tin = ""
        try:
            cert = request.GET['certificate']
        except:
            cert = ""
        try:
            phone = request.GET['jshshir']
        except:
            phone = ""

        try:
            address = request.GET['report']
        except:
            address =""
        try:
            key = request.GET['key']
        except:
            key = ""
        try:
            key_expiry = request.GET['key_expiry']
        except:
            key_expiry = ""
        
        pagType = False

        tins = False
        
        if name != "":
            query = Client.objects.filter(Q(name__icontains=name)&Q(type='ytt'))
        else:
            query = Client.objects.filter(type='ytt')

        if stir != "":
            query = query.filter(tin__icontains=stir)

        if tin != "":
            if tin == "True":
                query = query.exclude(tin__exact="")
            else:
                query = query.filter(tin__exact="")
        else:
            query = query

        if cert != "":
            if cert == "none":
                query = query.filter(Q(guvohnoma_file__exact="") | Q(guvohnoma_file__contains=" ") | Q(guvohnoma_file__isnull=True))
            elif cert == "in_ten_days":
                today = datetime.date.today()+datetime.timedelta(days=1)
                ten_days = today+datetime.timedelta(days=10)
                query = query.filter(guvohnoma_exp__range=(today, ten_days))
            elif cert == "in_a_month":
                today = datetime.date.today()+datetime.timedelta(days=11)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(guvohnoma_exp__range=(today, ten_days))
            elif cert == "active":
                today = datetime.date.today()+datetime.timedelta(days=10)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(guvohnoma_exp__gt=ten_days)
            elif cert =="inactive":
                today = datetime.date.today()
                query = query.filter(guvohnoma_exp__lte=today)
                query = query.exclude(Q(guvohnoma_exp__isnull=True))
                
            else:
                query = query
        else:
            query = query
        
        if phone != "":
            query = query.filter(jshshir__icontains=phone)
        else:
            query = query
        

        if address != "":
            query = query.filter(sub_type=address)
        else:
            query = query

        
        if key != "":
            if key == "true":
                query = query.exclude(key__exact="")
            if key =="false":
                query = query.filter(key__exact="")
            else:
                query = query
        else:
            query=query


        if key_expiry != "":
            if key_expiry == "none":
                query = query.filter(Q(key__exact="") | Q(key__contains=" ") | Q(key__isnull=True))
            elif key_expiry == "in_ten_days":
                today = datetime.date.today()+datetime.timedelta(days=1)
                ten_days = today+datetime.timedelta(days=10)
                query = query.filter(key_exp__range=(today, ten_days))
            elif key_expiry == "in_a_month":
                today = datetime.date.today()+datetime.timedelta(days=11)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(key_exp__range=(today, ten_days))
            elif key_expiry == "active":
                today = datetime.date.today()+datetime.timedelta(days=10)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(key_exp__gt=ten_days)
            elif key_expiry =="inactive":
                today = datetime.date.today()
                query = query.filter(key_exp__lte=today)
                
            else:
                query = query
        
        if request.method == "POST":
            text = request.POST['text']
            for reciever in query:
                rephone = reciever.phone1.replace(" ", "")
                rephone = rephone.replace("-","")
                rephone = rephone.replace(".","")
                rephone = rephone.replace(")","")
                rephone = rephone.replace("(","")
                if len(rephone) == 13:
                    rephone = rephone
                    sms_status = 10
                elif len(rephone) == 9:
                    rephone = '+998' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 12 and rephone[0] == '9':
                    rephone = '+' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 0 or len(rephone) == 1:
                    rephone = False
                    sms_status = 0
                else:
                    rephone = False
                    sms_status = 5

                if rephone:
                    numberid = rephone

                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )

                    url = 'http://91.204.239.44/broker-api/send'
                    headers = {'Content-type': 'application/json',  # Определение типа данных
                            'Accept': 'text/plain',
                            'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
                    data = {
                    "messages":
                    [
                    {
                    "recipient":numberid,
                    "message-id":"prime000019953",

                        "sms":{

                        "originator": "21ASR",
                        "content": {
                        "text": text
                        }
                        }
                            }
                        ]
                    } 
                    try:
                        requests.post(url, json=data, headers=headers)
                    except:
                        messages.error(request, 'Internet bilan bog\'liq muammo :(')
                else:
                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )
                
  
      
  
        context = {'clients':query, 'pagType':pagType, 'access':access, 'profile':profile}

    
    return render(request, 'base/yatt.html', context)

@login_required(login_url='login')
def YuridikPage(request):
    profile = Profile.objects.get(user = request.user)
    clients = Client.objects.filter(type='yuridik')
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1
    pagType = True

    result = 20
    paginator = Paginator(clients, result)

    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        page=1
        clients = paginator.page(page)
    except:
        page = paginator.num_pages
        clients = paginator.page(page)
    leftIndex = int(page)-1
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page)+2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1
    page_range = range(leftIndex, rightIndex)
    key_access = Access.objects.get(name="key")
    if profile in key_access.user.all():
        access = True
    else:
        access = False
    context = {'clients':clients, 'page_range':page_range, 'paginator':paginator, 'pagType':pagType, 'access':access, 'profile':profile}

    if 'filter' in request.GET:
        try:
            name = request.GET['name']
        except:
            name = ""
        try:
            stir = request.GET['stir']
        except:
            stir = ""
        try:
            tin = request.GET['tin']
        except:
            tin = ""
        try:
            cert = request.GET['certificate']
        except:
            cert = ""
        try:
            phone = request.GET['phone']
        except:
            phone = ""

        try:
            passport = request.GET['passport']
        except:
            passport =""
        try:
            key = request.GET['key']
        except:
            key = ""
        try:
            key_expiry = request.GET['key_expiry']
        except:
            key_expiry = ""
        
        pagType = False

        tins = False
        query = Client.objects.filter(type__exact='yuridik')
        
        if name != "":
            query = Client.objects.filter(Q(type__exact='yuridik') & Q(name__icontains=name))

        else:
            query = Client.objects.filter(type__exact='yuridik')

        if stir != "":
            query = query.filter(tin__icontains=stir)

        if tin != "":
            query = query.filter(jshshir__icontains=tin)

        if cert != "":
            if cert == "true":
                query = query.exclude(guvohnoma_file__isnull=False)
            else:
                query = query.filter(guvohnoma_file__exact="")
        else:
            query = query
        
        if phone != "":
            if phone == 'true':
                query = query.exclude(phone1__exact="")
            elif phone == 'false':
                query = query.filter(phone1__exact="")
            else:
                query = query
        else:
            query = query
        

        if passport != "":
            if passport == 'true':
                query = query.exclude(passport__exact="")
            if passport == 'false':
                query = query.filter(passport__exact="")
            else:
                query = query
        else:
            query = query

        
        if key != "":
            if key == "true":
                query = query.exclude(key__exact="")
            if key =="false":
                query = query.filter(key__exact="")
            else:
                query = query
        else:
            query=query


        if key_expiry != "":
            if key_expiry == "none":
                query = query.filter(Q(key__exact="") | Q(key__contains=" ") | Q(key__isnull=True))
            elif key_expiry == "in_ten_days":
                today = datetime.date.today()+datetime.timedelta(days=1)
                ten_days = today+datetime.timedelta(days=10)
                query = query.filter(key_exp__range=(today, ten_days))
            elif key_expiry == "in_a_month":
                today = datetime.date.today()+datetime.timedelta(days=11)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(key_exp__range=(today, ten_days))
            elif key_expiry == "active":
                today = datetime.date.today()+datetime.timedelta(days=10)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(key_exp__gt=ten_days)
            elif key_expiry =="inactive":
                today = datetime.date.today()
                query = query.filter(key_exp__lte=today)
                
            else:
                query = query
        
        if request.method == "POST":
            text = request.POST['text']
            for reciever in query:
                rephone = reciever.phone1.replace(" ", "")
                rephone = rephone.replace("-","")
                rephone = rephone.replace(".","")
                rephone = rephone.replace(")","")
                rephone = rephone.replace("(","")
                if len(rephone) == 13:
                    rephone = str(rephone)
                    sms_status = 10
                elif len(rephone) == 9:
                    rephone = '+998' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 12 and rephone[0] == '9':
                    rephone = '+' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 0 or len(rephone) == 1:
                    rephone = False
                    sms_status = 0
                else:
                    rephone = False
                    sms_status = 5

                if rephone:
                    numberid = rephone

                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )

                    url = 'http://91.204.239.44/broker-api/send'
                    headers = {'Content-type': 'application/json',  # Определение типа данных
                            'Accept': 'text/plain',
                            'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
                    data = {
                    "messages":
                    [
                    {
                    "recipient":numberid,
                    "message-id":"prime000019953",

                        "sms":{

                        "originator": "21ASR",
                        "content": {
                        "text": text
                        }
                        }
                            }
                        ]
                    } 
                    try:
                        requests.post(url, json=data, headers=headers)
                    except:
                        messages.error(request, 'Internet bilan bog\'liq muammo :(')
                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )
                
        

        context = {'clients':query, 'pagType':pagType, 'profile':profile, 'access':access}

  
    return render(request, 'base/yuridik.html', context)

@login_required(login_url='login')
def JismoniyPage(request):
    clients = Client.objects.filter(type='jismoniy')
    profile = Profile.objects.get(user=request.user)
    key_access = Access.objects.get(name="key")
    if profile in key_access.user.all():
        access = True
    else:
        access = False
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1
    pagType = True

    result = 20
    paginator = Paginator(clients, result)

    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        page=1
        clients = paginator.page(page)
    except:
        page = paginator.num_pages
        clients = paginator.page(page)
    leftIndex = int(page)-1
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page)+2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1
    page_range = range(leftIndex, rightIndex)
    context = {'clients':clients, 'page_range':page_range, 'paginator':paginator, 'pagType':pagType, 'profile':profile}

    if 'filter' in request.GET:
        try:
            name = request.GET['name']
        except:
            name = ""
        try:
            stir = request.GET['stir']
        except:
            stir = ""
        try:
            tin = request.GET['tin']
        except:
            tin = ""
        try:
            cert = request.GET['certificate']
        except:
            cert = ""
        try:
            phone = request.GET['phone']
        except:
            phone = ""

        try:
            passport = request.GET['passport']
        except:
            passport =""
        try:
            key = request.GET['key']
        except:
            key = ""
        try:
            key_expiry = request.GET['key_expiry']
        except:
            key_expiry = ""
        
        pagType = False

        tins = False
        query = Client.objects.filter(type__exact='jismoniy')
        
        if name != "":
            query = Client.objects.filter(Q(type__exact='jismoniy') & Q(name__icontains=name))
       
        else:
            query = Client.objects.filter(type__exact='jismoniy')

        if stir != "":
            query = query.filter(tin__icontains=stir)

        if tin != "":
            query = query.filter(jshshir__icontains=tin)

        if cert != "":
            if cert == "True":
                query = query.exclude(guvohnoma_file__exact="")
            else:
                query = query.filter(guvohnoma_file__exact="")
        else:
            query = query
        
        if phone != "":
            if phone == 'true':
                query = query.exclude(phone1__exact="")
            elif phone == 'false':
                query = query.filter(phone1__exact="")
            else:
                query = query
        else:
            query = query
        

        if passport != "":
            if passport == 'true':
                query = query.exclude(passport__exact="")
            if passport == 'false':
                query = query.filter(passport__exact="")
            else:
                query = query
        else:
            query = query

        
        if key != "":
            if key == "true":
                query = query.exclude(key__exact="")
            if key =="false":
                query = query.filter(key__exact="")
            else:
                query = query
        else:
            query=query


        if key_expiry != "":
            if key_expiry == "none":
                query = query.filter(Q(key__exact="") | Q(key__contains=" ") | Q(key__isnull=True))
            elif key_expiry == "in_ten_days":
                today = datetime.date.today()+datetime.timedelta(days=1)
                ten_days = today+datetime.timedelta(days=10)
                query = query.filter(key_exp__range=(today, ten_days))
            elif key_expiry == "in_a_month":
                today = datetime.date.today()+datetime.timedelta(days=11)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(key_exp__range=(today, ten_days))
            elif key_expiry == "active":
                today = datetime.date.today()+datetime.timedelta(days=10)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(key_exp__gt=ten_days)
            elif key_expiry =="inactive":
                today = datetime.date.today()
                query = query.filter(key_exp__lte=today)
                
            else:
                query = query
        
        if request.method == "POST":
            text = request.POST['text']
            for reciever in query:
                rephone = reciever.phone1.replace(" ", "")
                rephone = rephone.replace("-","")
                rephone = rephone.replace(".","")
                rephone = rephone.replace(")","")
                rephone = rephone.replace("(","")
                if len(rephone) == 13:
                    rephone = rephone
                    sms_status = 10
                elif len(rephone) == 9:
                    rephone = '+998' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 12 and rephone[0] == '9':
                    rephone = '+' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 0 or len(rephone) == 1:
                    rephone = False
                    sms_status = 0
                else:
                    rephone = False
                    sms_status = 5

                if rephone:
                    numberid = rephone

                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )

                    url = 'http://91.204.239.44/broker-api/send'
                    headers = {'Content-type': 'application/json',  # Определение типа данных
                            'Accept': 'text/plain',
                            'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
                    data = {
                    "messages":
                    [
                    {
                    "recipient":numberid,
                    "message-id":"prime000019953",

                        "sms":{

                        "originator": "21ASR",
                        "content": {
                        "text": text
                        }
                        }
                            }
                        ]
                    } 
                    try:
                        requests.post(url, json=data, headers=headers)
                    except:
                        messages.error(request, 'Internet bilan bog\'liq muammo :(')
                else:
                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )
                
  
        context = {'clients':query, 'pagType':pagType, 'access':access, 'profile':profile}

  
    return render(request, 'base/jismoniy.html', context)

@login_required(login_url='login')
def tanirovkaPage(request):
    profile = Profile.objects.get(user=request.user)
    clients = Client.objects.filter(type='tanirovka')
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1
    pagType = True
    result = 20
    paginator = Paginator(clients, result)
    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        page=1
        clients = paginator.page(page)
    except:
        page = paginator.num_pages
        clients = paginator.page(page)
    leftIndex = int(page)-1
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page)+2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1
    page_range = range(leftIndex, rightIndex)
    context = {'clients':clients, 'page_range':page_range, 'paginator':paginator, 'pagType':pagType, 'profile':profile}
    if 'filter' in request.GET:
        try:
            name = request.GET['name']
        except:
            name = ""
        try:
            owner = request.GET['owner']
        except:
            owner = ""
        try:
            tin = request.GET['tin']
        except:
            tin = ""
        try:
            tex_number = request.GET['tex_number']
        except:
            tex_number = ""
        try:
            phone = request.GET['phone']
        except:
            phone = ""
        try:
            access = request.GET['access']
        except:
            access = ""
        pagType = False
        tins = False
        query = Client.objects.filter(type__exact='tanirovka')
        if name != "":
            query = Client.objects.filter(Q(type__exact='tanirovka') & Q(name__icontains=name))
       
        else:
            query = Client.objects.filter(type__exact='tanirovka')
        if owner != "":
            query = query.filter(owner__icontains=owner)
        else:
            query = query
            
        if tin != "":
            query = query.filter(jshshir__icontains=tin)

        if tex_number != "":
            query = query.exclude(tex_number__icontains="")
        else:
            query = query

       
        
        if phone != "":
            if phone == 'true':
                query = query.exclude(phone1__exact="")
            elif phone == 'false':
                query = query.filter(phone1__exact="")
            else:
                query = query
        else:
            query = query
        



        if access != "":
            if access == "none":
                query = query.exclude(expiry_date__contains="")
            elif access == "in_ten_days":
                today = datetime.date.today()+datetime.timedelta(days=1)
                ten_days = today+datetime.timedelta(days=10)
                query = query.filter(expiry_date__range=(today, ten_days))
            elif access == "in_a_month":
                today = datetime.date.today()+datetime.timedelta(days=11)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(expiry_date__range=(today, ten_days))
            elif access == "active":
                today = datetime.date.today()+datetime.timedelta(days=10)
                ten_days = today+datetime.timedelta(days=20)
                query = query.filter(expiry_date__gt=ten_days)
            elif access =="inactive":
                today = datetime.date.today()
                query = query.filter(expiry_date__lte=today)
                
            else:
                query = query
        
        if request.method == "POST":
            text = request.POST['text']
            for reciever in query:
                rephone = reciever.phone1.replace(" ", "")
                rephone = rephone.replace("-","")
                rephone = rephone.replace(".","")
                rephone = rephone.replace(")","")
                rephone = rephone.replace("(","")
                if len(rephone) == 13:
                    rephone = rephone
                    sms_status = 10
                elif len(rephone) == 9:
                    rephone = '+998' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 12 and rephone[0] == '9':
                    rephone = '+' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 0 or len(rephone) == 1:
                    rephone = False
                    sms_status = 0
                else:
                    rephone = False
                    sms_status = 5

                if rephone:
                    numberid = rephone

                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )

                    url = 'http://91.204.239.44/broker-api/send'
                    headers = {'Content-type': 'application/json',  # Определение типа данных
                            'Accept': 'text/plain',
                            'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
                    data = {
                    "messages":
                    [
                    {
                    "recipient":numberid,
                    "message-id":"prime000019953",

                        "sms":{

                        "originator": "21ASR",
                        "content": {
                        "text": text
                        }
                        }
                            }
                        ]
                    } 
                    try:
                        requests.post(url, json=data, headers=headers)
                    except:
                        messages.error(request, 'Internet bilan bog\'liq muammo :(')
                else:
                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )
                
  
        context = {'clients':query, 'pagType':pagType, 'profile':profile}

  
    return render(request, 'base/tanirovka.html', context)

@login_required(login_url='login')
def auctionPage(request):
    profile = Profile.objects.get(user=request.user)
    clients = Client.objects.filter(type='auction')
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1
    pagType = True

    result = 20
    paginator = Paginator(clients, result)

    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        page=1
        clients = paginator.page(page)
    except:
        page = paginator.num_pages
        clients = paginator.page(page)
    leftIndex = int(page)-1
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page)+2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1
    page_range = range(leftIndex, rightIndex)
    context = {'clients':clients, 'page_range':page_range, 'paginator':paginator, 'pagType':pagType, 'profile':profile}

    if 'filter' in request.GET:
        try:
            name = request.GET['name']
        except:
            name = ""
        
        try:
            owner = request.GET['owner']
        except:
            owner = ""
            
        try:
            tin = request.GET['tin']
        except:
            tin = ""
        
    
        try:
            phone = request.GET['phone']
        except:
            phone = ""

        try:
            passport = request.GET['passport']
        except:
            passport = ""
        
        
        pagType = False

        tins = False
        query = Client.objects.filter(type__exact='auction')
        
        if name != "":
            query = Client.objects.filter(Q(type__exact='auction') & Q(name__icontains=name))
         
        else:
            query = Client.objects.filter(type__exact='auction')

        if owner != "":
            query = query.filter(owner__icontains=owner)
        else:
            query = query
    
        if tin != "":
            query = query.filter(jshshir__icontains=tin)
       
        
        if phone != "":
            if phone == 'true':
                query = query.exclude(phone1__exact="")
            elif phone == 'false':
                query = query.filter(phone1__exact="")
            else:
                query = query
        else:
            query = query
        



        if passport != "":
            if passport == 'true':
                query = query.exclude(passport__exact="")
            elif passport == 'false':
                query = query.filter(passport__exact="")
            else:
                query = query
        else:
            query = query
        
        if request.method == "POST":
            text = request.POST['text']
            for reciever in query:
                rephone = reciever.phone1.replace(" ", "")
                rephone = rephone.replace("-","")
                rephone = rephone.replace(".","")
                rephone = rephone.replace(")","")
                rephone = rephone.replace("(","")
                if len(rephone) == 13:
                    rephone = rephone
                    sms_status = 10
                elif len(rephone) == 9:
                    rephone = '+998' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 12 and rephone[0] == '9':
                    rephone = '+' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 0 or len(rephone) == 1:
                    rephone = False
                    sms_status = 0
                else:
                    rephone = False
                    sms_status = 5

                if rephone:
                    numberid = rephone

                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )

                    url = 'http://91.204.239.44/broker-api/send'
                    headers = {'Content-type': 'application/json',  # Определение типа данных
                            'Accept': 'text/plain',
                            'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
                    data = {
                    "messages":
                    [
                    {
                    "recipient":numberid,
                    "message-id":"prime000019953",

                        "sms":{

                        "originator": "21ASR",
                        "content": {
                        "text": text
                        }
                        }
                            }
                        ]
                    }
                    requests.post(url, json=data, headers=headers)
                    
                else:
                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )
                
  
        context = {'clients':query, 'pagType':pagType, 'profile':profile}

    return render(request, 'base/auction.html', context)

@login_required(login_url='login')
def teachersPage(request):
    profile = Profile.objects.get(user=request.user)
    clients = Client.objects.filter(type='teacher')
    if "page" in request.GET:
        page = request.GET['page']
    else:
        page = 1
    pagType = True

    result = 20
    paginator = Paginator(clients, result)

    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        page=1
        clients = paginator.page(page)
    except:
        page = paginator.num_pages
        clients = paginator.page(page)
    leftIndex = int(page)-1
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page)+2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1
    page_range = range(leftIndex, rightIndex)
    context = {'clients':clients, 'page_range':page_range, 'paginator':paginator, 'pagType':pagType, 'profile':profile}

    if 'filter' in request.GET:
        try:
            name = request.GET['name']
        except:
            name = ""
        
        try:
            phone = request.GET['phone']
        except:
            phone = ""
        
        try:
            school = request.GET['school']
        except:
            school = ""
            
        try:
            work_as = request.GET['work_as']
        except:
            work_as = ""
            
        pagType = False

        tins = False
        
        query = Client.objects.filter(type__exact='teacher')
        
        if name != "":
            query = Client.objects.filter(Q(type__exact='teacher') & Q(name__icontains=name))
        
        else:
            query = Client.objects.filter(type__exact='teacher')
            
        if school != "":
            query = query.filter(school__icontains=school)
        else:
            query = query

        if work_as != "":
            query = query.filter(work_as__icontains=work_as)
        else:
            query = query       
        
        if phone != "":
            if phone == 'true':
                query = query.exclude(Q(phone1__exact="")& Q(phone1=None))
            elif phone == 'false':
                query = query.filter(Q(phone1__exact="") & Q(phone1=None))
            else:
                query = query
        else:
            query = query     
        
        if request.method == "POST":
            text = request.POST['text']
            for reciever in query:
                try:
                    rephone = reciever.phone1.replace(" ", "")
                except:
                    rephone = ""
                rephone = rephone.replace("-","")
                rephone = rephone.replace(".","")
                rephone = rephone.replace(")","")
                rephone = rephone.replace("(","")
                if len(rephone) == 13:
                    rephone = rephone
                    sms_status = 10
                elif len(rephone) == 9:
                    rephone = '+998' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 12 and rephone[0] == '9':
                    rephone = '+' + str(rephone)
                    sms_status = 10
                elif len(rephone) == 0 or len(rephone) == 1:
                    rephone = False
                    sms_status = 0
                else:
                    rephone = False
                    sms_status = 5

                if rephone:
                    numberid = rephone

                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )

                    url = 'http://91.204.239.44/broker-api/send'
                    headers = {'Content-type': 'application/json',  # Определение типа данных
                            'Accept': 'text/plain',
                            'Authorization': 'Basic eHhpYXNyOmJwOWJFTVA3ODI='}
                    data = {
                    "messages":
                    [
                    {
                    "recipient":numberid,
                    "message-id":"prime000019953",

                        "sms":{

                        "originator": "21ASR",
                        "content": {
                        "text": text
                        }
                        }
                            }
                        ]
                    } 
                    try:
                        requests.post(url, json=data, headers=headers)
                    except:
                        messages.error(request, 'Internet bilan bog\'liq muammo :(')
                else:
                    SMS.objects.create(
                        client=reciever,
                        text=text,
                        status=sms_status
                    )
                
  
        context = {'clients':query, 'pagType':pagType, 'profile':profile}

  
    return render(request, 'base/teacher.html', context)


@login_required(login_url='home')
def SMSPage(request):
    profile = Profile.objects.get(user = request.user)
    if profile.status == 'admin' or profile.status == 'superuser':
        sms = SMStext.objects.all()
        return render(request, 'base/smstemp.html', {'sms':sms, 'profile':profile})
    else:
        return render(request, 'error-404.html')

@login_required(login_url='home')
def editSMS(request, pk):
    profile = Profile.objects.get(user = request.user)
    if profile.status == 'admin' or profile.status == 'superuser':
        sms = SMStext.objects.get(id=pk)

        if sms:
            if request.method == "POST":
                text = request.POST['text']
                sms.text = text
                sms.save()
                messages.success(request, 'Malumot yangilandi :)')
                return redirect('sms')
            else:
                messages.error(request, 'Qandaydir xatolik :( ')
            return render(request, 'base/forms.html', {'sms':sms, 'view':'sms', 'profile':profile})
        else:
            return render(request, 'error-404.html')
    else:
        return render(request, 'error-404.html')
        
@login_required(login_url='home')
def deleteClient(request, pk):
    profile = Profile.objects.get(user = request.user)
    if profile.status == 'admin':
        if request.method == "POST":
            try:
                delclient = Client.objects.get(id=request.POST['client'])
            except:
                messages.error(request, 'Mijoz topilmadi :(')
                return redirect(request.META.get('HTTP_REFERER'))
            delclient.delete()
            messages.success(request, "Ma'lumot o'chirildi ;(")
            return redirect('create-client')
        return render(request, 'base/delete.html', {'pk':pk})
    else:
        return render(request, 'error-404.html')

@login_required(login_url='home')
def telegramPage(request):
    profile = Profile.objects.get(user = request.user)
    posts = telegramPost.objects.all().order_by('-id')
    if profile.status == 'admin' or profile.status == 'superuser':
        teleusers = subscriptions.objects.all().order_by('-id')
        if request.method == "POST":
            try:
                file = request.FILES['file']
            except:
                file = ""
            text = request.POST['text']
            post_type = request.POST['postType']
            client_type = request.POST['type']
            telegramPost.objects.create(
                file=file,
                text=text,
                post_type=post_type,
                client_type=client_type
                )
                
            messages.success(request, "Post qo'shildi")
            return redirect('telegram')
        
        if 'post' in request.GET:
            post = telegramPost.objects.get(id=request.GET['post'])
            
            subs = Client.objects.filter(~Q(telegram=""))
            subs = subs.filter(~Q(telegram__isnull=True))
            
            if post.client_type != 'all':
                subs = subs.filter(type=post.client_type)
            for sub in subs:
                if post.post_type == 'text':
                    requests.get(f"https://api.telegram.org/bot5194587575:AAFprDquC60qUcCpVhyViIJ5hH5z7VGGRHw/sendMessage?chat_id={sub.telegram}&text={post.text}")
                elif post.post_type == 'photo':
                    requests.get(f"https://api.telegram.org/bot5194587575:AAFprDquC60qUcCpVhyViIJ5hH5z7VGGRHw/sendPhoto?chat_id={sub.telegram}&photo=https://21-buxgalteriya.uz/app{post.file.url}&caption={post.text}&parse_mode=html")
                elif post.post_type == 'video':
                    requests.get(f"https://api.telegram.org/bot5194587575:AAFprDquC60qUcCpVhyViIJ5hH5z7VGGRHw/sendVideo?chat_id={sub.telegram}&video=https://21-buxgalteriya.uz/app{post.file.url}&caption={post.text}&parse_mode=html")
                elif post.post_type == 'audio':
                    requests.get(f"https://api.telegram.org/bot5194587575:AAFprDquC60qUcCpVhyViIJ5hH5z7VGGRHw/sendAudio?chat_id={sub.telegram}&audio=https://21-buxgalteriya.uz/app{post.file.url}&caption={post.text}&parse_mode=html")
                elif post.post_type == 'document':
                    requests.get(f"https://api.telegram.org/bot5194587575:AAFprDquC60qUcCpVhyViIJ5hH5z7VGGRHw/sendDocument?chat_id={sub.telegram}&document=https://21-buxgalteriya.uz/app{post.file.url}&caption={post.text}&parse_mode=html")
                else:
                    messages.error(request, "Xatolik( Qaytadan boshlang")
                    return redirect("telegram")
            messages.success(request, f"Xabar {subs.count()}ta obunachiga yuborildi")

        return render(request, 'base/telegram.html', {'profile':profile, 'posts':posts, 'telegrams':teleusers})
    else:
        return render(request, 'error-404.html')
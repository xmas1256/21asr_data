
from http import client
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
import datetime    
from datetime import date  

# Create your models here.
class Profile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    picture = models.ImageField(null=True, blank=True, default='static/profile/user-default.jpg', upload_to='static/profile/')
    phone = models.CharField(max_length=100, null=True, blank=True)
    ADMIN_CHOICES = (
        ('user', 'Oddiy foydalanuvchi'),
        ('superuser', 'Nazoratchi'),
        ('admin', 'Admin')
    )
    status = models.CharField(choices=ADMIN_CHOICES, max_length=200)
    OFFICE_CHOICES = (
        ('1', 'XXI ASR BUXGALTERIYA'),
        ('2', 'XXI ASR KOMPYUTER XIZMATLARI'),
        ('3', 'XXI ASR BUXGALTERIYA XIZMATLARI MARKAZI'),
    )
    office = models.CharField(choices=OFFICE_CHOICES, max_length=200)
    password = models.CharField(max_length=300)

    def __str__(self):
        return self.name    


class Access(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ManyToManyField(Profile)
    name = models.CharField(max_length=255)

class Client(models.Model):
    picture = models.ImageField(null=True, blank=True, default="static/profile/user-default.jpg", upload_to="static/profile/")
    name = models.CharField(max_length=255)
    tin = models.CharField(max_length=255, null=True, blank=True)
    TYPE_CHOICES = (
        ('ytt','YaTT'),
        ('yuridik','Yuridik shaxs'),
        ('jismoniy','Jismoniy shaxs'),
        ('tanirovka','Tanirovka'),
        ('auction','Auksion'),
        ('teacher',"O'qituvchi"),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=255)
    SUB_CHOICES = (
        ('aylanma', 'Aylanma'),
        ('oddiy', 'Oddiy'),
    )
    sub_type = models.CharField(choices=SUB_CHOICES, max_length=255, null=True, blank=True)
    gov_login = models.CharField(max_length=255, null=True, blank=True)
    gov_password = models.CharField(max_length=255, null=True, blank=True)
    jshshir = models.CharField(max_length=255, null=True, blank=True)
    guvohnoma_file = models.FileField(null=True, blank=True, upload_to="static/guvohnoma/")
    guvohnoma_exp = models.DateField(null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    director_tin = models.CharField(max_length=255, null=True, blank=True)
    school = models.CharField(max_length=255, null=True, blank=True)
    work_as = models.CharField(max_length=255, null=True, blank=True)
    phone1 = models.CharField(max_length=255, null=True, blank=True)
    phone2 = models.CharField(max_length=255, null=True, blank=True)
    phone3 = models.CharField(max_length=255, null=True, blank=True)
    telegram = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    key = models.FileField(upload_to='static/keys', null=True, blank=True)
    key_exp = models.DateField(null=True, blank=True)
    passport = models.FileField(null=True, blank=True, upload_to="static/passport/")
    owner = models.CharField(max_length=255, null=True, blank=True)
    tex_number = models.CharField(max_length=255, null=True, blank=True)
    text_series = models.CharField(max_length=255, null=True, blank=True)
    given_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    ustav = models.FileField(null=True, blank=True, upload_to="static/ustav/")
    selfy = models.FileField(null=True, blank=True, upload_to="static/selfy/")
    ruxsatnoma = models.FileField(null=True, blank=True, upload_to="static/ruxsatnoma/")
    texpas = models.FileField(null=True, blank=True, upload_to="static/texpas/")
    order1 = models.CharField(max_length=255, null=True, blank=True)
    order2 = models.CharField(max_length=255, null=True, blank=True)
    order3 = models.CharField(max_length=255, null=True, blank=True)
    auc_login = models.CharField(max_length=255, null=True, blank=True)
    auc_password = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def is_certificate_expired(self):
        if self.guvohnoma_exp:
            dates = datetime.datetime.strptime(str(self.guvohnoma_exp), "%Y-%m-%d").date()
            today = datetime.date.today()
            subs =  dates -today
            if subs.days >=1 and subs.days <=10:
                return 'in_ten_days'
            elif subs.days >10 and subs.days <=30:
                return 'in_a_month'
            elif subs.days > 30:
                return 'active'
            else:
                return 'inactive'
        else:
            return 'not_found'
    @property
    def is_key_expired(self):
        if self.key_exp:
            dates = datetime.datetime.strptime(str(self.key_exp), "%Y-%m-%d").date()
            today = datetime.date.today()
            subs =  dates -today
            if subs.days >=1 and subs.days <=10:
                return 'in_ten_days'
            elif subs.days >10 and subs.days <=30:
                return 'in_a_month'
            elif subs.days > 30:
                return 'active'
            else:
                return 'inactive'
        else:
            return 'not_found'

    @property
    def is_t_expired(self):
        if self.expiry_date:
            dates = datetime.datetime.strptime(str(self.expiry_date), "%Y-%m-%d").date()
            today = datetime.date.today()
            subs =  dates -today
            if subs.days >=1 and subs.days <=10:
                return 'in_ten_days'
            elif subs.days >10 and subs.days <=30:
                return 'in_a_month'
            elif subs.days > 30:
                return 'active'
            else:
                return 'inactive'
        else:
            return 'not_found'





class Service(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True,primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Upload(models.Model):
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    reciever = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='reciever')
    STATUS_CHOICES = (
        ('0','Narxlanmagan'),
        ('5','Bajarilmagan'),
        ('10','Bajarilgan')
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='0')
    payment = models.CharField(max_length=255, null=True, blank=True)
    loaded_date = models.DateTimeField(auto_now_add=True)
    period = models.DateField(null=True, blank=True)
    uploaded_file = models.FileField(upload_to='static/files', null=True, blank=True)
    answer = models.TextField(max_length=350, null=True, blank=True)
    sender = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='sender')
    office = models.CharField(max_length=10)

    class Meta:
        ordering = ['-status', 'period']

class Task(models.Model):
    text = models.TextField(max_length=500)
    given_date = models.DateTimeField(auto_now_add=True)
    duration = models.DateField(null=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255, null=True, blank=True)
    STATUS_CHOICES = (
        ('0', 'Bajarilmagan'),
        ('5', 'Jarayonda'),
        ('10', 'Tugatilgan'),
    )
    client = models.ManyToManyField(Client, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, default='0')
    given_file = models.FileField(upload_to='static/files/task', null=True, blank=True)
    answer_text = models.TextField(max_length=500, null=True, blank=True)
    answer_file = models.FileField(upload_to='static/files/task', null=True, blank=True)

    OFFICE_CHOICES = (
        ('1', 'XXI ASR BUXGALTERIYA'),
        ('2', 'XXI ASR KOMPYUTER XIZMATLARI'),
        ('3', 'XXI ASR BUXGALTERIYA XIZMATLARI MARKAZI'),
    )
    office = models.CharField(choices=OFFICE_CHOICES, max_length=200)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-given_date']

    @property
    def is_past_due(self):
            return date.today() >= self.duration


class SMS(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    STATUS_CHOICES = (
        ('0', 'Raqam kiritilmagan'),
        ('5', 'Raqam xato kiritilgan'),
        ('10', 'Yuborilgan'),
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client.name


class Notes(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    period = models.DateField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.CharField(max_length=255, null=True, blank=True)
    payed = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(max_length=300, null=True, blank=True)
    
    STATUS_CHOICES = (
        ('0', 'Bajarilmagan'),
        ('5', 'Jarayonda'),
        ('10', 'Tugatilgan'),
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, default='0')
    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-period']

class SMStext(models.Model):
    name = models.CharField(max_length=255)
    text = models.TextField(max_length=300)
    
    
class subscriptions(models.Model):
    name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255, null=True, blank=True)
    
class telegramPost(models.Model):
    file = models.FileField(upload_to='static/files/telegram', null=True, blank=True)
    post_type = models.CharField(max_length=255)
    client_type = models.CharField(max_length=255)
    text = models.TextField(max_length=1000, blank=True, null=True)
    
def __str__(self):
        return self.text
    
    
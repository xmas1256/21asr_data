
from django.urls import path

from base.client_views import singleClient
from base.upload_views import NotesPage, cancelService, confirmSerivce, editClient, editNote
from base.views import JismoniyPage, SMSPage, YaTTPage, YuridikPage, deleteClient, auctionPage, telegramPage, createClient, createService, deleteTask, editSMS, editService, finishTask, homePage, logoutPage, monitoringPage, serviceHistoryPage, tanirovkaPage, taskPage, teachersPage, uploadPage, deleteService, viewTaskPage, loginPage
from .user_views import CreateProfile, DeleteProfile, EditProfile, Profiles

urlpatterns = [
    path("login/", loginPage, name='login'),
    path("logout/", logoutPage, name='logout'),
    path("", homePage, name="home"),
    path("monitoring/", monitoringPage, name="monitoring"),
    path("upload/", uploadPage, name="upload"),
    path("create-service/", createService, name="create-service"),
    path("edit-service/<str:pk>", editService, name="edit-service"),
    path("delete-service/<str:pk>", deleteService, name="delete-service"),
    path("task/", taskPage, name="task"),
    path("view-task/<str:pk>", viewTaskPage, name="view-task"),
    path("delete-task/<str:pk>", deleteTask, name="delete-task"),
    path("finish-task/<str:pk>", finishTask, name="finish-task"),
    path("history/", serviceHistoryPage, name="history"),
    path("create-client/", createClient, name="create-client"),
    path("yatt/", YaTTPage, name='yatt'),
    path("jismoniy/", JismoniyPage, name='jismoniy'),
    path("yuridik/", YuridikPage, name='yuridik'),
    path("tanirovka/", tanirovkaPage, name='tanirovka'),
    path("auction/", auctionPage, name='auction'),
    path("teacher/", teachersPage, name='teacher'),


    path("cancel-serivce/<str:pk>", cancelService, name='cancel-service'),
    path("confirm-serivce/<str:pk>", confirmSerivce, name='confirm-service'),

    path("client/<str:pk>", singleClient, name='client'),
    path("edit-client/<str:pk>", editClient, name='edit-client'),

    path("notes/", NotesPage, name='notes'),
    path("note/<str:pk>", editNote, name='note'),
    path("sms/", SMSPage, name='sms'),
    path("edit-sms/<str:pk>", editSMS, name='edit-sms'),

    path("users/", Profiles, name="users"),
    path("create-user/", CreateProfile, name='create-user'),
    path("delete-user/<str:pk>", DeleteProfile, name="delete-profile"),
    path("edit-user/<str:pk>", EditProfile, name="edit-profile"),
    path("delete-client/<str:pk>", deleteClient, name="delete-client"),
    path("telegram/", telegramPage, name="telegram"),
]


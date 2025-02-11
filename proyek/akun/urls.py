from django.urls import path
from . import views

app_name = 'user'

urlpatterns =[
    path('',views.LoginView, name='logi_view'),
    path('register/',views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('daftarakun/', views.DaftarAkun.as_view(), name='daftar_akun'),
    path('jurnal/', views.Jurnal.as_view(), name='jurnal'),
    path('bukubesar/', views.BukuBesar.as_view(), name='buku_besar'),
    path('jurnal/delete/', views.JurnalDelete.as_view(), name='jurnal_delete'),
    path('jurnal/edit/<int:pk>/',views.JurnalEdit.as_view(),name='jurnal_edit'),
    path('labarugi/', views.LabaRugiView.as_view(), name='laba_rugi'),
    path('neraca/', views.NeracaView.as_view(), name='neraca'),
    path('daftarakun/delete/', views.AkunDelete.as_view(), name='akun_delete'),
    path('daftarakun/eidt/<int:pk>/', views.AkunEdit.as_view(), name='akun_edit'),
    path('reset/', views.reset_filter, name='reset_filter'),
    path('beranda/', views.Dashboard.as_view(), name='beranda')
]
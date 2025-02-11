from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm
from django.contrib.auth import authenticate, login, logout
from .models import Profil, JurnalUmum, User
from django.views import View
from django.views.generic import TemplateView
from django.db.models import Sum
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from itertools import chain
from django.urls import reverse_lazy
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.http import HttpResponse
# Create your views here.
def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            msg = 'operator dibuat'
            return redirect('user:logi_view')
        else:
            msg = 'user gagal dibuat'
    else:
        form=SignUpForm()
    return render(request, 'user/login.html', {'form':form, 'msg':msg})

def LoginView(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        form = LoginForm(request.POST)    
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.operator:
                login(request, user)
                return redirect('user:jurnal')
            else:
                msg='invalid credentials'
        else:
            msg='error validating form'
    return render(request, 'user/login.html', {'form':form, 'msg':msg})

def logout_view(request):
    logout(request)
    return redirect('user:logi_view')

class DaftarAkun(View):
    def get(self, request, *args, **kwargs):
        profil_list = Profil.objects.filter(operator=self.request.user)
        jurnal_list = JurnalUmum.objects.filter(operator=self.request.user)
        user_list = User.objects.all()
        pos_choices = Profil._meta.get_field('pos').choices
        master_choices = Profil._meta.get_field('master_akun').choices
        sn_choices = Profil._meta.get_field('saldo_normal').choices
        return render(request, 'user/daftarakun.html', {
            'profil_list':profil_list, 
            'jurnal_list':jurnal_list,
            'user_list':user_list,
            'pos_choices': pos_choices,
            'master_choices': master_choices,
            'sn_choices': sn_choices,
            })
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            nama_akun = request.POST.get('nama_akun')
            nomor = request.POST.get('nomor')
            pos = request.POST.get('pos')
            master_akun = request.POST.get('master_akun')
            saldo_normal = request.POST.get('saldo_normal')
            operator = request.user
            
            Profil.objects.create(nama_akun=nama_akun, operator=operator, nomor=nomor, pos=pos, master_akun=master_akun, saldo_normal=saldo_normal)
        return redirect('user:daftar_akun')

class Jurnal(TemplateView):
    template_name = 'user/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profil_list = Profil.objects.filter(operator=self.request.user)

        # ambil parameter tanggal
        tanggal = self.request.GET.get('tanggal')
        bulan = self.request.GET.get('bulan')
        tahun = self.request.GET.get('tahun')

        if tanggal:
            self.request.session['filter_tanggal'] = tanggal
        elif bulan:
            self.request.session['filter_bulan'] = bulan
        elif tahun:
            self.request.session['filter_tahun'] = tahun

        tanggal = self.request.session.get('filter_tanggal', None)
        bulan = self.request.session.get('filter_bulan', None)
        tahun = self.request.session.get('filter_tahun', None)

        jurnal_list = JurnalUmum.objects.filter(operator=self.request.user)

        if tanggal:
            jurnal_list = jurnal_list.filter(tanggal=tanggal)
        elif bulan:
            jurnal_list = jurnal_list.filter(tanggal__month=bulan)
        elif tahun:
            jurnal_list = jurnal_list.filter(tanggal__year=tahun)

        user_list = User.objects.all()
        total_debit = jurnal_list.aggregate(total_debit=Sum('debit'))['total_debit'] or 0
        total_kredit = jurnal_list.aggregate(total_kredit=Sum('kredit'))['total_kredit'] or 0
        balance = total_debit - total_kredit
        context['profil_list'] = profil_list
        context['jurnal_list'] = jurnal_list
        context['user_list']= user_list
        context['total_debit'] = total_debit
        context['total_kredit'] = total_kredit
        context['balance'] = balance
        context['filter_tanggal'] = tanggal
        context['filter_bulan'] = bulan
        context['filter_tahun'] = tahun
        return context

    def post(self, request, *args, **kwargs):
        if request.method =='POST':
            akun_id = request.POST.get('akun')
            operator = request.user
            tanggal = request.POST.get('tanggal')
            uraian = request.POST.get('uraian')
            debit = request.POST.get('debit') or 0
            kredit = request.POST.get('kredit') or 0

            try:
                akun=Profil.objects.get(id=akun_id)
            except Profil.DoesNotExist:
                return redirect('user:jurnal')
            
            try:
                debit = int(debit)
                kredit = int(kredit)
            except ValueError:
                return redirect('user:jurnal')

            JurnalUmum.objects.create(akun=akun, debit=debit, kredit=kredit,tanggal=tanggal, uraian=uraian, operator=operator)
        return redirect('user:jurnal')
    
class JurnalDelete(View):
    def post(self, request, *args, **kwargs):
        jurnal_id = request.POST.get('jurnal_id')
        try:
            jurnal = JurnalUmum.objects.get(id=jurnal_id)
            jurnal.delete()
        except JurnalUmum.DoesNotExist:
            return redirect('user:jurnal')
        return redirect('user:jurnal')

class AkunDelete(View):
    def post(self, request, *args, **kwargs):
        akun_id = request.POST.get('akun_id')
        try:
            akun = Profil.objects.get(id=akun_id)
            akun.delete()
        except Profil.DoesNotExist:
            return redirect('user:daftar_akun')
        return redirect('user:daftar_akun')
    
class JurnalEdit(UpdateView):
    model=JurnalUmum
    fields='__all__'
    success_url=reverse_lazy('user:jurnal')

class AkunEdit(UpdateView):
    model=Profil
    fields='__all__'
    success_url=reverse_lazy('user:daftar_akun')
    
class BukuBesar(TemplateView):
    template_name ='user/bukubesar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        tanggal = self.request.session.get('filter_tanggal', None)
        bulan = self.request.session.get('filter_bulan', None)
        tahun = self.request.session.get('filter_tahun', None)

        accounts = Profil.objects.filter(operator=self.request.user)
        jurnal_list = JurnalUmum.objects.filter(operator=self.request.user)

        if tanggal:
            jurnal_list = jurnal_list.filter(tanggal=tanggal)
        elif bulan:
            jurnal_list = jurnal_list.filter(tanggal__month=bulan)
        elif tahun:
            jurnal_list = jurnal_list.filter(tanggal__year=tahun)
        
        ledgers = {}

        for account in accounts:
            transactions = jurnal_list.filter(akun=account)
            total_debit = transactions.aggregate(total_debit = Sum('debit'))['total_debit'] or 0
            total_kredit = transactions.aggregate(total_kredit = Sum('kredit'))['total_kredit'] or 0
            balance = 0
            transaction_list = []

            for transaction in transactions:
                balance += transaction.debit - transaction.kredit
                transaction_list.append({
                    'debit': transaction.debit,
                    'kredit':transaction.kredit,
                    'uraian': transaction.uraian,
                    'balance': balance
                })
            ledgers [account.nama_akun] ={
                'transactions': transaction_list,
                'total_debit':total_debit,
                'total_kredit':total_kredit,
                'balance':total_debit - total_kredit
            }

        context ['ledgers'] = ledgers
        return context
    
class LabaRugiView(TemplateView):
    template_name = 'user/laba_rugi.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tanggal = self.request.session.get('filter_tanggal', None)
        bulan = self.request.session.get('filter_bulan', None)
        tahun = self.request.session.get('filter_tahun', None)

        accounts = Profil.objects.filter(pos='laba rugi', operator=self.request.user)
        jurnal_list = JurnalUmum.objects.filter(operator=self.request.user)

        if tanggal:
            jurnal_list = jurnal_list.filter(tanggal=tanggal)
        elif bulan:
            jurnal_list = jurnal_list.filter(tanggal__month=bulan)
        elif tahun:
            jurnal_list = jurnal_list.filter(tanggal__year=tahun)

        ledgers_pendapatan = {}
        ledgers_beban = {}
        total_pendapatan = 0
        total_beban = 0

        for account in accounts:
            transactions = jurnal_list.filter(akun=account)
            total_debit = transactions.aggregate(total_debit=Sum('debit'))['total_debit'] or 0
            total_kredit = transactions.aggregate(total_kredit=Sum('kredit'))['total_kredit'] or 0
            balance = total_debit - total_kredit

            if account.master_akun == 'pendapatan':
                ledgers_pendapatan[account.nama_akun] = {
                    'total_debit': total_debit,
                    'total_kredit': total_kredit,
                    'balance': abs(balance)
                }
                total_pendapatan += total_kredit
            elif account.master_akun == 'beban':
                ledgers_beban[account.nama_akun] = {
                    'total_debit': total_debit,
                    'total_kredit': total_kredit,
                    'balance': abs(balance)
                }
                total_beban += total_debit

        # Hitung laba rugi
        laba_rugi = total_pendapatan - total_beban

        context['ledgers_pendapatan'] = ledgers_pendapatan
        context['ledgers_beban'] = ledgers_beban
        context['total_pendapatan'] = total_pendapatan
        context['total_beban'] = total_beban
        context['laba_rugi'] = laba_rugi

        return context

class NeracaView(TemplateView):
    template_name='user/neraca.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = Profil.objects.filter(pos='neraca', operator=self.request.user)
        jurnal_list = JurnalUmum.objects.filter(operator=self.request.user)
        ledgers_aktiva = {}
        ledgers_passiva = {}
        total_aktiva = 0
        total_passiva = 0

        for account in accounts:
            transactions = jurnal_list.filter(akun=account)
            total_debit = transactions.aggregate(total_debit=Sum('debit'))['total_debit'] or 0
            total_kredit = transactions.aggregate(total_kredit=Sum('kredit'))['total_kredit'] or 0
            balance = total_debit - total_kredit

            if account.master_akun == 'aktiva':
                ledgers_aktiva[account.nama_akun] ={
                    'total_debit': total_debit,
                    'total_kredit': total_kredit,
                    'balance': abs(balance)
                }
                total_aktiva += balance
            elif account.master_akun == 'passiva':
                ledgers_passiva[account.nama_akun] ={
                    'total_debit':total_debit,
                    'total_kredit':total_kredit,
                    'balance': abs(balance)
                }
                total_passiva += balance

        neraca = total_aktiva + total_passiva
        context['ledgers_aktiva'] = ledgers_aktiva
        context['ledgers_passiva'] = ledgers_passiva
        context['total_aktiva'] = total_aktiva
        context['total_passiva'] = total_passiva
        context['neraca'] = neraca

        return context
    
def reset_filter(request):
    if 'filter_tanggal' in request.session:
        del request.session['filter_tanggal']
    if 'filter_bulan' in request.session:
        del request.session['filter_bulan']
    if 'filter_tahun' in request.session:
        del request.session['filter_tahun']
    return redirect('user:jurnal')

class Dashboard(View):
    Template_name = 'user/beranda.html'

    def get(self, request, *args, **kwargs):
        accounts = Profil.objects.filter(pos='laba rugi', operator = self.request.user)
        jurnal_list = JurnalUmum.objects.filter(operator= self.request.user)

        tanggal = self.request.session.get('filter_tanggal', None)
        bulan = self.request.session.get('filter_bulan', None)
        tahun = self.request.session.get('filter_tahun', None)

        if tanggal:
            jurnal_list = jurnal_list.filter(tanggal=tanggal)
        elif bulan:
            jurnal_list = jurnal_list.filter(tanggal__month=bulan)
        elif tahun:
            jurnal_list = jurnal_list.filter(tanggal__year=tahun)

        total_pendapatan = 0

        for account in accounts:
            transactions = jurnal_list.filter(akun=account)
            total_kredit = transactions.aggregate(total_kredit=Sum('kredit'))['total_kredit'] or 0

            if account.master_akun == 'pendapatan':
                total_pendapatan += total_kredit

        # membuat diagram
        buf = io.BytesIO()
        fig, ax = plt.subplots()
        ax.bar(['pendapatan'], [total_pendapatan], color='blue')
        ax.set_title(total_pendapatan)
        ax.set_ylabel('Jumlah')
        plt.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)

        context={
            'chart': uri,
            'total_pendapatan': total_pendapatan
        }

        return render(request, self.Template_name, context)
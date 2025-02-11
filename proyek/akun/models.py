from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    operator = models.BooleanField('Operator', default=False)

class Profil(models.Model):
    nama_akun = models.CharField(max_length=50)
    nomor = models.CharField(max_length=50)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    pos = models.CharField(max_length=30, choices=[
        ('laba rugi', 'laba rugi'),
        ('neraca', 'neraca')
    ])
    master_akun = models.CharField(max_length=30, choices=[
        ('aktiva', 'aktiva'),
        ('passiva', 'passiva'),
        ('pendapatan', 'pendapatan'),
        ('beban', 'beban')
    ])
    saldo_normal = models.CharField(max_length=30, choices=[
        ('debit','debit'),
        ('kredit','kredit'),
    ])

    def __str__(self):
        return self.nama_akun   

class JurnalUmum(models.Model):
    akun = models.ForeignKey(Profil, on_delete=models.CASCADE)
    uraian = models.CharField(max_length=50)
    kredit = models.IntegerField(blank=True, null=True) 
    debit = models.IntegerField(blank=True, null=True)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    tanggal = models.DateField()

    def __str__(self):
        return self.uraian

    
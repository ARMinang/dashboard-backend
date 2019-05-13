from django.db import models


# Create your models here.
class Iuran(models.Model):
    nilai_penerimaan = models.DecimalField(max_digits=20, decimal_places=2)
    nilai_iuran = models.DecimalField(max_digits=20, decimal_places=2)
    denda = models.DecimalField(max_digits=20, decimal_places=2)
    npp = models.CharField(max_length=8)
    nama_perusahaan = models.CharField(max_length=200)
    kode_perusahaan = models.CharField(max_length=20)
    kode_divisi = models.CharField(max_length=3)
    channel = models.CharField(max_length=7)
    kode_penerimaan = models.CharField(max_length=20)
    tgl_bayar = models.DateField(auto_now=False, auto_now_add=False)
    kode_pembina = models.CharField(max_length=8)


class Tk(models.Model):
    nomor_pegawai = models.CharField(max_length=32, blank=True, null=True)
    nama_tk = models.CharField(max_length=64, blank=False, null=False)
    tgl_kepesertaan = models.DateField(auto_now=False, auto_now_add=False)
    kpj = models.CharField(max_length=11)
    tgl_lahir = models.DateField(auto_now=False, auto_now_add=False)
    npp = models.CharField(max_length=8, blank=False, null=False)
    kode_pembina = models.CharField(max_length=8, blank=False, null=False)

    class Meta:
        unique_together = ("kpj", "npp", "tgl_kepesertaan")

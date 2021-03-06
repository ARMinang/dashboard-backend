from pemasaran.models import Iuran, Tk, Npp
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

import datetime


class IuranBulanan(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        current_year = datetime.datetime.today().strftime("%Y")
        iuran_qs = Iuran.objects.filter(tgl_bayar__year=current_year)
        iuran_per_month = iuran_qs.values('nilai_penerimaan')\
                                  .annotate(month=TruncMonth('tgl_bayar'))\
                                  .values('month')\
                                  .annotate(jml_bayar=Sum('nilai_penerimaan'))\
                                  .values('month', 'jml_bayar')\
                                  .order_by('month')
        return Response(iuran_per_month)


class IuranPerAr(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        current_year = datetime.datetime.today().strftime("%Y")
        iuran_qs = Iuran.objects.filter(tgl_bayar__year=current_year)
        iuran_per_month = iuran_qs.values('nilai_penerimaan')\
                                  .annotate(month=TruncMonth('tgl_bayar'))\
                                  .values('month')\
                                  .annotate(jml_bayar=Sum('nilai_penerimaan'))\
                                  .values(
                                      'month', 'kode_pembina', 'jml_bayar'
                                  ).order_by('month', 'kode_pembina')
        return Response(iuran_per_month)


class TkPerAr(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        current_year = datetime.datetime.today().strftime("%Y")
        tk_qs = Tk.objects.filter(tgl_kepesertaan__year=current_year)
        tk_per_month = tk_qs.annotate(month=TruncMonth('tgl_kepesertaan'))\
                            .values('month')\
                            .annotate(jml_tk=Count('id'))\
                            .values('month', 'kode_pembina', 'jml_tk')\
                            .order_by('month', 'kode_pembina')
        return Response(tk_per_month)


class TkBulanan(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        current_year = datetime.datetime.today().strftime("%Y")
        tk_qs = Tk.objects.filter(tgl_kepesertaan__year=current_year)
        tk_per_month = tk_qs.annotate(month=TruncMonth('tgl_kepesertaan'))\
                            .values('month')\
                            .annotate(jml_tk=Count('id'))\
                            .values('month', 'jml_tk')\
                            .order_by('month')
        return Response(tk_per_month)


class NppBulananPerArk(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        current_year = datetime.datetime.today().strftime("%Y")
        npp_qs = Npp.objects.filter(keps_awal__year=current_year)
        npp_per_month = npp_qs.annotate(month=TruncMonth('keps_awal'))\
                              .values('month', 'kode_pembina')\
                              .annotate(jml_npp=Count('id'))\
                              .values('month', 'kode_pembina', 'jml_npp')\
                              .order_by('month', 'kode_pembina')
        return Response(npp_per_month)


class NppBulanan(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        current_year = datetime.datetime.today().strftime("%Y")
        npp_qs = Npp.objects.filter(keps_awal__year=current_year)
        npp_per_month = npp_qs.annotate(month=TruncMonth('keps_awal'))\
                              .values('month')\
                              .annotate(jml_npp=Count('id'))\
                              .values('month', 'jml_npp')\
                              .order_by('month')
        aktif_qs = Npp.objects.filter(blth_na=None).count()
        npp_ret = {"penambahan_npp": npp_per_month, "total_npp": aktif_qs}
        return Response(npp_ret)

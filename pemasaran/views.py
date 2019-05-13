from pemasaran.models import Iuran, Tk
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

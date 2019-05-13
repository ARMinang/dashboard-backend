from rest_framework import serializers
from pemasaran.models import Iuran


class IuranSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(IuranSerializer, self).__init__(many=many, *args, **kwargs)

        class Meta:
            model = Iuran
            fields = ('pk', 'npp', 'nilai_penerimaan', 'nilai_iuran', 'denda',
                'nama_perusahaan', 'kode_perusahaan', 'kode_divisi', 'channel',
                'kode_penerimaan', 'tgl_bayar'
            )
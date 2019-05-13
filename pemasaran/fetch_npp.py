from pemasaran.download_alamat import fetch_alamat
from pemasaran.download_mkro import download_all
from pemasaran.download_knr1415 import download_all_ar
import pandas as pd
from pemasaran.models import Npp


def fetch_all_npp():
    data_eps, data_mkar = download_all()
    data_alamat = fetch_alamat()
    data_nik = download_all_ar()
    pd1 = pd.DataFrame(data_alamat)
    pd2 = pd.DataFrame(data_mkar)
    pd3 = pd.DataFrame(data_nik)
    integer_header = [
        "NIK_VALID_AKTIF", "NIK_INVALID_AKTIF", "NIK_VALID_NA",
        "NIK_INVALID_NA"
    ]
    for c in integer_header:
        pd3[c] = pd.to_numeric(pd3[c], downcast="integer")
    result = pd1.merge(pd2, on="NPP", how="left")
    result_nik = result.merge(pd3, on="NPP", how="left")
    result_dict = result_nik.to_dict()
    instances = []
    for result in result_dict:
        ex_npp = Npp.objects.filter(
            npp=result["npp"],
            kode_divisi=result["kode_divisi"]
        )
        if len(ex_npp) == 0:
            instances.append(result)
    if instances:
        Npp.objects.bulk_create(
            [Npp(**data) for data in instances]
        )

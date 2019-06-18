from pemasaran.download_alamat import fetch_alamat
from pemasaran.download_mkro import download_all
import pandas as pd
from pemasaran.models import Npp
import pydash as lo


FILTER = [
    "npp", "kode_divisi", "kode_perusahaan", "nama_perusahaan", "keps_awal",
    "blth_na", "kode_paket", "kode_ilo", "alamat", "nama_kontak",
    "handphone_kontak", "email_kontak", "kode_pembina"
]


def fetch_all_npp():
    data_eps, data_mkar = download_all()
    data_alamat = fetch_alamat()
    pd1 = pd.DataFrame(data_alamat)
    pd2 = pd.DataFrame(data_mkar)
    result = pd1.merge(pd2, on="npp", how="left")
    result["keps_awal"] = result["keps_awal"].dt.strftime("%Y-%m-%d")
    result["blth_na"] = result["blth_na"].dt.strftime("%Y-%m-%d")
    result["kode_paket"].fillna("2P", inplace=True)
    result["blth_na"] = result["blth_na"].where(
        (pd.notnull(result["blth_na"])), None
    )
    result.drop_duplicates(subset=["npp", "kode_divisi"], inplace=True)
    result_dict = result.to_dict('records')
    instances = []
    for result in result_dict:
        ex_npp = Npp.objects.filter(
            npp=result["npp"],
            kode_divisi=result["kode_divisi"]
        )
        if len(ex_npp) == 0:
            result_filtered = lo.pick(result, FILTER)
            if result_filtered["keps_awal"] == "NaT":
                result_filtered["keps_awal"] = None
            if result_filtered["blth_na"] == "NaT":
                result_filtered["blth_na"] = None
            if (
                result_filtered["npp"] is not None and
                result_filtered["kode_divisi"] is not None and
                result_filtered["keps_awal"] is not None
            ):
                instances.append(result_filtered)
    if instances:
        Npp.objects.bulk_create(
            [Npp(**data) for data in instances]
        )

import requests
import threading
import xml.etree.cElementTree as etree

from queue import Queue
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pemasaran.download_knr1415 import ALL_AR


URL_MKRO = (
    "http://rptserver.bpjsketenagakerjaan.go.id/reports/rwservlet/setauth?butt"
    "on=Submit&username=smile&password=smilekanharimu&authtype=D&mask=GQ%253D%"
    "253D&isjsp=no&database=dboltp&nextpage=destype%3Dcache%26desformat%3DXML%"
    "26report%3DKNR8801.rdf%26userid%3D%2Fdata%2Freports%2Fkn%26%26P_KANTOR%3D"
    "'D00'%26P_PEMBINA%3D'{user}'%26P_KODE_KANTOR%3D'D00'%26P_PERIODE%3D'"
    "{periode}'%26P_USER%3D'{user}'%26P_ROLE%3D'8'"
)

HEADER_MKRO = [
    "CS_NOMOR", "NPP", "KODE_DIVISI", "KODE_KEPESERTAAN", "NAMA_PERUSAHAAN",
    "KEPS_AWAL", "KEPS_JP", "BLTH_NA", "KODE_PAKET", "PENAMBAHAN_TK",
    "PENGURANGAN_TK", "TK_AKTIF", "TK_NA", "BLTH_DUTK", "BLTH_REKON",
    "CHANNEL_DUTK", "NILAI_IURAN", "TOTAL_TERIMA_IUR", "ITW", "IJT", "IDM"
]

INT_HEADER = [
    "CS_NOMOR", "PENAMBAHAN_TK", "PENGURANGAN_TK", "TK_AKTIF", "TK_NA",
    "NILAI_IURAN", "TOTAL_TERIMA_IUR"
]

HEADER_EXCEL = [
    "No.", "NPP", "Div", "Kode Kepesertaan", "Nama Perusahaan", "Keps. Awal",
    "Keps. JP", "BLTH NA", "Paket", "Penambahan TK", "Pengurangan TK",
    "TK Aktif", "TK NA", "BLTH DUTK", "BLTH Rekon", "Channel", "Iuran",
    "Total Iuran", "ITW", "IJT", "IDM", "Kode Pembina"
]

CUR_HEADER = [
    "NILAI_IURAN", "TOTAL_TERIMA_IUR"
]

BLTH_HEADER = [
    "keps_awal", "keps_jp", "blth_dutk", "blth_rekon", "blth_na"
]


def trunc_datetime(blth):
    return blth.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def convert_to_date(timestamp):
    try:
        return trunc_datetime(datetime.strptime(timestamp, "%m-%Y"))
    except ValueError:
        return None


def fetch_mkro(data):
    url = URL_MKRO.format(**data)
    req = requests.get(url, stream=True)
    if req.url != url:
        print("Something went wrong, redirected to %s" % req.url)
    if req.status_code == 200:
        req.raw.decode_content = True
        context = iter(etree.iterparse(req.raw, events=("start", "end")))
        event, root = next(context)
        data_eps = []
        data_mkar = []
        for event, elem in context:
            if event == "end" and elem.tag == "G_NAMA_KANTOR":
                for child in elem:
                    for list_npp in child.findall("G_NPP"):
                        singleNpp = dict(
                            (
                                e.lower(),
                                list_npp.find(e).text
                                if list_npp.find(e) is not None else ""
                            )
                            for e in HEADER_MKRO
                        )
                        singleNpp["kode_pembina"] = data["user"]
                        intSingle = dict(
                            (
                                k,
                                float(v)
                                if k in INT_HEADER and v is not None else v
                            ) for k, v in singleNpp.items()
                        )
                        all_converted = dict(
                            (
                                k,
                                convert_to_date(v)
                                if k in BLTH_HEADER and v is not None
                                else v
                            ) for k, v in intSingle.items()
                        )
                        to_eps = create_eps_list(all_converted) if\
                            all_converted["blth_na"] == "-" or\
                            all_converted["blth_na"] is None else None
                        if to_eps and to_eps["blth_na"] == "-":
                            to_eps["blth_na"] = None
                        data_eps.append(to_eps) if to_eps else None
                        data_mkar.append(all_converted)
        return data_mkar, data_eps


def create_eps_list(single):
    if single["blth_rekon"]:
        if single["blth_rekon"] < trunc_datetime(datetime.now()) and\
            single["blth_rekon"] >= trunc_datetime(
            datetime.now() - relativedelta(months=+2)
        ):
            return single
    return None


def do_check(q, data_eps, data_mkar):
    while True:
        to_fetch = q.get()
        mkar, eps = fetch_mkro(to_fetch)
        data_eps.extend(eps)
        data_mkar.extend(mkar)
        q.task_done()


def download_all():
    data_eps = []
    data_mkar = []
    q = Queue(maxsize=0)
    for i in range(1):
        t = threading.Thread(target=do_check, args=(q, data_eps, data_mkar))
        t.setDaemon(True)
        t.start()
    for user in ALL_AR:
        to_fetch = dict()
        to_fetch["user"] = user
        to_fetch["periode"] = datetime.today().strftime("%d-%m-%Y")
        q.put(to_fetch)
    q.join()
    return data_eps, data_mkar

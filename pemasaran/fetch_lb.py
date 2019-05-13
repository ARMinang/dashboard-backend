import datetime
import requests

import xml.etree.cElementTree as etree
from celery.utils.log import get_task_logger

from pemasaran.models import Iuran

logger = get_task_logger(__name__)

URL_IURAN = (
    "http://rptserver.bpjsketenagakerjaan.go.id/reports/rwservlet/setauth?"
    "button=Submit&username=smile&password=smilekanharimu&authtype=D&mask="
    "GQ%253D%253D&isjsp=no&database=dboltp&nextpage=destype%3Dcache%26desf"
    "ormat%3DXML%26report%3DKNR1002.rdf%26userid%3D%2Fdata%2Freports%2Fkn%"
    "26%26P_KODE_KANTOR%3D'D00'%26P_PERIODE1%3D'{periode1}'%26P_PERIODE2%3"
    "D'{periode2}'%26P_USER%3D'{user}'%26P_ROLE%3D'8'%26P_KONSOLIDASI%3D''"
)

HEADER_IURAN = [
    "NILAI_PENERIMAAN",
    "NILAI_IURAN",
    "DENDA",
    "NPP",
    "NAMA_PERUSAHAAN",
    "KODE_PERUSAHAAN",
    "KODE_DIVISI",
    "CHANNEL",
    "KODE_PENERIMAAN",
    "TGL_BAYAR",
]


def convert_to_datetime(tanggal, format="%d-%b-%y"):
    date_object_str = None
    try:
        date_object = datetime.datetime.strptime(tanggal, format)
        date_object_str = datetime.datetime.strftime(date_object, "%Y-%m-%d")
    except ValueError:
        date_object_str = None
    return date_object_str


def fetch_iuran(data):
    url = URL_IURAN.format(**data)
    req = requests.get(url, stream=True)
    logger.info("Status Code: %s" % req.status_code)
    if req.url != url:
        logger.info("Fetching data error, redirected to %s" % req.url)
    elif req.status_code == 200:
        req.raw.decode_content = True
        context = iter(etree.iterparse(req.raw, events=("start", "end")))
        event, root = next(context)
        instances = []
        for event, elem in context:
            if event == "end" and elem.tag == "G_PEMBINA":
                for child in elem:
                    if child.tag == "PEMBINA":
                        kode_pembina = child.text
                    for list_npp in child.findall("G_NPP"):
                        singleIuran = dict(
                            (
                                e.lower(),
                                list_npp.find(e).text
                                if list_npp.find(e) is not None
                                else "",
                            )
                            for e in HEADER_IURAN
                        )
                        if "tgl_bayar" in singleIuran:
                            singleIuran["tgl_bayar"] = convert_to_datetime(
                                singleIuran["tgl_bayar"]
                            )
                        singleIuran["kode_pembina"] = kode_pembina
                        instances.append(singleIuran)
                root.clear()
        if instances:
            Iuran.objects.all().delete()
            Iuran.objects.bulk_create([Iuran(**data) for data in instances])
    else:
        logger.info("Failed to fetch data: %s" % req.status_code)

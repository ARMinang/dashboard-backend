import requests
import threading
import xml.etree.cElementTree as etree

from queue import Queue


URL_NIK = (
    "http://rptserver.bpjsketenagakerjaan.go.id/reports/rwservlet/setauth?butt"
    "on=Submit&username=smile&password=smilekanharimu&authtype=D&mask=GQ%253D%"
    "253D&isjsp=no&database=dboltp&nextpage=destype%3Dcache%26desformat%3DXML%"
    "26report%3DKNR1415.rdf%26userid%3D%2Fdata%2Freports%2Fkn%26%26P_KODE_KANT"
    "OR%3D%27D00%27%26P_KODE_USER%3D%27{user}%27"
)

HEADER_NIK = [
    "NPP", "NIK_VALID_AKTIF", "NIK_INVALID_AKTIF", "NIK_VALID_NA",
    "NIK_INVALID_NA", "STATUS_NPWP"
]

ALL_AR = [
    "AK153580", "ED160810", "FA165960", "FE174690", "GR153600", "MU165970",
    "NI273920", "RA174700", "RA184220", "RA248900", "SE251740", "SU122530",
    "SU244930", "RO259060"
]


def fetch_report(data):
    url = URL_NIK.format(**data)
    req = requests.get(url, stream=True)
    if req.url != url:
        print("Something went wrong, redirected to %s" % req.url)
    if req.status_code == 200:
        req.raw.decode_content = True
        context = iter(etree.iterparse(req.raw, events=("start", "end")))
        event, root = next(context)
        data_nik = []
        for event, elem in context:
            if event == "end" and elem.tag == "G_KODE_KANTOR_CABANG":
                for child in elem:
                    for list_npp in child.findall("G_CS_1"):
                        singleNpp = dict(
                            (
                                e,
                                list_npp.find(e).text
                                if list_npp.find(e) is not None else ""
                            )
                            for e in HEADER_NIK
                        )
                        data_nik.append(singleNpp)
        return data_nik


def do_check(q, list_data):
    while True:
        to_get = q.get()
        per_npp = fetch_report(to_get)
        list_data.extend(per_npp)
        q.task_done()


def download_all_ar():
    list_data = []
    q = Queue(maxsize=0)
    for i in range(1):
        t = threading.Thread(target=do_check, args=(q, list_data))
        t.setDaemon(True)
        t.start()
    for user in ALL_AR:
        to_fetch = dict()
        to_fetch["user"] = user
        q.put(to_fetch)
    q.join()
    return list_data

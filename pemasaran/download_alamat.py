import requests
import xml.etree.cElementTree as etree

from datetime import datetime


URL_ALAMAT = (
    "http://rptserver.bpjsketenagakerjaan.go.id/reports/rwservlet/setauth?butt"
    "on=Submit&username=smile&password=smilekanharimu&authtype=D&mask=GQ%253D%"
    "253D&isjsp=no&database=dboltp&nextpage=destype%3Dcache%26desformat%3DXML%"
    "26report%3DKNR1021.rdf%26userid%3D%2Fdata%2Freports%2Fkn%26%26P_KODE_KANT"
    "OR%3D%27D00%27%26P_PERIODE%3D%27{periode}%27%26P_KODE_USER%3D%27%27%26P_R"
    "OLE%3D%2710%27%26P_KONSOLIDASI%3D%27%27"
)

HEADER_ALAMAT = [
    "NPP", "KODE_PERUSAHAAN", "KODE_ILO", "RATE_JKK", "ALAMAT",
    "NAMA_KONTAK", "HANDPHONE_KONTAK", "EMAIL_KONTAK"
]


def fetch_alamat():
    today = dict()
    today["periode"] = datetime.today().strftime("%d-%m-%Y")  # "28-02-2019"
    url = URL_ALAMAT.format(**today)
    req = requests.get(url, stream=True)
    if req.url != url:
        print("Something went wrong, redirected to %s" % req.url)
    if req.status_code == 200:
        req.raw.decode_content = True
        context = iter(etree.iterparse(req.raw, events=("start", "end")))
        event, root = next(context)
        data_alamat = []
        for event, elem in context:
            if event == "end" and elem.tag == "G_KODE_KANTOR":
                for child in elem:
                    for list_npp in child.findall("G_1"):
                        singleNpp = dict(
                            (
                                e,
                                list_npp.find(e).text
                                if list_npp.find(e) is not None else ""
                            )
                            for e in HEADER_ALAMAT
                        )
                        intSingle = dict(
                            (
                                k,
                                float(v)
                                if k == "RATE_JKK" and v is not None else v
                            ) for k, v in singleNpp.items()
                        )
                        data_alamat.append(intSingle)
        return data_alamat


def do_check(data_mkar):
    mkar = fetch_alamat()
    data_mkar.extend(mkar)

import requests
import xml.etree.cElementTree as etree
import asyncio
from aiohttp import ClientSession
import aiohttp
from pemasaran.models import Tk
from pemasaran.fetch_lb import convert_to_datetime
from celery.utils.log import get_task_logger
import pandas as pd

logger = get_task_logger(__name__)

URL_TK_NPP = (
    "http://rptserver.bpjsketenagakerjaan.go.id/reports/rwservlet/setauth?butt"
    "on=Submit&username=smile&password=smilekanharimu&authtype=D&mask=GQ%253D%"
    "253D&isjsp=no&database=dboltp&nextpage=destype%3Dcache%26desformat%3DXML%"
    "26report%3DKNR2201.rdf%26userid%3D%2Fdata%2Freports%2Fkn%26%26P_KODE_KANT"
    "OR%3D'D00'%26P_PERIODE%3D'{periode}'%26P_NPP%3D'{npp}'%26P_KODE_USER%3D'{"
    "user}'%26P_ROLE%3D'8'%26P_KONSOLIDASI%3D''"
)

HEADER_TK = [
    "NOMOR_PEGAWAI", "NAMA_TK", "TGL_KEPESERTAAN", "KPJ", "TGL_LAHIR",
]

URL_TK_REKAP = (
    "http://rptserver.bpjsketenagakerjaan.go.id/reports/rwservlet/setauth?butt"
    "on=Submit&username=smile&password=smilekanharimu&authtype=D&mask=GQ%253D%"
    "253D&isjsp=no&database=dboltp&nextpage=destype%3Dcache%26desformat%3DXML%"
    "26report%3DKNR1025.rdf%26userid%3D%2Fdata%2Freports%2Fkn%26%26P_KODE_KANT"
    "OR%3D%27D00%27%26P_PERIODE%3D%27{periode}%27%26P_USER%3D%27%27%26P_"
    "ROLE%3D%278%27%26P_KONSOLIDASI%3D%27%27"
)

HEADER_NPP = [
    "NPP", "TOTAL_TK"
]


def fetch_tk_rekap(data):
    all_tk = []
    url = URL_TK_REKAP.format(**data)
    req = requests.get(url, stream=True)
    if req.url != url:
        logger.info("fetching data error, redirect to %s" % req.url)
    elif req.status_code == 200:
        req.raw.decode_content = True
        context = iter(etree.iterparse(req.raw, events=("start", "end")))
        event, root = next(context)
        for event, elem in context:
            if event == "end" and elem.tag == "G_KODE_KANTOR":
                for child in elem:
                    if child.tag == "PEMBINA":
                        kode_pembina = child.text
                    for list_tk in child.findall("G_NPP"):
                        single_npp = dict(
                            (
                                e.lower(),
                                list_tk.find(e).text
                                if list_tk.find(e) is not None
                                else "",
                            )
                            for e in HEADER_NPP
                        )
                        single_npp["user"] = kode_pembina
                        single_npp["periode"] = data["periode"]
                        all_tk.append(single_npp)
                root.clear()
    else:
        logger.info("Failed to fetch data: %s" % req.status_code)
        return None
    return all_tk


async def fetch_tk_per_npp(data, session):
    url = URL_TK_NPP.format(**data)
    count = 0
    while True:
        try:
            async with session.get(url) as response:
                instances = []
                content = await response.read()
                context = etree.fromstring(content)
                for elem in context.iter("G_PERUSAHAAN"):
                    for child in elem:
                        if child.tag == "KODE_PEMBINA":
                            kode_pembina = child.text
                        if child.tag == "NPP":
                            npp = child.text
                        for list_tk in child.findall("G_KPJ"):
                            single_tk = dict(
                                (
                                    e.lower(),
                                    list_tk.find(e).text
                                    if list_tk.find(e) is not None
                                    else "",
                                )
                                for e in HEADER_TK
                            )
                            single_tk["tgl_kepesertaan"] = convert_to_datetime(
                                single_tk["tgl_kepesertaan"], "%d-%b-%y"
                            )
                            single_tk["tgl_lahir"] = convert_to_datetime(
                                single_tk["tgl_lahir"], "%d-%b-%y"
                            )
                            single_tk["kode_pembina"] = kode_pembina
                            single_tk["npp"] = npp
                            ex_item = Tk.objects.filter(
                                npp=single_tk["npp"],
                                kpj=single_tk["kpj"],
                                tgl_kepesertaan=single_tk["tgl_kepesertaan"]
                            )
                            if len(ex_item) == 0:
                                instances.append(single_tk)
                if instances:
                    pd1 = pd.DataFrame(instances)
                    pd1.drop_duplicates(
                        subset=["kpj", "npp", "tgl_kepesertaan"], inplace=True
                    )
                    result_dict = pd1.to_dict('records')
                    Tk.objects.bulk_create(
                        [Tk(**data) for data in result_dict]
                    )
            break
        except asyncio.TimeoutError as te:
            count += 1
            if count >= 5:
                break
            logger.info("TimeoutError: %s" % te.msg)
        except aiohttp.client_exceptions.ClientError:
            logger.info("ServerDisconnectedError")
            count += 1
            if count >= 5:
                logger.info("breaking in")
                break


async def safe_download(npp, session):
    sem = asyncio.Semaphore(10)
    async with sem:
        return await fetch_tk_per_npp(npp, session)


async def run(data):
    tasks = []
    async with ClientSession() as session:
        for npp in data:
            task = asyncio.ensure_future(safe_download(npp, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


def fetch_all_tk_baru(to_fetch):
    rekap_npp = fetch_tk_rekap(to_fetch)
    no_dupli = [dict(t) for t in {tuple(d.items()) for d in rekap_npp}]
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(no_dupli))
    loop.run_until_complete(future)

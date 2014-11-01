
import httplib2
import urllib.parse
import urllib.request
import csv

def get_pdb_ids_by_component(component):
    query = (
        "<orgPdbQuery>\n"
        "  <queryType>org.pdb.query.simple.ChemCompIdQuery</queryType>\n"
        "    <chemCompId>{0}</chemCompId>\n"
        "    <polymericType>Any</polymericType>\n"
        "</orgPdbQuery>\n".format(component))
    return send_pdb_query(query).splitlines()

def send_pdb_query(query):
    conn = httplib2.Http()
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    url = "http://www.rcsb.org/pdb/rest/search"
    (response, body) = conn.request(url, "POST", body=query, headers=headers)

    http_status = response["status"]
    if (http_status == "200"):
        return body.decode("utf-8")
    else:
        raise Exception("HTTP Response {}".format(http_status))

def get_report(pdb_ids, columns):
    url = "http://www.rcsb.org/pdb/rest/customReport.csv?" \
          "pdbids={0}&customReportColumns={1}&format=csv" \
          .format(",".join(pdb_ids), ",".join(columns))
    f = urllib.request.urlopen(url)
    csv_string = f.read().decode("utf-8").replace("<br />", "\n")
    table = list(csv.reader(csv_string.splitlines()))
    return list(table[1:])

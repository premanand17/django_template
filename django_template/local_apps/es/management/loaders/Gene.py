import gzip
import re
import requests
from django_template import settings
import json
from db.management.loaders.GFF import GFF
from es.views import elastic_search


class GeneManager:

    '''
    Create index based on genenames.org download file for names
    (http://www.genenames.org/cgi-bin/download).
    The file is assumed to include the following columns:
    hgnc id, approved symbol, status, locus type, previous symbols
    synonyms, entrez gene id, ensembl gene id
    '''
    def load_genename(self, **options):
        if options['org']:
            org = options['org']
        else:
            org = 'human'

        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "gene"

        if options['indexGene'].endswith('.gz'):
            f = gzip.open(options['indexGene'], 'rb')
        else:
            f = open(options['indexGene'], 'rb')

        col = []
        synonymColumns = ["previous symbols", "synonyms",
                          "approved name",
                          "accession numbers", "locus type"]
        dbxrefColumns = ["entrez", "ensembl", "mgi", "refseq"]
        nn = 0
        n = 0
        data = ''

        try:
            for line in f:
                parts = re.split('\t', line.decode("utf-8").rstrip())
                ''' Use table header to identify column names '''
                if(len(col) == 0):
                    for part in parts:
                        col.append(part.lower()
                                   .replace(' gene id', '')
                                   .replace(' ids', '')
                                   .replace('mouse genome database id', 'mgi'))
                    continue

                col_dict = {}
                for idx, part in enumerate(parts):
                    if part != '':
                        col_dict[col[idx]] = part

                if("status" in col_dict and col_dict["status"] == 'Approved'):
                    print("loading... "+col_dict["approved symbol"])

                    dbxref_data = {}
                    for dbType in dbxrefColumns:
                        if(dbType in col_dict and
                           col_dict[dbType].strip() != ''):
                            # split and strip
                            dbxrefs = re.sub(r'\s', '',
                                             col_dict[dbType]
                                             .strip()).split(',')
                            for acc in dbxrefs:
                                dbxref_data[dbType] = acc.strip()

                    synonym_data = []
                    for synType in synonymColumns:
                        if(synType in col_dict):
                            syns = col_dict[synType].strip().split(',')
                            for syn in syns:
                                synonym_data.append(syn.strip())

                    data += '{"index": {"_id": "%s"}}\n' % nn
                    data += json.dumps({"gene_symbol":
                                        col_dict["approved symbol"],
                                        "organism": org,
                                        "hgnc": col_dict["hgnc id"][5:],
                                        "dbxrefs": dbxref_data,
                                        "synonyms": synonym_data
                                        })+'\n'
                    nn += 1
                    n += 1

                    if(n > 5000):
                        n = 0
                        response = requests.put(settings
                                                .ELASTICSEARCH_URL+'/' +
                                                indexName+'/gene/_bulk',
                                                data=data)
                        data = ''
        finally:
            response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                    indexName+'/gene/_bulk', data=data)
            return response

    def load_gene_GFF(self, **options):
        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "gene"

        if options['indexGeneGFF'].endswith('.gz'):
            f = gzip.open(options['indexGeneGFF'], 'rb')
        else:
            f = open(options['indexGeneGFF'], 'rb')
        for line in f:
            line = line.decode("utf-8").rstrip()
            if(line.startswith("##")):
                continue
            gff = GFF(line)
            print(gff.seqid+" "+str(gff.start)+".."+str(gff.end) +
                  " "+gff.attrs["Name"])

            fields = ["gene_symbol"]
            data = {"query": {"query_string": {"query": gff.attrs["Name"],
                                               "fields": fields}}}
            context = elastic_search(data, 0, 20, indexName)
            if context["total"] != 1:
                print ("ERROR ")
            print (context["data"][0])

        return

    ''' Create the mapping for gene names indexing '''
    def create_genename_index(self, **options):
        if options['indexName']:
            indexName = options['indexName'].lower()
        else:
            indexName = "genename"

        props = {"properties":
                 {"gene_symbol": {"type": "string", "boost": 4},
                  "organism": {"type": "string"},
                  "hgnc": {"type": "string"},
                  "dbxrefs": {"type": "object"},
                  "synonyms": {"type": "string"},
                  "biotype": {"type": "string"},
                  "featureloc": {"properties":
                                 {"fmin": {"type": "integer"},
                                  "fmax": {"type": "integer"},
                                  "parent": {"type": "string"}
                                  }
                                 }
                  }
                 }

        data = {"gene": props}
        ''' create index and add mapping '''
        requests.put(settings.ELASTICSEARCH_URL+'/' + indexName)
        response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                indexName+'/_mapping/gene',
                                data=json.dumps(data))
        print (response.text)
        return
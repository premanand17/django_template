import gzip
import re
import json
import requests
from django.conf import settings


class GeneTargetManager:

    def create_load_gene_target_index(self, **options):
        ''' Index gene target data '''
        index_name = self._get_index_name(**options)
        self._create_gene_target_index(**options)

        if options['indexGTarget'].endswith('.gz'):
            f = gzip.open(options['indexGTarget'], 'rb')
        else:
            f = open(options['indexGTarget'], 'rb')

        data = ''
        n = 0
        nn = 0

        try:
            for line in f:
                line = line.rstrip().decode("utf-8")
                parts = re.split('\t', line)
                if nn == 0:
                    nn += 1
                    continue

                data += '{"index": {"_id": "%s"}}\n' % nn
                data += json.dumps({"ensg": parts[0],
                                    "name": parts[1],
                                    "biotype": parts[2],
                                    "strand": parts[3],
                                    "baitChr": parts[4],
                                    "baitStart": parts[5],
                                    "baitEnd": parts[6],
                                    "baitID": parts[7],
                                    "baitName": parts[8],
                                    "oeChr": parts[9],
                                    "oeStart": parts[10],
                                    "oeEnd": parts[11],
                                    "oeID": parts[12],
                                    "oeName": parts[13],
                                    "dist": abs(int(float(parts[14]))),
                                    "Monocyte": parts[15],
                                    "Macrophage": parts[16],
                                    "Erythroblast": parts[17],
                                    "Megakaryocyte": parts[18],
                                    "CD4_Naive": parts[19],
                                    "Non_Activated": parts[20],
                                    "CD4_Total": parts[21],
                                    "CD4_Activated": parts[22]
                                    })+'\n'

                n += 1
                nn += 1
                if(n > 5000):
                    n = 0
                    print('.', end="", flush=True)
                    response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                            index_name+'/gene_target/_bulk',
                                            data=data)
                    data = ''

        finally:
            response = requests.put(settings.ELASTICSEARCH_URL+'/' +
                                    index_name+'/gene_target/_bulk', data=data)
        return response

    def _create_gene_target_index(self, **options):
        ''' Create the mapping for gene target indexing '''
        index_name = self._get_index_name(**options)

        props = {"properties":
                 {"ensg": {"type": "string", "index": "not_analyzed", "boost": 4},
                  "name": {"type": "string", "index": "not_analyzed"},
                  "biotype": {"type": "string", "index": "not_analyzed"},
                  "strand": {"type": "string", "index": "no"},
                  "baitChr": {"type": "string", "index": "no"},
                  "baitStart": {"type": "integer", "index": "not_analyzed"},
                  "baitEnd": {"type": "integer", "index": "not_analyzed"},
                  "baitID": {"type": "string", "index": "no"},
                  "baitName": {"type": "string", "index": "no"},
                  "oeChr": {"type": "string", "index": "no"},
                  "oeStart": {"type": "integer", "index": "not_analyzed"},
                  "oeEnd": {"type": "integer", "index": "not_analyzed"},
                  "oeID": {"type": "string", "index": "no"},
                  "oeName": {"type": "string", "index": "no"},
                  "dist": {"type": "integer", "index": "not_analyzed"},
                  "Monocyte": {"type": "string", "index": "not_analyzed"},
                  "Macrophage": {"type": "string", "index": "not_analyzed"},
                  "Erythroblast": {"type": "string", "index": "not_analyzed"},
                  "Megakaryocyte": {"type": "string", "index": "not_analyzed"},
                  "CD4_Naive": {"type": "string", "index": "not_analyzed"},
                  "Non_Activated": {"type": "string", "index": "not_analyzed"},
                  "CD4_Total": {"type": "string", "index": "not_analyzed"},
                  "CD4_Activated": {"type": "string", "index": "not_analyzed"}
                  }
                 }

        data = {"gene_target": props}

        ''' create index and add mapping '''
        requests.put(settings.ELASTICSEARCH_URL+'/' + index_name)
        requests.put(settings.ELASTICSEARCH_URL+'/' +
                     index_name+'/_mapping/gene_target',
                     data=json.dumps(data))
        return

    def _get_index_name(self, **options):
        if options['indexName']:
            return options['indexName'].lower()
        return "ensg_gene_target"
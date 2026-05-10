
#!/bin/bash

HOST=plessur.ethz.ch
PORT=9200
USER=elastic
CACERT=./secrets/certs/ca/ca.crt

curl --cacert ${CACERT} -H 'Content-Type: application/json' -su ${USER} -vv -XGET "https://${HOST}:${PORT}/wikidata/_search?pretty" -d '
{
"query": {
    "match" : {
                "labels" : {
                            "query" : "wäshington geörge",
                                            "operator": "and",
                                                        "fuzziness": "auto"
                            }
            }
    }
}
'

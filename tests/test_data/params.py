es_171726375 = {
    'gndIdentifier': '171726375',
    'preferredNameEntityForThePerson': {
        'forename': ['David'],
        'surname': ['Birchall'],
    },
    'variantNameEntityForThePerson': {
        'forename': ['D. W.', 'David W.', 'D.'],
        'surname': ['Birchall']
    },
    'academicDegree': ['Prof. em.'],
    'biographicalOrHistoricalInformation': ['Henley Management College, Henley Business School, Univ. of Reading']
}
es_1089259662 = {
    'gndIdentifier': '1089259662',
    'preferredNameEntityForThePerson': {
        'forename': ['J. D.'],
        'surname': ['Birchall'],
        },
    'biographicalOrHistoricalInformation': ['Chemiker, USA']
}
PARAMS_search_person_gnd = [
    (["Albert"], "Einstein", "1800", 0, True, {}, {}),
    (["D."], "Birchall", "1800", 10, True,
     {'171726375': {
         'gid': {'171726375'},
         'prefForename': {'David'},
         'prefSurname': {'Birchall'},
         'varForename': {'D.', 'D. W.', 'David W.'},
         'varSurname': {'Birchall'},
         'academic': {'Prof. em.'},
         'desc': {
             'Henley Management College, Henley Business School, Univ. of \
Reading'},
         'score': 1},
      '1089259662': {
          'gid': {'1089259662'},
          'prefForename': {'J. D.'},
          'prefSurname': {'Birchall'},
          'desc': {'Chemiker, USA'},
          'score': 1},
      '171776313': {
          'gid': {'171776313'},
          'prefForename': {'Sérgio de Oliveira'},
          'prefSurname': {'Birchal'},
          'varForename': {'Sérgio'},
          'varSurname': {'Oliveira Birchal'},
          'birthdate': {'1959'},
          'desc': {'UNA School of Business, Belo Horizonte, Brazil (1999)'},
          'score': 0.8674251549328357},
      '1016708696': {
          'gid': {'1016708696'},
          'prefForename': {'Alice de Souza'},
          'prefSurname': {'Birchal'},
          'varForename': {'Alice', 'Alice de'},
          'varSurname': {'De Souza Birchal', 'Souza Birchal'},
          'desc': {'Brasilian. Juristin, Spez. Familien- u. Erbrecht'},
          'score': 0.8674251549328357},
      '129263265': {
          'gid': {'129263265'},
          'prefForename': {'Derek'},
          'prefSurname': {'Birdsall'},
          'birthdate': {'1934'},
          'score': 0.767993985144672},
      '1020064781': {
          'gid': {'1020064781'},
          'prefForename': {'Dean R.'},
          'prefSurname': {'Brimhall'},
          'birthdate': {'1886'},
          'score': 0.767993985144672},
      '1089356234': {
          'gid': {'1089356234'},
          'prefForename': {'Derek'},
          'prefSurname': {'Birdsall'},
          'desc': {'Graphiker'},
          'score': 0.767993985144672},
      '1102224219': {
          'gid': {'1102224219'},
          'prefForename': {'David'},
          'prefSurname': {'Burchell'},
          'score': 0.767993985144672},
      '1119113008': {
          'gid': {'1119113008'},
          'prefForename': {'Douglas'},
          'prefSurname': {'Birdsall'},
          'activeperiod': {'ca. 21. Jh.'},
          'desc': {'Chairman of the Third Lausanne Congress, Cape Town 2010'},
          'score': 0.767993985144672},
      '1158133847': {
          'gid': {'1158133847'},
          'prefForename': {'David Lyn'},
          'prefSurname': {'Birdsall'},
          'varForename': {'David', 'David L.'},
          'varSurname': {'Birdsall'},
          'score': 0.767993985144672}},
     {'hits': {
            'hits': [
                {'_index': 'gnd_lobid',
                 '_id': '171726375',
                 '_score': 13.893601,
                 '_source': es_171726375
                 },
                {'_index': 'gnd_lobid',
                 '_id': '1089259662',
                 '_score': 13.893601,
                 '_source': es_1089259662
                 },
                {'_index': 'gnd_lobid',
                 '_id': '171776313',
                 '_score': 12.051659,
                 '_source': {
                     'gndIdentifier': '171776313',
                     'preferredNameEntityForThePerson': {
                        'forename': ['Sérgio de Oliveira'],
                        'surname': ['Birchal'],
                     },
                     'variantNameEntityForThePerson': {
                        'forename': ['Sérgio'],
                        'nameAddition': ['de'],
                        'surname': ['Oliveira Birchal'],
                     },
                     'biographicalOrHistoricalInformation': ['UNA School of Business, Belo Horizonte, Brazil (1999)'],
                     'dateOfBirth': ['1959']}
                 },
                {'_index': 'gnd_lobid',
                 '_id': '1016708696',
                 '_score': 12.051659,
                 '_source': {
                     'gndIdentifier': '1016708696',
                     'preferredNameEntityForThePerson': {
                        'forename': ['Alice de Souza'],
                        'surname': ['Birchal'],
                     },
                     'variantNameEntityForThePerson': {
                        'forename': ['Alice de', 'Alice'],
                        'surname': ['Souza Birchal', 'De Souza Birchal'],
                     },
                     'biographicalOrHistoricalInformation': ['Brasilian. Juristin, Spez. Familien- u. Erbrecht']}
                 },
                {'_index': 'gnd_lobid',
                 '_id': '129263265',
                 '_score': 10.670202,
                 '_source': {
                     'gndIdentifier': '129263265',
                     'preferredNameEntityForThePerson': {
                        'forename': ['Derek'],
                        'surname': ['Birdsall'],
                     },
                     'dateOfBirth': ['1934']}
                 },
                {'_index': 'gnd_lobid',
                 '_id': '1020064781',
                 '_score': 10.670202,
                 '_source': {
                     'gndIdentifier': '1020064781',
                     'preferredNameEntityForThePerson': {
                        'forename': ['Dean R.'],
                        'surname': ['Brimhall'],
                     },
                     'dateOfBirth': ['1886']}
                 },
                {'_index': 'gnd_lobid',
                 '_id': '1089356234',
                 '_score': 10.670202,
                 '_source': {
                     'gndIdentifier': '1089356234',
                     'preferredNameEntityForThePerson': {
                        'forename': ['Derek'],
                        'surname': ['Birdsall'],
                     },
                     'biographicalOrHistoricalInformation': ['Graphiker']}
                 },
                {'_index': 'gnd_lobid',
                 '_id': '1102224219',
                 '_score': 10.670202,
                 '_source': {
                     'gndIdentifier': '1102224219',
                     'preferredNameEntityForThePerson': {
                        'forename': ['David'],
                        'surname': ['Burchell']
                     }}
                 },
                {'_index': 'gnd_lobid',
                 '_id': '1119113008',
                 '_score': 10.670202,
                 '_source': {
                     'gndIdentifier': '1119113008',
                     'preferredNameEntityForThePerson': {
                        'forename': ['Douglas'],
                        'surname': ['Birdsall'],
                     },
                     'periodOfActivity': ['ca. 21. Jh.'],
                     'biographicalOrHistoricalInformation': ['Chairman of the Third Lausanne Congress, Cape Town 2010']}
                 },
                {'_index': 'gnd_lobid',
                 '_id': '1158133847',
                 '_score': 10.670202,
                 '_source': {
                     'gndIdentifier': '1158133847',
                     'preferredNameEntityForThePerson': {
                        'forename': ['David Lyn'],
                        'surname': ['Birdsall'],
                     },
                     'variantNameEntityForThePerson': {
                        'forename': ['David', 'David L.'],
                        'surname': ['Birdsall']}
                     }
                 }
            ]
        }
      }
     ),
    (["Jean"], "Bodel", "1897", 3, True,
     {'101695268': {'prefForename': {'Jean'},
        'prefSurname': {'Borel'},
        'desc': {'Schweizer jüdischer Sprachforscher, Verleger, Hauptmann, Wegbereiter des Esperanto in Deutschland'},
        'birthdate': {'1868-08-23'},
        'deathdate': {'1946-01-30'},
        'gid': {'101695268'},
        'score': 1.0},
        '123137241': {'prefForename': {'Jean'},
        'prefSurname': {'Bedel'},
        'desc': {'Franz. Theologe, Regularkanoniker der Congregation du Saint Saveur in Lothringen'},
        'deathdate': {'1657'},
        'gid': {'123137241'},
        'score': 0.9295216727551718},
        '1217500138': {'prefForename': {'Jean'},
        'prefSurname': {'Borel'},
        'desc': {'Adresse: Rue Saint-Jean-de-Beauvais',
        'Adresse: Rue Saint-Jean-de-Latran',
        'Firmenschild: À la Foi chrétienne'},
        'gid': {'1217500138'},
        'score': 0.9295216727551718}},
     {'hits': {
     'total': {
         'value': 7,
         'relation': 'eq'},
     'max_score': 14.188759,
     'hits': [
         {'_index': 'gnd_lobid',
          '_id': 'eNxAK5oBN03XJUZAE-YP',
          '_score': 14.188759,
          '_source': {
              'professionOrOccupation': [
                  {'id': 'https://d-nb.info/gnd/4224183-2',
                   'label': 'Linguist'},
                  {'id': 'https://d-nb.info/gnd/7848462-5',
                   'label': 'Esperantist'}],
              'placeOfBirth': [
                  {'id': 'https://d-nb.info/gnd/4627341-4',
                   'label': 'Couvet'}],
              'gender': [
                  {'id': 'https://d-nb.info/standards/vocab/gnd/gender#male',
                   'label': 'Männlich'}],
              'dateOfDeath': ['1946-01-30'],
              'dateOfBirth': ['1868-08-23'],
              'placeOfDeath': [
                  {'id': 'https://d-nb.info/gnd/4099915-4',
                   'label': 'Lugano'}],
              'variantNameEntityForThePerson': [
                  {'forename': ['Jan'],
                   'surname': ['Borel']},
                  {'forename': ['J.'],
                   'surname': ['Borel']},
                  {'personalName': ['D. Spero']},
                  {'forename': ['Jules'],
                   'surname': ['Borel']},
                  {'personalName': ['J.B.']}],
              'type': [
                  'Person',
                  'AuthorityResource',
                  'DifferentiatedPerson'],
              '@context': 'https://lobid.org/gnd/context.jsonld',
              'oldAuthorityNumber': [
                  '(DE-588)116248661',
                  '(DE-588a)116248661',
                  '(DE-588a)101695268'],
              'geographicAreaCode': [
                  {'id': 'https://d-nb.info/standards/vocab/gnd/geographic-area-code#XA-CH',
                   'label': 'Schweiz'}],
              'deprecatedUri': [
                  'https://d-nb.info/gnd/116248661'],
              'biographicalOrHistoricalInformation': [
                  'Schweizer jüdischer Sprachforscher, Verleger, Hauptmann, Wegbereiter des Esperanto in Deutschland'],
              'pseudonymNameOfThePerson': [
                  {'type': 'PseudonymNameOfThePerson',
                   'personalName': ['D. Spero']},
                  {'type': 'PseudonymNameOfThePerson',
                   'personalName': ['J.B.']}],
              'publication': [
                  'Die Frage einer internationalen Hilfssprache und das Esperanto. - 1906'],
              'describedBy': {
                  'id': 'https://d-nb.info/gnd/101695268/about',
                  'maintainer': {
                      'id': 'https://ld.zdb-services.de/resource/organisations/DE-601',
                      'label': 'https://ld.zdb-services.de/resource/organisations/DE-601'},
                  'dctCreator': {
                      'id': 'https://ld.zdb-services.de/resource/organisations/DE-7',
                      'label': 'https://ld.zdb-services.de/resource/organisations/DE-7'},
                  'license': {
                      'id': 'http://creativecommons.org/publicdomain/zero/1.0/',
                      'label': 'http://creativecommons.org/publicdomain/zero/1.0/'},
                  'dateModified': '2021-12-08T13:57:41.000',
                  'descriptionLevel': {
                      'id': 'https://d-nb.info/standards/vocab/gnd/description-level#1',
                      'label': 'Katalogisierungslevel 1'}},
              'gndIdentifier': '101695268',
              'id': 'https://d-nb.info/gnd/101695268',
              'preferredName': 'Borel, Jean',
              'wikipedia': [
                  {'id': 'https://de.wikipedia.org/wiki/Jean_Borel_%28Esperantist%29',
                   'label': 'https://de.wikipedia.org/wiki/Jean_Borel_%28Esperantist%29'}],
              'variantName': ['Borel, Jules', 'Borel, Jan', 'J.B.', 'Borel, J.', 'D. Spero'],
              'preferredNameEntityForThePerson': {
                  'forename': ['Jean'],
                  'surname': ['Borel']},
              'sameAs': [
                  {'id': 'http://id.loc.gov/rwo/agents/no2012076804',
                   'collection': {
                       'id': 'http://www.wikidata.org/entity/Q13219454',
                       'abbr': 'LC',
                       'publisher': 'Library of Congress',
                       'icon': 'http://www.loc.gov/favicon.ico',
                       'name': 'NACO Authority File'}},
                  {'id': 'http://viaf.org/viaf/161088241',
                   'collection': {
                       'id': 'http://www.wikidata.org/entity/Q54919',
                       'abbr': 'VIAF',
                       'publisher': 'OCLC',
                       'icon': 'http://viaf.org/viaf/images/viaf.ico',
                       'name': 'Virtual International Authority File (VIAF)'}},
                  {'id': 'http://www.wikidata.org/entity/Q12349739',
                   'collection': {
                       'id': 'http://www.wikidata.org/entity/Q2013',
                       'abbr': 'WIKIDATA',
                       'publisher': 'Wikimedia Foundation Inc.',
                       'icon': 'https://www.wikidata.org/static/favicon/wikidata.ico',
                       'name': 'Wikidata'}},
                  {'collection': {
                      'abbr': 'DNB',
                      'name': 'Gemeinsame Normdatei (GND) im Katalog der Deutschen Nationalbibliothek',
                      'publisher': 'Deutsche Nationalbibliothek',
                      'icon': 'https://www.dnb.de/SiteGlobals/Frontend/DNBWeb/Images/favicon.png?__blob=normal&v=4',
                      'id': 'http://www.wikidata.org/entity/Q36578'},
                   'id': 'https://d-nb.info/gnd/101695268/about'},
                  {'id': 'https://d-nb.info/gnd/116248661',
                   'collection': {
                       'id': 'http://www.wikidata.org/entity/Q36578',
                       'abbr': 'DNB',
                       'publisher': 'Deutsche Nationalbibliothek',
                       'icon': 'http://www.dnb.de/SiteGlobals/StyleBundles/Bilder/favicon.png?__blob=normal&v=1',
                       'name': 'Gemeinsame Normdatei (GND) im Katalog der Deutschen Nationalbibliothek'}},
                  {'collection': {
                      'abbr': 'dewiki',
                      'name': 'Wikipedia (Deutsch)',
                      'publisher': 'Wikimedia Foundation Inc.',
                      'icon': 'https://de.wikipedia.org/static/favicon/wikipedia.ico',
                      'id': 'http://www.wikidata.org/entity/Q48183'},
                   'id': 'https://de.wikipedia.org/wiki/Jean_Borel_%28Esperantist%29'},
                  {'id': 'https://isni.org/isni/0000000110946877',
                   'collection': {
                       'id': 'https://isni.org'}},
                  {'collection': {
                      'abbr': 'DE-611',
                      'name': 'Kalliope Verbundkatalog',
                      'publisher': 'Staatsbibliothek zu Berlin - Preußischer Kulturbesitz',
                      'icon': 'https://kalliope-verbund.info/img/favicon.ico',
                      'id': 'https://kalliope-verbund.info'},
                   'id': 'https://kalliope-verbund.info/gnd/101695268'},
                  {'collection': {
                      'abbr': 'DDB',
                      'name': 'Deutsche Digitale Bibliothek',
                      'publisher': 'Deutsche Digitale Bibliothek',
                      'icon': 'https://www.deutsche-digitale-bibliothek.de/favicon.ico',
                      'id': 'http://www.wikidata.org/entity/Q621630'},
                   'id': 'https://www.deutsche-digitale-bibliothek.de/person/gnd/101695268'}],
              'depiction': [
                  {'id': 'https://commons.wikimedia.org/wiki/Special:FilePath/Jean%20Borel.jpg',
                   'url': 'https://commons.wikimedia.org/wiki/File:Jean%20Borel.jpg?uselang=de',
                   'thumbnail': 'https://commons.wikimedia.org/wiki/Special:FilePath/Jean%20Borel.jpg?width=270'}]}},
         {'_index': 'gnd_lobid',
          '_id': 'lutFK5oBN03XJUZAynvO',
          '_score': 13.188759,
          '_source': {
              'gender': [
                  {'id': 'https://d-nb.info/standards/vocab/gnd/gender#notKnown',
                   'label': 'Unbekannt'}],
              'dateOfDeath': ['1657'],
              'variantNameEntityForThePerson': [
                  {'forename': ['Johannes'],
                   'surname': ['Bedel']},
                  {'forename': ['Joannes'],
                   'surname': ['Bedel']},
                  {'forename': ['Jean'],
                   'surname': ['Bedle']}],
              'type': [
                  'AuthorityResource', 'Person', 'DifferentiatedPerson'],
              '@context': 'https://lobid.org/gnd/context.jsonld',
              'oldAuthorityNumber': ['(DE-588a)123137241'],
              'biographicalOrHistoricalInformation': [
                  'Franz. Theologe, Regularkanoniker der Congregation du Saint Saveur in Lothringen'],
              'publication': [
                  'Idea boni parochi & perfecti religiosi, sive vita Petri Forerii. - 1668'],
              'describedBy': {
                  'id': 'https://d-nb.info/gnd/123137241/about',
                  'maintainer': {
                      'id': 'https://ld.zdb-services.de/resource/organisations/DE-576',
                      'label': 'https://ld.zdb-services.de/resource/organisations/DE-576'},
                  'dctCreator': {
                      'id': 'https://ld.zdb-services.de/resource/organisations/DE-576',
                      'label': 'https://ld.zdb-services.de/resource/organisations/DE-576'},
                  'license': {
                      'id': 'http://creativecommons.org/publicdomain/zero/1.0/',
                      'label': 'http://creativecommons.org/publicdomain/zero/1.0/'},
                  'dateModified': '2016-11-24T17:15:17.000',
                  'descriptionLevel': {
                      'id': 'https://d-nb.info/standards/vocab/gnd/description-level#3',
                      'label': 'Katalogisierungslevel 3'}},
              'gndIdentifier': '123137241',
              'id': 'https://d-nb.info/gnd/123137241',
              'preferredName': 'Bedel, Jean',
              'variantName': [
                  'Bedel, Joannes', 'Bedle, Jean', 'Bedel, Johannes'],
              'preferredNameEntityForThePerson': {
                  'forename': ['Jean'],
                  'surname': ['Bedel']},
              'sameAs': [
                  {'id': 'http://id.loc.gov/rwo/agents/no96031052',
                   'collection': {
                       'id': 'http://www.wikidata.org/entity/Q13219454',
                       'abbr': 'LC',
                       'publisher': 'Library of Congress',
                       'icon': 'http://www.loc.gov/favicon.ico',
                       'name': 'NACO Authority File'}}, 
                  {'id': 'http://viaf.org/viaf/79254078',
                   'collection': {
                       'id': 'http://www.wikidata.org/entity/Q54919',
                       'abbr': 'VIAF',
                       'publisher': 'OCLC',
                       'icon': 'http://viaf.org/viaf/images/viaf.ico',
                       'name': 'Virtual International Authority File (VIAF)'}},
                  {'id': 'http://www.wikidata.org/entity/Q112435498',
                   'collection': {
                       'id': 'http://www.wikidata.org/entity/Q2013',
                       'abbr': 'WIKIDATA',
                       'publisher': 'Wikimedia Foundation Inc.',
                       'icon': 'https://www.wikidata.org/static/favicon/wikidata.ico',
                       'name': 'Wikidata'}},
                  {'collection': {
                      'abbr': 'DNB',
                      'name': 'Gemeinsame Normdatei (GND) im Katalog der Deutschen Nationalbibliothek',
                      'publisher': 'Deutsche Nationalbibliothek',
                      'icon': 'https://www.dnb.de/SiteGlobals/Frontend/DNBWeb/Images/favicon.png?__blob=normal&v=4',
                      'id': 'http://www.wikidata.org/entity/Q36578'},
                   'id': 'https://d-nb.info/gnd/123137241/about'},
                  {'id': 'https://isni.org/isni/0000000108152242',
                   'collection': {
                       'id': 'https://isni.org'}}]}},
         {'_index': 'gnd_lobid',
          '_id': '5gZQK5oBN03XJUZAIIsX',
          '_score': 13.188759,
          '_source': {
              'professionOrOccupation': [
                  {'id': 'https://d-nb.info/gnd/4138343-6',
                   'label': 'Verleger'}],
              'gender': [
                  {'id': 'https://d-nb.info/standards/vocab/gnd/gender#notKnown',
                   'label': 'Unbekannt'}],
              'variantNameEntityForThePerson': [
                  {'forename': ['Johannes'],
                   'surname': ['Borellus']},
                  {'forename': ['Iean'],
                   'surname': ['Borel']},
                  {'forename': ['Joannes'],
                   'surname': ['Borellus']}],
              'type': ['Person', 'AuthorityResource', 'DifferentiatedPerson'],
              '@context': 'https://lobid.org/gnd/context.jsonld',
              'geographicAreaCode': [
                  {'id': 'https://d-nb.info/standards/vocab/gnd/geographic-area-code#XA-FR',
                   'label': 'Frankreich'}],
              'biographicalOrHistoricalInformation': [
                  'Adresse: Rue Saint-Jean-de-Latran',
                  'Firmenschild: À la Foi chrétienne',
                  'Adresse: Rue Saint-Jean-de-Beauvais'],
              'describedBy': {
                  'id': 'https://d-nb.info/gnd/1217500138/about',
                  'maintainer': {
                      'id': 'https://ld.zdb-services.de/resource/organisations/DE-1',
                      'label': 'https://ld.zdb-services.de/resource/organisations/DE-1'},
                  'dctCreator': {
                      'id': 'https://ld.zdb-services.de/resource/organisations/DE-1',
                      'label': 'https://ld.zdb-services.de/resource/organisations/DE-1'},
                  'license': {
                      'id': 'http://creativecommons.org/publicdomain/zero/1.0/',
                      'label': 'http://creativecommons.org/publicdomain/zero/1.0/'},
                  'dateModified': '2022-05-17T10:27:00.000',
                  'descriptionLevel': {
                      'id': 'https://d-nb.info/standards/vocab/gnd/description-level#3',
                      'label': 'Katalogisierungslevel 3'}},
              'gndIdentifier': '1217500138',
              'id': 'https://d-nb.info/gnd/1217500138',
              'placeOfActivity': [
                  {'id': 'https://d-nb.info/gnd/4044660-8',
                   'label': 'Paris'}],
              'preferredName': 'Borel, Jean',
              'variantName': ['Borellus, Joannes', 'Borellus, Johannes', 'Borel, Iean'],
              'preferredNameEntityForThePerson': {
                  'forename': ['Jean'],
                  'surname': ['Borel']},
              'sameAs': [
                  {'id': 'http://viaf.org/viaf/2898160001834530300000',
                   'collection': {
                       'id': 'http://www.wikidata.org/entity/Q54919',
                       'abbr': 'VIAF',
                       'publisher': 'OCLC',
                       'icon': 'http://viaf.org/viaf/images/viaf.ico',
                       'name': 'Virtual International Authority File (VIAF)'}},
                  {'collection': {
                      'abbr': 'DNB',
                      'name': 'Gemeinsame Normdatei (GND) im Katalog der Deutschen Nationalbibliothek',
                      'publisher': 'Deutsche Nationalbibliothek',
                      'icon': 'https://www.dnb.de/SiteGlobals/Frontend/DNBWeb/Images/favicon.png?__blob=normal&v=4',
                      'id': 'http://www.wikidata.org/entity/Q36578'},
                   'id': 'https://d-nb.info/gnd/1217500138/about'}]}}]}},
     ),
    (["Jean"], "Bodel", "1897", 3, False, {}, {})
]
PARAMS_search_person_wikidata = [
    ("D. Birchall", "1800", 5, True,
     {'1119113008':
         {'gid': {'1119113008'},
          'name': {'Douglas Birdsall'},
          'prefSurname': {'Birdsall'},
          'prefForename': {'Douglas'},
          'score': 1.0}
     },
     {'hits': {
         'hits': [
             {'_index': 'wikidata-v2',
              '_id': 'nu30YYsBW8gB8I1OZr1w',
              '_score': 11.325728,
              '_source': {
                  'id': 'Q113843374',
                  'labels': 'Douglas Birdsall',
                  'aliases': [],
                  'instanceOf': ['Q5'],
                  'GND_ID': ['1119113008']
                  }
              }
            ]
        }
     }),
    ("J.F. Bitschnau", "1800", 5, True,
     {'1065067526':
         {'prefForename': {'Johann'},
          'jobliteral': {'Arzt', 'Historiker', 'Politiker', 'Rechtsanwalt'},
          'birthdate': {'1776-00-00'},
          'deathdate': {'1819-00-00'},
          'gid': {'1065067526'},
          'name': {'Johann Josef Bitschnau'},
          'prefSurname': {'Bitschnau'},
          'score': 1.0}},
     {'hits': {
         'hits': [
             {'_index': 'wikidata-v2',
              '_id': 'rdLuYYsBW8gB8I1ONY30',
              '_score': 16.720705,
              '_source': {
                  'id': 'Q94917995',
                  'labels': 'Johann Josef Bitschnau',
                  'aliases': [],
                  'gender': ['männlich'],
                  'instanceof': ['Q5'],
                  'occupation': ['Arzt', 'Historiker', 'Rechtsanwalt', 'Politiker'],
                  'GND_ID': ['1065067526'],
                  'dateOfBirth': ['+1776-00-00T00:00:00Z'],
                  'dateOfDeath': ['+1819-00-00T00:00:00Z'],
                  'givenName': ['Johann'],
                  'GND_ID_2': ['1065067526']}
              }
            ]
          }
      }),
    ("Viktor Amadeus", "1800", 5, True,
     {'142136859': {
         'desc': {'(1727-1793)'},
         'birthplaceLiteral': {'Mierczyce'},
         'prefForename': {'Viktor'},
         'jobliteral': {'Kammerherr'},
         'birthdate': {'1727-09-15'},
         'deathdate': {'1793-01-31'},
         'deathplaceLiteral': {'Königsberg'},
         'gid': {'142136859'},
         'name': {'Viktor Amadeus Henckel von Donnersmarck'},
         'prefSurname': {'Donnersmarck'},
         'score': 1.0},
      '135979773': {
          'desc': {'Duke of Savoy (1587–1637)'},
          'birthplaceLiteral': {'Turin'},
          'prefForename': {'Victor-Amédée'},
          'prefSurname': {'Savoia'},
          'jobliteral': {'Aristokrat', 'Politiker'},
          'birthdate': {'1587-05-08'},
          'deathdate': {'1637-10-07'},
          'deathplaceLiteral': {'Vercelli'},
          'gid': {'135979773'},
          'name': {'Victor Amadeus I of Savoy'},
          'score': 0.9484621382358511},
      '118804537': {
          'desc': {'Duke of Savoy and King of Sardinia (1675-1732)'},
          'birthplaceLiteral': {'Turin'},
          'prefForename': {'Victor-Amédée'},
          'prefSurname': {'Savoia'},
          'jobliteral': {'Politiker'},
          'birthdate': {'1666-05-14'},
          'deathdate': {'1732-10-31'},
          'deathplaceLiteral': {'Moncalieri', 'Rivoli'},
          'gid': {'118804537'},
          'name': {'Victor Amadeus II of Savoy'},
          'score': 0.9484621382358511},
      '189532912': {
          'desc': {'German noble (1779-1834)'},
          'birthplaceLiteral': {'Rotenburg an der Fulda'},
          'prefForename': {'Victor-Amédée'},
          'jobliteral': {'Kammerherr', 'Politiker'},
          'birthdate': {'1779-09-02'},
          'deathdate': {'1834-11-12'},
          'deathplaceLiteral': {'Zembowitz'},
          'gid': {'189532912'},
          'name': {'Victor Amadeus, Landgrave of Hesse-Rotenburg'},
          'prefSurname': {'Hesse-Rotenburg'},
          'score': 0.86924704972046},
      '118144677': {
          'desc': {'German prince'},
          'birthplaceLiteral': {'Harzgerode'},
          'prefForename': {'Victor-Amédée'},
          'varForename': {'Der Gerühmte'},
          'jobliteral': {'Aristokrat'},
          'birthdate': {'1634-10-06'},
          'deathdate': {'1718-02-14'},
          'deathplaceLiteral': {'Bernburg'},
          'gid': {'118144677'},
          'name': {'Victor Amadeus, Prince of Anhalt-Bernburg'},
          'prefSurname': {'Anhalt-Bernburg'},
          'score': 0.86924704972046}
      },
     {'hits': {
         'hits': [
             {'_index': 'wikidata-v2',
              '_id': '627WYYsBW8gB8I1OaYbi',
              '_score': 14.632427,
              '_source': {
                  'placeOfBirth': ['Mierczyce'],
                  'aliases': [],
                  'occupation': ['Kammerherr'],
                  'gender': ['männlich'],
                  'dateOfDeath': ['+1793-01-31T00:00:00Z'],
                  'givenName': ['Viktor'],
                  'dateOfBirth': ['+1727-09-15T00:00:00Z'],
                  'placeOfDeath': ['Königsberg'],
                  'descriptions': '(1727-1793)',
                  'GND_ID': ['142136859'],
                  'spouse': ['Eleonore Maximiliane Ottilie Henckel von Donnersmarck'],
                  'labels': 'Viktor Amadeus Henckel von Donnersmarck',
                  'instanceOf': ['Q5'],
                  'GND_ID_2': ['142136859'],
                  'countryOfCitizenship': ['Königreich Preußen'],
                  'claims': {},
                  'id': 'Q2524210'}
             },
             {'_index': 'wikidata-v2',
              '_id': 'TFfQYYsBW8gB8I1OrPD0',
              '_score': 13.878303,
              '_source': {
                  'placeOfBirth': ['Turin'],
                  'aliases': [
                      'Duke of Savoy Victor Amedee',
                      'Duke of Savoy Vittorio Amadeo',
                      'Vittorio Amedeo II',
                      'Vittorio Amedeo II di Savoia',
                      'Duke of Savoy Victor Amadeus I',
                      'Victor Amadeus I'
                   ],
                  'occupation': ['Aristokrat', 'Politiker'],
                  'gender': ['männlich'],
                  'dateOfDeath': ['+1637-10-07T00:00:00Z'],
                  'givenName': ['Victor-Amédée'],
                  'dateOfBirth': ['+1587-05-08T00:00:00Z'],
                  'placeOfDeath': ['Vercelli'],
                  'descriptions': 'Duke of Savoy (1587–1637)',
                  'GND_ID': ['135979773'],
                  'spouse': ['Christina von Frankreich'],
                  'labels': 'Victor Amadeus I of Savoy',
                  'instanceOf': ['Q5'],
                  'GND_ID_2': ['135979773'],
                  'familyName': ['Savoia'],
                  'claims': {},
                  'id': 'Q356145',
                  'causeOfDeath': ['Krankheit']}
             },
             {'_index': 'wikidata-v2',
              '_id': 'iW3VYYsBW8gB8I1O6oWl',
              '_score': 13.878303,
              '_source': {
                  'nativeName': ['Victorius Amadeus II', 'Victor-Amédée II', 'Vittorio Amedeo II'],
                  'placeOfBirth': ['Turin'],
                  'aliases': ['Vittorio Amedeo II', 'Victor Amadeus II'],
                  'occupation': ['Politiker'],
                  'gender': ['männlich'],
                  'dateOfDeath': ['+1732-10-31T00:00:00Z'],
                  'mannerOfDeath': ['natürliche Todesursache'],
                  'givenName': ['Victor-Amédée'],
                  'dateOfBirth': ['+1666-05-14T00:00:00Z'],
                  'placeOfDeath': ['Moncalieri', 'Rivoli'],
                  'descriptions': 'Duke of Savoy and King of Sardinia (1675-1732)',
                  'GND_ID': ['118804537'],
                  'spouse': ['Anne Marie d’Orléans', 'Anna Canalis di Cumiana'],
                  'labels': 'Victor Amadeus II of Savoy',
                  'instanceOf': ['Q5'],
                  'GND_ID_2': ['118804537'],
                  'countryOfCitizenship': [],
                  'familyName': ['Savoia'],
                  'claims': {},
                  'id': 'Q209579',
                  'causeOfDeath': ['Schlaganfall']}
             },
             {'_index': 'wikidata-v2',
              '_id': '0-_0YYsBW8gB8I1O0mGr',
              '_score': 12.719194,
              '_source': {
                  'placeOfBirth': ['Rotenburg an der Fulda'],
                  'aliases': [
                      'Victor Amadeus von Hessen-Rotenburg',
                      'Viktor Amadeus Landgraf von Hessen-Rotenburg',
                      'Victor of Hesse-Rotenburg'
                  ],
                  'occupation': ['Kammerherr', 'Politiker'],
                  'gender': ['männlich'],
                  'dateOfDeath': ['+1834-11-12T00:00:00Z'],
                  'givenName': ['Victor-Amédée'],
                  'dateOfBirth': ['+1779-09-02T00:00:00Z'],
                  'placeOfDeath': ['Zembowitz'],
                  'descriptions': 'German noble (1779-1834)',
                  'GND_ID': ['189532912'],
                  'spouse': ['Elise von Hessen-Rothenburg'],
                  'labels': 'Victor Amadeus, Landgrave of Hesse-Rotenburg',
                  'instanceOf': ['Q5'],
                  'GND_ID_2': ['189532912'],
                  'countryOfCitizenship': ['Deutschland'],
                  'claims': {},
                  'id': 'Q553931'}
             },
             {'_index': 'wikidata-v2',
              '_id': 'uW3VYYsBW8gB8I1O1msB',
              '_score': 12.719194,
              '_source': {
                  'nativeName': ['Viktor I. Amadeus von Anhalt-Bernburg'],
                  'placeOfBirth': ['Harzgerode'],
                  'aliases': ['Victor Amadeus of Anhalt-Bernburg'],
                  'occupation': ['Aristokrat'],
                  'gender': ['männlich'],
                  'dateOfDeath': ['+1718-02-14T00:00:00Z'],
                  'givenName': ['Victor-Amédée'],
                  'dateOfBirth': ['+1634-10-06T00:00:00Z'],
                  'placeOfDeath': ['Bernburg'],
                  'descriptions': 'German prince',
                  'GND_ID': ['118144677'],
                  'spouse': ['Elisabeth of Palatinate-Zweibrücken'],
                  'labels': 'Victor Amadeus, Prince of Anhalt-Bernburg',
                  'instanceOf': ['Q5'],
                  'GND_ID_2': ['118144677'],
                  'countryOfCitizenship': ['Deutschland'],
                  'claims': {},
                  'nickname': ['Der Gerühmte'],
                  'id': 'Q69454'}
             },
         ]
      }
     }),
    (" Hiilimann", "1800", 5, True,
     {'1059539489': {
         'desc': {'(1793-1850)'},
         'birthplaceLiteral': {'Riedikon'},
         'prefForename': {'Johann'},
         'prefSurname': {'Hürlimann'},
         'jobliteral': {'Druckgrafiker'},
         'birthdate': {'1793-05-02'},
         'deathdate': {'1850-03-18'},
         'deathplaceLiteral': {'Paris'},
         'gid': {'1059539489'},
         'name': {'Johann Hürlimann'},
         'score': 1.0},
      '10429521X': {
          'birthplaceLiteral': {'Basel'},
          'jobliteral': {'Ratsherr'},
          'birthdate': {'1739-00-00'},
          'deathdate': {'1817-00-00'},
          'deathplaceLiteral': {'Biel/Bienne'},
          'gid': {'10429521X'},
          'name': {'Niklaus Heilmann'},
          'prefSurname': {'Heilmann'},
          'prefForename': {'Niklaus'},
          'score': 0.9731347810092921},
      '135688949': {
          'prefForename': {'Gottfried'},
          'jobliteral': {'Unternehmer'},
          'birthdate': {'1743-01-01'},
          'deathdate': {'1807-01-01'},
          'gid': {'135688949'},
          'name': {'Gottfried Heilmann'},
          'prefSurname': {'Heilmann'},
          'score': 0.9731347810092921},
      '1034910442': {
          'prefForename': {'Bruno'},
          'birthdate': {'1635-06-18'},
          'deathdate': {'1708-06-29'},
          'gid': {'1034910442'},
          'name': {'Bruno Heilmann'},
          'prefSurname': {'Heilmann'},
          'score': 0.9731347810092921},
      '129252433': {
          'desc': {'German architect (1475-1523)'},
          'birthplaceLiteral': {'Schweinfurt'},
          'prefForename': {'Jacob', 'Jakob'},
          'prefSurname': {'Heilmann'},
          'jobliteral': {'Architekt'},
          'birthdate': {'1475-01-01'},
          'deathdate': {'1523-01-01'},
          'deathplaceLiteral': {'Annaberg-Buchholz'},
          'gid': {'129252433'},
          'name': {'Jakob Heilmann'},
          'score': 0.9731347810092921}
     },
        {'hits': {
            'hits': [
            {'_index': 'wikidata-v2',
             '_id': 'Vu_0YYsBW8gB8I1O8ZsD',
             '_score': 12.107774,
             '_source': {
                    'placeOfBirth': ['Riedikon'],
                    'aliases': ['Johann Huerlimann', 'Johann Hurlimann'],
                    'occupation': ['Druckgrafiker'],
                    'gender': ['männlich'],
                    'dateOfDeath': ['+1850-03-18T00:00:00Z'],
                    'givenName': ['Johann'],
                    'dateOfBirth': ['+1793-05-02T00:00:00Z'],
                    'placeOfDeath': ['Paris'],
                    'descriptions': '(1793-1850)',
                    'GND_ID': ['1059539489'],
                    'labels': 'Johann Hürlimann',
                    'instanceOf': ['Q5'],
                    'GND_ID_2': ['1059539489'],
                    'countryOfCitizenship': ['Schweiz'],
                    'familyName': ['Hürlimann'],
                    'claims': {},
                    'id': 'Q1101076'}
                },
            {'_index': 'wikidata-v2',
                '_id': '82bUYYsBW8gB8I1OeHLh',
                '_score': 11.782496,
                '_source': {
                    'placeOfBirth': ['Basel'],
                    'aliases': [],
                    'occupation': ['Ratsherr'],
                    'gender': ['männlich'],
                    'dateOfDeath': ['+1817-00-00T00:00:00Z'],
                    'dateOfBirth': ['+1739-00-00T00:00:00Z'],
                    'placeOfDeath': ['Biel/Bienne'],
                    'GND_ID': ['10429521X'],
                    'labels': 'Niklaus Heilmann',
                    'instanceOf': ['Q5'],
                    'GND_ID_2': ['10429521X'],
                    'claims': {},
                    'id': 'Q94837892'}
                },
            {'_index': 'wikidata-v2',
                '_id': 'YsztYYsBW8gB8I1OKpjv',
                '_score': 11.782496,
                '_source': {
                    'aliases': [],
                    'occupation': ['Unternehmer'],
                    'gender': ['männlich'],
                    'dateOfDeath': ['+1807-01-01T00:00:00Z'],
                    'givenName': ['Gottfried'],
                    'claims': {},
                    'dateOfBirth': ['+1743-01-01T00:00:00Z'],
                    'id': 'Q55851624',
                    'GND_ID': ['135688949'],
                    'labels': 'Gottfried Heilmann',
                    'instanceOf': ['Q5'],
                    'GND_ID_2': ['135688949']}
                },
            {'_index': 'wikidata-v2',
                '_id': 'Xv34YYsBW8gB8I1OR8OH',
                '_score': 11.782496,
                '_source': {
                    'aliases': [],
                    'gender': ['männlich'],
                    'dateOfDeath': ['+1708-06-29T00:00:00Z'],
                    'givenName': ['Bruno'],
                    'claims': {},
                    'dateOfBirth': ['+1635-06-18T00:00:00Z'],
                    'id': 'Q94913140',
                    'GND_ID': ['1034910442'],
                    'labels': 'Bruno Heilmann',
                    'instanceOf': ['Q5'],
                    'GND_ID_2': ['1034910442']}
                },
            {'_index': 'wikidata-v2',
                '_id': 'm1fQYYsBW8gB8I1OkMvg',
                '_score': 11.782496,
                '_source': {
                    'placeOfBirth': ['Schweinfurt'],
                    'aliases': ['Jacob Haylmann'],
                    'occupation': ['Architekt'],
                    'gender': ['männlich'],
                    'dateOfDeath': ['+1523-01-01T00:00:00Z'],
                    'givenName': ['Jakob', 'Jacob'],
                    'dateOfBirth': ['+1475-01-01T00:00:00Z'],
                    'placeOfDeath': ['Annaberg-Buchholz'],
                    'descriptions': 'German architect (1475-1523)',
                    'GND_ID': ['129252433'],
                    'labels': 'Jakob Heilmann',
                    'instanceOf': ['Q5'],
                    'GND_ID_2': ['129252433'],
                    'countryOfCitizenship': ['Deutschland'],
                    'familyName': ['Heilmann'],
                    'claims': {},
                    'id': 'Q99468'}
                },
            ]
            }
        }
        ),
    ("Urs fosef Cavelti", "2004", 5, True,
        {'1066273278': {
            'desc': {'(1927-2003)'},
            'birthplaceLiteral': {'Gossau'},
            'prefForename': {'Urs'},
            'jobliteral': {'Jurist'},
            'birthdate': {'1927-09-03'},
            'deathdate': {'2003-11-04'},
            'deathplaceLiteral': {'St. Gallen'},
            'gid': {'1066273278'},
            'name': {'Urs Josef Cavelti'},
            'prefSurname': {'Cavelti'},
            'score': 1.0}},
        {'hits': {
            'hits': [
                {'_index': 'wikidata-v2',
                '_id': 'zovdYYsBW8gB8I1Ow7qQ',
                '_score': 24.632502,
                '_source': {
                    'placeOfBirth': ['Gossau'],
                    'aliases': [],
                    'occupation': ['Jurist'],
                    'gender': ['männlich'],
                    'dateOfDeath': ['+2003-11-04T00:00:00Z'],
                    'givenName': ['Urs'],
                    'dateOfBirth': ['+1927-09-03T00:00:00Z'],
                    'placeOfDeath': ['St. Gallen'],
                    'descriptions': '(1927-2003)',
                    'GND_ID': ['1066273278'],
                    'labels': 'Urs Josef Cavelti',
                    'instanceOf': ['Q5'],
                    'countryOfCitizenship': ['Schweiz'],
                    'claims': {}, 
                    'id': 'Q55683152'}
                }
            ]
            }
        }
        ),
    ("Albert Einstein", "1800", 0, True, {}, {}),
    ("Jean Bodel", "1897", 3, True, 
     {
        '118660454': {'desc': {'Old French poet'},
                      'birthplaceLiteral': {'Arras'},
                      'prefForename': {'Jean'},
                      'prefSurname': {'Bodel'},
                      'jobliteral': {'Dichter', 'Musiker', 'Schriftsteller', 'Troubadour'},
                      'birthdate': {'1165-00-00'},
                      'deathdate': {'1210-00-00'},
                      'deathplaceLiteral': {'Beaurain'},
                      'gid': {'118660454'},
                      'name': {'Jean Bodel'},
                      'score': 1.0},
        '110611597X': {'birthplaceLiteral': {'Fenestrelle'},
                       'prefForename': {'Jean'},
                       'jobliteral': {'Arzt', 'Hochschullehrer'},
                       'birthdate': {'1684-12-22'},
                       'deathdate': {'1747-01-12'},
                       'gid': {'110611597X'},
                       'name': {'Jean Borel'},
                       'prefSurname': {'Borel'},
                       'score': 0.8852658442191151},
        '101695268': {'desc': {'Swiss Esperantist (1868-1946)'},
                      'birthplaceLiteral': {'Couvet'},
                      'prefForename': {'Jean'},
                      'prefSurname': {'Borel'},
                      'jobliteral': {'Esperantist', 'Linguist', 'Publizist', 'Verleger'},
                      'birthdate': {'1868-08-23'},
                      'deathdate': {'1946-00-00'},
                      'deathplaceLiteral': {'Lugano'},
                      'gid': {'101695268'},
                      'name': {'Jean Borel'},
                      'score': 0.8852658442191151}},
     {'hits': {
      'total': {
          'value': 6,
          'relation': 'eq'},
      'max_score': 19.762476,
      'hits': [
          {'_index': 'wikidata-v2',
           '_id': 'La7lYYsBW8gB8I1ONzdh',
           '_score': 19.762476,
           '_source': {
               'nativeName': ['Jean Bodel'],
               'placeOfBirth': ['Arras'],
               'aliases': ['Bodel'],
               'occupation': ['Dichter', 'Schriftsteller', 'Musiker', 'Troubadour'],
               'gender': ['männlich'],
               'dateOfDeath': ['+1210-00-00T00:00:00Z'],
               'givenName': ['Jean'],
               'dateOfBirth': ['+1165-00-00T00:00:00Z'],
               'placeOfDeath': ['Beaurain'],
               'descriptions': 'Old French poet',
               'GND_ID': ['118660454'],
               'labels': 'Jean Bodel',
               'instanceOf': ['Q5'],
               'GND_ID_2': ['118660454'],
               'countryOfCitizenship': ['Frankreich'],
               'familyName': ['Bodel'],
               'claims': {},
               'id': 'Q5172',
               'causeOfDeath': ['Lepra']}}, 
          {'_index': 'wikidata-v2',
           '_id': 'zf_4YYsBW8gB8I1OmGOY',
           '_score': 17.495045,
           '_source': {
               'placeOfBirth': ['Fenestrelle'],
               'aliases': [],
               'occupation': ['Arzt', 'Hochschullehrer'],
               'gender': ['männlich'],
               'dateOfDeath': ['+1747-01-12T00:00:00Z'],
               'givenName': ['Jean'],
               'dateOfBirth': ['+1684-12-22T00:00:00Z'],
               'GND_ID': ['110611597X'],
               'labels': 'Jean Borel',
               'instanceOf': ['Q5'],
               'GND_ID_2': ['110611597X'],
               'claims': {},
               'id': 'Q100371829'}}, 
          {'_index': 'wikidata-v2',
           '_id': 'psfrYYsBW8gB8I1O6M9y',
           '_score': 17.495045,
           '_source': {
               'placeOfBirth': ['Couvet'],
               'aliases': [],
               'occupation': ['Esperantist', 'Verleger', 'Publizist', 'Linguist', 'Esperantist'],
               'gender': ['männlich'],
               'dateOfDeath': ['+1946-00-00T00:00:00Z', '+1946-01-30T00:00:00Z'],
               'givenName': ['Jean'],
               'dateOfBirth': ['+1868-08-23T00:00:00Z', '+1868-00-00T00:00:00Z'],
               'placeOfDeath': ['Lugano'],
               'descriptions': 'Swiss Esperantist (1868-1946)',
               'GND_ID': ['101695268'],
               'labels': 'Jean Borel',
               'instanceOf': ['Q5'],
               'GND_ID_2': ['101695268'],
               'countryOfCitizenship': ['Schweiz', 'Deutschland'],
               'familyName': ['Borel'],
               'claims': {},
               'id': 'Q12349739'}}]}}),
    ("Jean Bodel", "1897", 3, False, 
     {
        '118660454': {
            'desc': {'Old French poet'},
            'birthplaceLiteral': {'Arras'},
            'prefForename': {'Jean'},
            'prefSurname': {'Bodel'},
            'jobliteral': {'Dichter', 'Musiker', 'Schriftsteller', 'Troubadour'},
            'birthdate': {'1165-00-00'},
            'deathdate': {'1210-00-00'},
            'deathplaceLiteral': {'Beaurain'},
            'gid': {'118660454'},
            'name': {'Jean Bodel'},
            'score': 1.0}},
     {
        'hits': {
        'total': {'value': 1, 'relation': 'eq'},
        'max_score': 22.740044,
        'hits': [
            {'_index': 'wikidata-v2',
             '_id': 'La7lYYsBW8gB8I1ONzdh',
             '_score': 22.740044,
             '_source': {
                 'nativeName': ['Jean Bodel'],
                 'placeOfBirth': ['Arras'],
                 'aliases': ['Bodel'],
                 'occupation': ['Dichter', 'Schriftsteller', 'Musiker', 'Troubadour'],
                 'gender': ['männlich'],
                 'dateOfDeath': ['+1210-00-00T00:00:00Z'],
                 'givenName': ['Jean'],
                 'dateOfBirth': ['+1165-00-00T00:00:00Z'],
                 'placeOfDeath': ['Beaurain'],
                 'descriptions': 'Old French poet',
                 'GND_ID': ['118660454'],
                 'labels': 'Jean Bodel',
                 'instanceOf': ['Q5'],
                 'GND_ID_2': ['118660454'],
                 'countryOfCitizenship': ['Frankreich'],
                 'familyName': ['Bodel'],
                 'claims': {}, 
                 'id': 'Q5172',
                 'causeOfDeath': ['Lepra']}}]}})
]
PARAMS_convert_wikidata_format_kibana = [
    ({'labels': 'Derek Birdsall',
      'descriptions': 'British graphic designer',
      'gender': ['männlich'],
      'instanceOf': ['Q5'],
      'occupation': ['Grafikdesigner'],
      'GND_ID': ['129263265'],
      'dateOfBirth': ['+1934-08-01T00:00:00Z'],
      'familyName': ['Birdsall'],
      'givenName': ['Derek']},
     {'desc': {'British graphic designer'},
      'prefForename': {'Derek'},
      'prefSurname': {'Birdsall'},
      'jobliteral': {'Grafikdesigner'},
      'birthdate': {'1934-08-01'},
      'gid': {'129263265'},
      'name': {'Derek Birdsall'}}),
    ({'labels': 'Douglas Birdsall',
      'instanceOf': ['Q5'],
      'GND_ID': ['1119113008']},
     {'gid': {'1119113008'},
      'name': {'Douglas Birdsall'},
      'prefSurname': {'Birdsall'},
      'prefForename': {'Douglas'}}),
    ({'labels': 'Johann Josef Bitschnau',
      'gender': ['männlich'],
      'instanceOf': ['Q5'],
      'occupation': ['Arzt', 'Historiker', 'Rechtsanwalt', 'Politiker'],
      'GND_ID': ['1065067526'],
      'dateOfBirth': ['+1776-00-00T00:00:00Z'],
      'dateOfDeath': ['+1819-00-00T00:00:00Z'],
      'givenName': ['Johann'],
      'GND_ID_2': ['1065067526']},
     {'prefForename': {'Johann'},
      'jobliteral': {'Arzt', 'Historiker', 'Politiker', 'Rechtsanwalt'},
      'birthdate': {'1776-00-00'},
      'deathdate': {'1819-00-00'},
      'gid': {'1065067526'},
      'name': {'Johann Josef Bitschnau'},
      'prefSurname': {'Bitschnau'}}),
    ({'labels': 'Victor Amadeus II of Savoy',
      'descriptions': 'Duke of Savoy and King of Sardinia (1675-1732)',
      'placeOfBirth': ['Turin'],
      'placeOfDeath': ['Moncalieri', 'Rivoli'],
      'gender': ['männlich'],
      'spouse': ['Anne Marie d’Orléans', 'Anna Canalis di Cumiana'],
      'P27': [],
      'instanceOf': ['Q5'],
      'occupation': ['Politiker'],
      'GND_ID': ['118804537'],
      'causeOfDeath': ['Schlaganfall'],
      'dateOfBirth': ['+1666-05-14T00:00:00Z'],
      'dateOfDeath': ['+1732-10-31T00:00:00Z'],
      'familyName': ['Savoia'],
      'givenName': ['Victor-Amédée'],
      'mannerOfDeath': ['natürliche Todesursache'],
      'nativeName': ['Victorius Amadeus II',
                     'Victor-Amédée II',
                     'Vittorio Amedeo II'],
      'GND_ID_2': ['118804537']},
     {'desc': {'Duke of Savoy and King of Sardinia (1675-1732)'},
      'birthplaceLiteral': {'Turin'},
      'prefForename': {'Victor-Amédée'},
      'prefSurname': {'Savoia'},
      'jobliteral': {'Politiker'},
      'birthdate': {'1666-05-14'},
      'deathdate': {'1732-10-31'},
      'deathplaceLiteral': {'Moncalieri', 'Rivoli'},
      'gid': {'118804537'},
      'name': {'Victor Amadeus II of Savoy'}}),
    ({'labels': 'Victor Amadeus I of Savoy',
      'descriptions': 'Duke of Savoy (1587–1637)',
      'placeOfBirth': ['Turin'],
      'placeOfDeath': ['Vercelli'],
      'gender': ['männlich'],
      'spouse': ['Christina von Frankreich'],
      'instanceOf': ['Q5'],
      'occupation': ['Aristokrat', 'Politiker'],
      'GND_ID': ['135979773'],
      'causeOfDeath': ['Krankheit'],
      'dateOfBirth': ['+1587-05-08T00:00:00Z'],
      'dateOfDeath': ['+1637-10-07T00:00:00Z'],
      'familyName': ['Savoia'],
      'givenName': ['Victor-Amédée'],
      'GND_ID_2': ['135979773']},
     {'desc': {'Duke of Savoy (1587–1637)'},
      'birthplaceLiteral': {'Turin'},
      'prefForename': {'Victor-Amédée'},
      'prefSurname': {'Savoia'},
      'jobliteral': {'Aristokrat', 'Politiker'},
      'birthdate': {'1587-05-08'},
      'deathdate': {'1637-10-07'},
      'deathplaceLiteral': {'Vercelli'},
      'gid': {'135979773'},
      'name': {'Victor Amadeus I of Savoy'}}),
    ({'labels': 'Viktor Paul Amadeus von Wolff',
      'gender': ['männlich'],
      'spouse': ['Marie Anna Eva von Wolff'],
      'instanceOf': ['Q5'],
      'GND_ID': ['1193647002'],
      'dateOfBirth': ['+1821-00-00T00:00:00Z'],
      'dateOfDeath': ['+1880-00-00T00:00:00Z'],
      'givenName': ['Viktor'],
      'GND_ID_2': ['1193647002']},
     {'prefForename': {'Viktor'},
      'birthdate': {'1821-00-00'},
      'deathdate': {'1880-00-00'},
      'gid': {'1193647002'},
      'name': {'Viktor Paul Amadeus von Wolff'},
      'prefSurname': {'Wolff'}}),
    ({'labels': 'Viktor Amadeus Henckel von Donnersmarck',
      'descriptions': '(1727-1793)',
      'placeOfBirth': ['Mierczyce'],
      'placeOfDeath': ['Königsberg'],
      'gender': ['männlich'],
      'spouse': ['Eleonore Maximiliane Ottilie Henckel von Donnersmarck'],
      'countryOfCitizenship': ['Königreich Preußen'],
      'instanceOf': ['Q5'],
      'occupation': ['Kammerherr'],
      'GND_ID': ['142136859'],
      'dateOfBirth': ['+1727-09-15T00:00:00Z'],
      'dateOfDeath': ['+1793-01-31T00:00:00Z'],
      'givenName': ['Viktor'],
      'GND_ID_2': ['142136859']},
     {'desc': {'(1727-1793)'},
      'birthplaceLiteral': {'Mierczyce'},
      'prefForename': {'Viktor'},
      'jobliteral': {'Kammerherr'},
      'birthdate': {'1727-09-15'},
      'deathdate': {'1793-01-31'},
      'deathplaceLiteral': {'Königsberg'},
      'gid': {'142136859'},
      'name': {'Viktor Amadeus Henckel von Donnersmarck'},
      'prefSurname': {'Donnersmarck'}}),
    ({'labels': 'Viktor Amadeus Meyer',
      'gender': ['männlich'],
      'instanceOf': ['Q5'],
      'occupation': ['Mittelschullehrer'],
      'GND_ID': ['117569518'],
      'dateOfBirth': ['+1828-00-00T00:00:00Z'],
      'givenName': ['Viktor'],
      'GND_ID_2': ['117569518']},
     {'prefForename': {'Viktor'},
      'jobliteral': {'Mittelschullehrer'},
      'birthdate': {'1828-00-00'},
      'gid': {'117569518'},
      'name': {'Viktor Amadeus Meyer'},
      'prefSurname': {'Meyer'}}),
    ({'labels': 'Manfred Hürlimann',
      'descriptions': 'Swiss artist',
      'placeOfBirth': ['Oberstaufen'],
      'gender': ['männlich'],
      'countryOfCitizenship': ['Schweiz', 'Deutschland'],
      'instanceOf': ['Q5'],
      'occupation': ['Maler'],
      'GND_ID': ['119192241'],
      'dateOfBirth': ['+1958-09-29T00:00:00Z'],
      'familyName': ['Hürlimann'],
      'givenName': ['Manfred']},
     {'desc': {'Swiss artist'},
      'birthplaceLiteral': {'Oberstaufen'},
      'prefForename': {'Manfred'},
      'prefSurname': {'Hürlimann'},
      'jobliteral': {'Maler'},
      'birthdate': {'1958-09-29'},
      'gid': {'119192241'},
      'name': {'Manfred Hürlimann'}})
]
PARAMS_convert_gnd_format_kibana = [
    (es_171726375, {
        'gid': {'171726375'},
        'prefForename': {'David'},
        'prefSurname': {'Birchall'},
        'varForename': {'D.', 'D. W.', 'David W.'},
        'varSurname': {'Birchall'},
        'academic': {'Prof. em.'},
        'desc': {
            'Henley Management College, Henley Business School, Univ. of \
Reading'}
    }),
    (es_1089259662, {
    'gid': {'1089259662'},
    'prefForename': {'J. D.'},
    'prefSurname': {'Birchall'},
    'desc': {'Chemiker, USA'}
    }),
    (
        {'gndIdentifier': '1033767735',
         'preferredNameEntityForThePerson': {
            'forename': ['Josef'],
            'surname': ['Bitschnau'],
         },
         'dateOfBirth': ['1925-10-10']},
        {'gid': {'1033767735'},
         'prefForename': {'Josef'},
         'prefSurname': {'Bitschnau'},
         'birthdate': {'1925-10-10'}}
    ),
    (
        {'gndIdentifier': '1065067526',
         'preferredNameEntityForThePerson': {
            'forename': ['Johann Josef'],
            'surname': ['Bitschnau'],
         },
         'academicDegree': ['Dr.jur.et med.'],
         'dateOfBirth': ['1776'],
         'dateOfDeath': ['1819']},
        {'gid': {'1065067526'},
         'prefForename': {'Johann Josef'},
         'prefSurname': {'Bitschnau'},
         'academic': {'Dr.jur.et med.'},
         'birthdate': {'1776'},
         'deathdate': {'1819'}}
    ),
    (
        {'gndIdentifier': '1056411104',
         'preferredNameEntityForThePerson': {
            'forename': ['Victor Oliveira'],
            'surname': ['Mateus'],
         },
         'variantNameEntityForThePerson': {
            'forename': ['Victor'],
            'surname': ['Oliveira Mateus'],
         },
         'biographicalOrHistoricalInformation': ['geb. in Lissabon', ' Philosoph u. Dichter']},
        {'gid': {'1056411104'},
         'prefForename': {'Victor Oliveira'},
         'prefSurname': {'Mateus'},
         'varForename': {'Victor'},
         'varSurname': {'Oliveira Mateus'},
         'desc': {'geb. in Lissabon', ' Philosoph u. Dichter'}}),
    (
        {'gndIdentifier': '1147518866',
         'preferredNameEntityForThePerson': {
            'forename': ['Charles'],
            'surname': ['Hirlimann'],
         },
         'dateOfBirth': ['1947']},
        {'gid': {'1147518866'},
         'prefForename': {'Charles'},
         'prefSurname': {'Hirlimann'},
         'birthdate': {'1947'}}
    ),
    (
        {'gndIdentifier': '115824839',
         'preferredNameEntityForThePerson': {
            'forename': ['Christoph'],
            'surname': ['Hürlimann'],
         },
         'biographicalOrHistoricalInformation': ['Theologe', ' Schriftsteller'],
         'dateOfBirth': ['1938']},
        {'gid': {'115824839'},
         'prefForename': {'Christoph'},
         'prefSurname': {'Hürlimann'},
         'birthdate': {'1938'},
         'desc': {'Theologe', ' Schriftsteller'}}
    ),
    (
        {'gndIdentifier': '1066273278',
         'preferredNameEntityForThePerson': {
            'forename': ['Urs Josef'],
            'surname': ['Cavelti'],
         },
         'variantNameEntityForThePerson': {
            'forename': ['Urs Joseph', 'Urs J.', 'Urs'],
            'surname': ['Cavelti'],
         },
         'biographicalOrHistoricalInformation': ['St. Galler Politiker, Rechtsanwalt und Redaktor'],
         'dateOfBirth': ['1927-09-03'],
         'dateOfDeath': ['2003-11-04']},
        {'gid': {'1066273278'},
         'prefForename': {'Urs Josef'},
         'prefSurname': {'Cavelti'},
         'varForename': {'Urs', 'Urs J.', 'Urs Joseph'},
         'varSurname': {'Cavelti'},
         'birthdate': {'1927-09-03'},
         'deathdate': {'2003-11-04'},
         'desc': {'St. Galler Politiker, Rechtsanwalt und Redaktor'}}
    )
]

PARAMS_test_aggregate_with = [
    ({"x": [
         {
          "info": {
              "lastnames": "Müller",
              "firstnames": "Maria",
              "abbr_firstnames": "",
              "titles": ["match_titles"],
              "address": ["match_address"],
              "occupations": ["match_occupations"],
              "others": ["match_others"]
          },
          "pageNo": 44,
          "sentenceNo": 55,
          "pageNames": "",
          "pid": "",
          "positions": "",
          "articles": "",
          'type': 'PER'
          }
        ]
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example1")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": {()},
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
    "fullfirstnames",
    [{'firstname': {('Anna', 'Maria'), ('Maria',)},
      'lastname': 'Müller',
      'abbr_firstname': set(),
      'titles': {('match_titles',), ('Frau', 'Dr.')},
      'address': {('match_address',), ('a', 'b')},
      'profession': {('match_occupations',), ('c', 'd')},
      'other': {'example1', ('match_others',)},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')],
          (44, '', ''): [(55, '', '')]}},
     {'firstname': {('Kat', 'Man')},
      'lastname': 'Bil',
      'abbr_firstname': {()},
      'titles': {('Herr', 'Prof')},
      'address': {('a', 'b')},
      'profession': {('c', 'd')},
      'other': {},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}
      }]
    ),
    ({"x": [
        {
            "info": {
                "lastnames": "Müller",
                "firstnames": "",
                "abbr_firstnames": "M",
                "titles": "",
                "address": "",
                "occupations": "",
                "others": ["example3"]
             },
            "pageNo": 44,
            "sentenceNo": 55,
            "pageNames": "",
            "pid": "",
            "positions": "",
            "articles": "",
            'type': 'PER'
         }
       ]
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example2")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
     {"firstname": {("Kat", "Man")},
      "lastname": "Bil",
      "abbr_firstname": {()},
      "titles": {("Herr", "Prof")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {},
      "references": {
                (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
            }
      }],
       "fullfirstnames",
       [{'firstname': {('Anna', 'Maria')},
         'lastname': 'Müller',
         'abbr_firstname': {()},
         'titles': {('Frau', 'Dr.')},
         'address': {('a', 'b')},
         'profession': {('c', 'd')},
         'other': {'example2'},
         'references': {
            (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}},
        {'firstname': {('Kat', 'Man')},
         'lastname': 'Bil',
         'abbr_firstname': {()},
         'titles': {('Herr', 'Prof')},
         'address': {('a', 'b')},
         'profession': {('c', 'd')},
         'other': {},
         'references': {
             (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}},
        {'lastname': 'Müller',
         'firstname': {()},
         'abbr_firstname': {('M',)},
         'address': {()},
         'titles': {()},
         'profession': {()},
         'other': {('example3',)},
         'references': {
             (44, '', ''): [(55, '', '')]},
         'type': 'PER'}]
    ),
    ({"x": [
         {
          "info": {
              "lastnames": "Müller",
              "firstnames": "",
              "abbr_firstnames": "M",
              "titles": ["match_titles"],
              "address": ["match_address"],
              "occupations": ["match_occupations"],
              "others": ["match_others"]
          },
          "pageNo": 44,
          "sentenceNo": 55,
          "pageNames": "",
          "pid": "",
          "positions": "",
          "articles": "",
          'type': 'PER'
          }
        ]
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example5")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": {()},
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
    "abbrevs",
    [{'firstname': {('Anna', 'Maria')},
      'lastname': 'Müller',
      'abbr_firstname': {('M',)},
      'titles': {('match_titles',), ('Frau', 'Dr.')},
      'address': {('a', 'b'), ('match_address',)},
      'profession': {('match_occupations',), ('c', 'd')},
      'other': {'example5', ('match_others',)},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')],
          (44, '', ''): [(55, '', '')]}},
     {'firstname': {('Kat', 'Man')},
      'lastname': 'Bil',
      'abbr_firstname': {()},
      'titles': {('Herr', 'Prof')},
      'address': {('a', 'b')},
      'profession': {('c', 'd')},
      'other': {},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}
      }]
    ),
   ({"x": [
        {
            "info": {
                "lastnames": "Müller",
                "firstnames": "",
                "abbr_firstnames": "D",
                "titles": "",
                "address": "",
                "occupations": "",
                "others": ["example8"]
             },
            "pageNo": 44,
            "sentenceNo": 55,
            "pageNames": "",
            "pid": "",
            "positions": "",
            "articles": "",
            'type': 'PER'
         }
       ]
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example6")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
     {"firstname": {("Kat", "Man")},
      "lastname": "Bil",
      "abbr_firstname": {()},
      "titles": {("Herr", "Prof")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {},
      "references": {
                (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
            }
      }],
    "abbrevs",
    [{'firstname': {('Anna', 'Maria')},
      'lastname': 'Müller',
      'abbr_firstname': {()},
      'titles': {('Frau', 'Dr.')},
      'address': {('a', 'b')},
      'profession': {('c', 'd')},
      'other': {'example6'},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}},
     {'firstname': {('Kat', 'Man')},
      'lastname': 'Bil',
      'abbr_firstname': {()},
      'titles': {('Herr', 'Prof')},
      'address': {('a', 'b')},
      'profession': {('c', 'd')},
      'other': {},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}},
     {'lastname': 'Müller',
      'firstname': {()},
      'abbr_firstname': {('D',)},
      'address': {()},
      'titles': {()},
      'profession': {()},
      'other': {('example8',)},
      'references': {
          (44, '', ''): [(55, '', '')]},
      'type': 'PER'}]
    ),
    ({"x": [
         {
          "info": {
              "lastnames": "Müller",
              "firstnames": "",
              "abbr_firstnames": "M",
              "titles": ["match_titles"],
              "address": ["match_address"],
              "occupations": ["match_occupations"],
              "others": ["match_others"]
          },
          "pageNo": 44,
          "sentenceNo": 55,
          "pageNames": "",
          "pid": "",
          "positions": "",
          "articles": "",
          'type': 'PER'
          }
        ]
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example9")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": {()},
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
    "onlylastnames",
    [{'firstname': {('Anna', 'Maria')},
      'lastname': 'Müller',
      'abbr_firstname': {('M',)},
      'titles': {('match_titles',), ('Frau', 'Dr.')},
      'address': {('a', 'b'), ('match_address',)},
      'profession': {('match_occupations',), ('c', 'd')},
      'other': {'example9', ('match_others',)},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')],
          (44, '', ''): [(55, '', '')]}},
     {'firstname': {('Kat', 'Man')},
      'lastname': 'Bil',
      'abbr_firstname': {()},
      'titles': {('Herr', 'Prof')},
      'address': {('a', 'b')},
      'profession': {('c', 'd')},
      'other': {},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}
      }]
    ),
   ({"x": [
         {
             "info": {
                 "lastnames": "Müller",
                 "firstnames": "x",
                 "abbr_firstnames": "",
                 "titles": ["match_titles"],
                 "address": ["match_address"],
                 "occupations": ["match_occupations"],
                 "others": ["match_others"]
              },
             "pageNo": 44,
             "sentenceNo": 55,
             "pageNames": "",
             "pid": "",
             "positions": "",
             "articles": "",
             'type': 'PER'
          }
        ]
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example9")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": {()},
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
    "onlylastnames",
    [{'firstname': {('x',), ('Anna', 'Maria')},
        'lastname': 'Müller',
        'abbr_firstname': set(),
        'titles': {('Frau', 'Dr.'), ('match_titles',)},
        'address': {('match_address',), ('a', 'b')},
        'profession': {('c', 'd'), ('match_occupations',)},
        'other': {('match_others',), 'example9'},
        'references': {
            (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')],
            (44, '', ''): [(55, '', '')]}},
       {'firstname': {('Kat', 'Man')},
        'lastname': 'Bil',
        'abbr_firstname': {()},
        'titles': {('Herr', 'Prof')},
        'address': {('a', 'b')},
        'profession': {('c', 'd')},
        'other': {},
        'references': {
            (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}
        }]),
    ({"x": [
         {
             "info": {
                 "lastnames": "z",
                 "firstnames": "Anna",
                 "abbr_firstnames": "",
                 "titles": "",
                 "address": "",
                 "occupations": "",
                 "others": "e"
              },
             "pageNo": 44,
             "sentenceNo": 55,
             "pageNames": "",
             "pid": "",
             "positions": "",
             "articles": "",
             'type': 'PER'
          }
        ]
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example10")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": {()},
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
    "onlyfirstnames",
    [
     {'firstname': {('Anna', 'Maria')},
      'lastname': 'Müller',
      'abbr_firstname': {()},
      'titles': {('Frau', 'Dr.')},
      'address': {('a', 'b')},
      'profession': {('c', 'd')},
      'other': {'example10'},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'),
                          (6, '456', '456')]}},
     {'firstname': {('Kat', 'Man')},
      'lastname': 'Bil',
      'abbr_firstname': {()},
      'titles': {('Herr', 'Prof')},
      'address': {('a', 'b')},
      'profession': {('c', 'd')},
      'other': {},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'),
                          (6, '456', '456')]}},
     {'firstname': {('Anna',)},
      'lastname': 'z',
      'abbr_firstname': {()},
      'titles': {()},
      'address': {()},
      'profession': {()},
      'other': {('e',)},
      'references': {(44, '', ''): [(55, '', '')]},
      'type': 'PER'}
     ]
    ),
   ({"x": [
       {"info": {"lastnames": "z", "firstnames": "x",
                 "abbr_firstnames": "A",
                 "titles": ["titles_newmatch"],
                 "address": ["address_newmatch"],
                 "occupations": ["occupation_newmatch"],
                 "others": ["others_newmatch"]},
        "pageNo": 44, "sentenceNo": 55, "pageNames": "", "pid": "",
        "positions": "", "articles": "", 'type': 'PER'
        }]
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {"A"},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example11")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": {()},
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
    "onlyabbrevfirstnames",
    [{'firstname': {('x',), ('Anna', 'Maria')},
      'lastname': 'Müller',
      'abbr_firstname': {('A',), 'A'},
      'titles': {('Frau', 'Dr.'), ('titles_newmatch',)},
      'address': {('a', 'b'), ('address_newmatch',)},
      'profession': {('c', 'd'), ('occupation_newmatch',)},
      'other': {('others_newmatch',), 'example11'},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')],
          (44, '', ''): [(55, '', '')]}},
     {'firstname': {('Kat', 'Man')},
      'lastname': 'Bil',
      'abbr_firstname': {()},
      'titles': {('Herr', 'Prof')},
      'address': {('a', 'b')},
      'profession': {('c', 'd')},
      'other': {},
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}}]
    ),
    ({("e",): [
      {"info": {"lastnames": "z",
                "firstnames": "x",
                "abbr_firstnames": "y",
                "titles": "",
                "address": "",
                "occupations": "",
                "others": ["example12"]},
       "pageNo": 4,
       "sentenceNo": 5,
       "pageNames": "",
       "pid": "",
       "positions": "",
       "articles": "",
       'type': 'PER'}],
     ("b",): [
      {"info": {"lastnames": "",
                "firstnames": "",
                "abbr_firstnames": "",
                "titles": "",
                "address": "",
                "occupations": "",
                "others": ["example12"]},
       "pageNo": 0,
       "sentenceNo": 11,
       "pageNames": "",
       "pid": "",
       "positions": "",
       "articles": ""}]},
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("example12",)},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": {()},
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
    "others",
    # # # # sol # # # #
    [{'abbr_firstname': {('y',)},
      'address': {('a', 'b')},
      'firstname': {('Anna', 'Maria'), ('x',)},
      'lastname': 'Müller',
      'other': {('example12',)},
      'profession': {('c', 'd')},
      'references': {(0, '', ''): [(11, '', '')], (4, '', ''): [(5, '', '')],
                     (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]},
      'titles': {('Frau', 'Dr.')}},
     {'abbr_firstname': {()},
      'address': {('a', 'b')},
      'firstname': {('Kat', 'Man')},
      'lastname': 'Bil',
      'other': {},
      'profession': {('c', 'd')},
      'references': {(4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]},
      'titles': {('Herr', 'Prof')}
      }]
    )
]

PARAMS_test_full_firstname_match = [
    ({"info": {"lastnames": "Müller",
              "firstnames": "Maria",
              "abbr_firstnames": "",
              "titles": ["match_titles"],
              "address": ["match_address"],
              "occupations": ["match_occupations"],
              "others": ["match_others"]},
     "pageNo": 44,
     "sentenceNo": 55,
     "pageNames": "",
     "pid": "",
     "positions": "",
     "articles": "",
     'type': 'PER'
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": set(),
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": set(),
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
      {'firstname': {('Anna', 'Maria')},
       'lastname': 'Müller',
       'abbr_firstname': set(),
       'titles': {('Frau', 'Dr.')},
       'address': {('a', 'b')},
       'profession': {('c', 'd')},
       'other': {'e'},
       'references': {(4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}}
    ),
    ({"info": {"lastnames": "x",
              "firstnames": "Maria",
              "abbr_firstnames": "",
              "titles": ["match_titles"],
              "address": ["match_address"],
              "occupations": ["match_occupations"],
              "others": ["match_others"]},
     "pageNo": 44,
     "sentenceNo": 55,
     "pageNames": "",
     "pid": "",
     "positions": "",
     "articles": "",
     'type': 'PER'
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": set(),
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": set(),
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
     None)
]
PARAMS_abbrev_firstname_match = [
    ({"info": {"lastnames": "Müller",
              "firstnames": "",
              "abbr_firstnames": "M",
              "titles": ["match_titles"],
              "address": ["match_address"],
              "occupations": ["match_occupations"],
              "others": ["match_others"]},
     "pageNo": 44,
     "sentenceNo": 55,
     "pageNames": "",
     "pid": "",
     "positions": "",
     "articles": "",
     'type': 'PER'
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": set(),
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": set(),
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
      [{'firstname': {('Anna', 'Maria')},
        'lastname': 'Müller',
        'abbr_firstname': set(),
        'titles': {('Frau', 'Dr.')},
        'address': {('a', 'b')},
        'profession': {('c', 'd')},
        'other': {'e'},
        'references': {
            (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]}}]
    )
]
PARAMS_only_lastname_match = [
    ({"info": {"lastnames": "Müller", "firstnames": "x",
              "abbr_firstnames": "",
              "titles": "", "address": "", "occupations": "",
              "others": "e"},
     "pageNo": 4, "sentenceNo": 5, "pageNames": "", "pid": "",
     "positions": "", "articles": "", 'type': 'PER'
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": set(),
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": set(),
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
      [{'firstname': {('Anna', 'Maria')},
        "lastname": "Müller",
        "abbr_firstname": set(),
        "titles": {("Frau", "Dr.")},
        "address": {("a", "b")},
        "profession": {("c", "d")},
        "other": {("e")},
        "references": {
                 (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
             }
        }]
    )
]
PARAMS_aggregate_names = [
    ((("abc", "1234"), [{'info': {
    # If one of the firstnames matches, we match
         'lastnames': ['Müller'], 'firstnames': ['Anne'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt',
         'pageNo': 1, 'sentenceNo': 29,
         'positions': ['865,1781,49,22:main', '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
       {'info': {
         'lastnames': ['Müller'], 'firstnames': ['Anne', 'Marie'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
         'sentenceNo': 30,
         'positions': [
            '789,2016,48,22:main',
            '847,2013,65,30:main',
            '920,2014,101,24:main'],
         'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001.json"]),
      [{'lastname': 'Müller', 'firstname': ['Anne', 'Anne Marie'],
        'abbr_firstname': [], 'address': [], 'titles': [], 'profession': [],
        'other': [],
        'references': {
            'abc-001_1234_123_0001.txt': {
                'pid': 1,
                'refs': [
                   {'sent': 29,
                    'coords': ['865,1781,49,22:main', '924,1780,100,23:main']},
                   {'sent': 30,
                    'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                               '920,2014,101,24:main']}],
                'elements': []}},
        'type': 'PER', 'id': 0}]),
     # if we have the genetiv version, we clean it up and still match
     ((("abc", "1234"), [{'info': {
         'lastnames': ['Müller'], 'firstnames': ['Maria'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt',
         'pageNo': 1, 'sentenceNo': 29,
         'positions': ['865,1781,49,22:main', '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
       {'info': {
         'lastnames': ['Müllers'], 'firstnames': ['Maria'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt',
         'pageNo': 1, 'sentenceNo': 30,
         'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                       '920,2014,101,24:main'],
         'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001.json"]),
      [{'lastname': 'Müller', 'firstname': ['Maria'], 'abbr_firstname': [],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
            'abc-001_1234_123_0001.txt': {
               'pid': 1,
               'refs': [
                   {'sent': 29,
                    'coords': ['865,1781,49,22:main', '924,1780,100,23:main']},
                   {'sent': 30,
                    'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                               '920,2014,101,24:main']}],
               'elements': []}},
        'type': 'PER',
        'id': 0}]),
     # page number, page name, pid do not matter if both firstname
     # and lastname match, we match all mentions within a magazine-year
     ((("abc", "1234"), [{'info': {
         'lastnames': ['Müller'], 'firstnames': ['Maria'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
         'sentenceNo': 29, 'positions': ['865,1781,49,22:main',
                                         '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
       {'info': {
           'lastnames': ['Müllers'], 'firstnames': ['Maria'],
           'abbr_firstnames': [], 'occupations': [], 'titles': [],
           'address': [], 'others': []}, 'pid': 100,
           'pageNames': 'abc-001_1234_123_0100.txt', 'pageNo': 100,
           'sentenceNo': 30,
           'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                         '920,2014,101,24:main'],
           'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001.json", "abc-001_1234_123_0100.json"]),
      [{'lastname': 'Müller', 'firstname': ['Maria'], 'abbr_firstname': [],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
           'abc-001_1234_123_0001.txt': {
              'pid': 1,
              'refs': [
                  {'sent': 29,
                   'coords': ['865,1781,49,22:main', '924,1780,100,23:main']}],
              'elements': []},
           'abc-001_1234_123_0100.txt': {
              'pid': 100,
              'refs': [
                  {'sent': 30,
                   'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                              '920,2014,101,24:main']}],
              'elements': []}},
        'type': 'PER', 'id': 0}]),
     # even if the names are close, we do not match if the names don't match
     ((("abc", "1234"), [{'info': {
         'lastnames': ['Müller'], 'firstnames': ['Maria'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
         'sentenceNo': 29, 'positions': ['865,1781,49,22:main',
                                         '924,1780,100,23:main'],
        'type': 'PER', 'articles': []},
      {'info': {
          'lastnames': ['Müller'], 'firstnames': ['Meria'],
          'abbr_firstnames': [], 'occupations': [], 'titles': [],
          'address': [], 'others': []}, 'pid': 1,
          'pageNames': 'abc-001_1234_123_0001.txt',
          'pageNo': 1, 'sentenceNo': 30,
          'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                        '920,2014,101,24:main'],
          'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001.json"]),
      [{'lastname': 'Müller', 'firstname': ['Maria'], 'abbr_firstname': [],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
            'abc-001_1234_123_0001.txt': {
              'pid': 1,
              'refs': [
                  {'sent': 29,
                   'coords': ['865,1781,49,22:main', '924,1780,100,23:main']}],
              'elements': []}},
        'type': 'PER', 'id': 0},
       {'lastname': 'Müller', 'firstname': ['Meria'], 'abbr_firstname': [],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
            'abc-001_1234_123_0001.txt': {
                'pid': 1,
                'refs': [
                    {'sent': 30,
                     'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                                '920,2014,101,24:main']}],
                'elements': []}},
        'type': 'PER', 'id': 1}]),
     # if the lastname matches the firstnames don't contradict each other,
     # and we're closer than to any other person, we match.
     ((("abc", "1234"), [{'info': {
         'lastnames': ['Müller'], 'firstnames': ['Maria'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
         'sentenceNo': 29, 'positions': ['865,1781,49,22:main',
                                         '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
      {'info': {
          'lastnames': ['Müller'], 'firstnames': [''], 'abbr_firstnames': [],
          'occupations': [], 'titles': [], 'address': [], 'others': []},
          'pid': 1, 'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
          'sentenceNo': 30,
          'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                        '920,2014,101,24:main'],
          'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001"]),
      [{'lastname': 'Müller', 'firstname': ['Maria'], 'abbr_firstname': [],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
           'abc-001_1234_123_0001.txt': {
               'pid': 1,
               'refs': [
                   {'sent': 29,
                    'coords': ['865,1781,49,22:main', '924,1780,100,23:main']},
                   {'sent': 30,
                    'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                               '920,2014,101,24:main']}],
               'elements': []}},
        'type': 'PER', 'id': 0}]),
     # the second occurrence of Müller is matched to martin instead of maria
     # because we go through the people and ONLY match with previous
     # occurrences, never with future ones.
     # this is intended behavior
     ((("abc", "1234"), [{'info': {
         'lastnames': ['Müller'], 'firstnames': ['Martin'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 9,
         'pageNames': 'abc-001_1234_123_0009.txt', 'pageNo': 9,
         'sentenceNo': 27, 'positions': ['865,1781,49,22:main',
                                         '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
       {'info': {
           'lastnames': ['Müller'], 'firstnames': [''], 'abbr_firstnames': [],
           'occupations': [], 'titles': [], 'address': [], 'others': []},
           'pid': 10, 'pageNames': 'abc-001_1234_123_0010.txt', 'pageNo': 10,
           'sentenceNo': 28,
           'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                         '920,2014,101,24:main'],
           'type': 'PER', 'articles': []},
       {'info': {
           'lastnames': ['Müller'], 'firstnames': ['Maria'],
           'abbr_firstnames': [], 'occupations': [], 'titles': [],
           'address': [], 'others': []}, 'pid': 11,
           'pageNames': 'abc-001_1234_123_0011.txt', 'pageNo': 11,
           'sentenceNo': 29,
           'positions': ['865,1781,49,22:main', '924,1780,100,23:main'],
           'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0010.json", "abc-001_1234_123_0011.json"]),
      [{'lastname': 'Müller', 'firstname': ['Maria'], 'abbr_firstname': [],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
            'abc-001_1234_123_0011.txt': {
              'pid': 11,
              'refs': [
                  {'sent': 29,
                   'coords': ['865,1781,49,22:main', '924,1780,100,23:main']}],
              'elements': []}},
        'type': 'PER', 'id': 0},
       {'lastname': 'Müller', 'firstname': ['Martin'], 'abbr_firstname': [],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
            'abc-001_1234_123_0009.txt': {
              'pid': 9,
              'refs': [
                  {'sent': 27,
                   'coords': ['865,1781,49,22:main', '924,1780,100,23:main']}],
              'elements': []},
            'abc-001_1234_123_0010.txt': {
                'pid': 10,
                'refs': [
                    {'sent': 28,
                     'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                                '920,2014,101,24:main']}],
                'elements': []}},
        'type': 'PER', 'id': 1}]),
     # abbreviated firstnames and same lastnames are matched.
     ((("abc", "1234"), [{'info': {
         'lastnames': ['Müller'], 'firstnames': ['Maria'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
         'sentenceNo': 29, 'positions': ['865,1781,49,22:main',
                                         '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
      {'info': {
          'lastnames': ['Müller'], 'firstnames': [], 'abbr_firstnames': ["M."],
          'occupations': [], 'titles': [], 'address': [], 'others': []},
          'pid': 1, 'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
          'sentenceNo': 30,
          'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                        '920,2014,101,24:main'],
          'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001.json"]),
      [{'lastname': 'Müller', 'firstname': ['Maria'], 'abbr_firstname': ['M.'],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
            'abc-001_1234_123_0001.txt': {
                'pid': 1, 'refs': [
                   {'sent': 29,
                    'coords': ['865,1781,49,22:main', '924,1780,100,23:main']},
                   {'sent': 30,
                    'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                               '920,2014,101,24:main']}],
                'elements': []}},
        'type': 'PER', 'id': 0}]),
     # same firstnames and not conflicing lastnames are matched.
     ((("abc", "1234"), [{'info': {
         'lastnames': [], 'firstnames': ['Maria'],
         'abbr_firstnames': [], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
         'sentenceNo': 29, 'positions': ['865,1781,49,22:main',
                                         '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
       {'info': {
           'lastnames': [], 'firstnames': ["Maria"], 'abbr_firstnames': [],
           'occupations': [], 'titles': [], 'address': [], 'others': []},
           'pid': 100, 'pageNames': 'abc-001_1234_123_0100.txt', 'pageNo': 100,
           'sentenceNo': 30,
           'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                         '920,2014,101,24:main'],
           'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001.json", "abc-001_1234_123_0100.json"]),
      [{'lastname': '', 'firstname': ['Maria'], 'abbr_firstname': [],
        'address': [], 'titles': [], 'profession': [], 'other': [],
        'references': {
            'abc-001_1234_123_0001.txt': {
              'pid': 1, 'refs': [
                  {'sent': 29,
                   'coords': ['865,1781,49,22:main', '924,1780,100,23:main']}],
              'elements': []},
            'abc-001_1234_123_0100.txt': {
              'pid': 100, 'refs': [
                  {'sent': 30,
                   'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                              '920,2014,101,24:main']}],
              'elements': []}},
        'type': 'PER', 'id': 0}]),
     # same abbreviated firstnames and not conflicing lastnames are not matched.
     ((("abc", "1234"), [{'info': {
         'lastnames': [], 'firstnames': ['Maria'],
         'abbr_firstnames': ["A."], 'occupations': [], 'titles': [],
         'address': [], 'others': []}, 'pid': 1,
         'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
         'sentenceNo': 29, 'positions': ['865,1781,49,22:main',
                                         '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
       {'info': {
           'lastnames': [], 'firstnames': [], 'abbr_firstnames': ["A."],
           'occupations': [], 'titles': [], 'address': [], 'others': []},
           'pid': 100, 'pageNames': 'abc-001_1234_123_0100.txt', 'pageNo': 100,
           'sentenceNo': 30,
           'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                         '920,2014,101,24:main'],
           'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001.json", "abc-001_1234_123_0100.json"]),
      []),
     # same other and non-conflicting names are matched
     ((("abc", "1234"), [{'info': {
         'lastnames': [], 'firstnames': [], 'abbr_firstnames': [],
         'occupations': [], 'titles': [], 'address': [], 'others': ["Beta"]},
         'pid': 1, 'pageNames': 'abc-001_1234_123_0001.txt', 'pageNo': 1,
         'sentenceNo': 29, 'positions': ['865,1781,49,22:main',
                                         '924,1780,100,23:main'],
         'type': 'PER', 'articles': []},
       {'info': {
           'lastnames': [], 'firstnames': [], 'abbr_firstnames': [],
           'occupations': [], 'titles': [], 'address': [], 'others': ["Beta"]},
           'pid': 100, 'pageNames': 'abc-001_1234_123_0100.txt', 'pageNo': 100,
           'sentenceNo': 30,
           'positions': ['789,2016,48,22:main', '847,2013,65,30:main',
                         '920,2014,101,24:main'],
           'type': 'PER', 'articles': []}
       ], ["abc-001_1234_123_0001.json", "abc-001_1234_123_0100.json"]),
      [{'lastname': '', 'firstname': [], 'abbr_firstname': [], 'address': [],
        'titles': [], 'profession': [], 'other': ['Beta'],
        'references': {
            'abc-001_1234_123_0001.txt': {
              'pid': 1, 'refs': [
                  {'sent': 29,
                   'coords': ['865,1781,49,22:main', '924,1780,100,23:main']}],
              'elements': []},
            'abc-001_1234_123_0100.txt': {
              'pid': 100, 'refs': [
                  {'sent': 30,
                   'coords': ['789,2016,48,22:main', '847,2013,65,30:main',
                              '920,2014,101,24:main']}],
              'elements': []}},
        'type': 'PER', 'id': 0}]),
]
PARAMS_aggregate_place = [
    (
     {"name": "Zürich",
      "tokens": ["ZÜRICH"],
      "type": "LOC",
      "references": {
              (4, "abc", 2): [(5, "123", "123")]  # (pageNo, pageNames, pid)
          }
      },
     {"name": "Zürich",
      "tokens": ["ZÜRICH"],
      "type": "LOC",
      "pageNo": 4,
      "pageNames": "abc",
      "pid": 2,
      "sentenceNo": 6,
      "positions": "456",
      "articles": "456"
      },
     {"name": "Zürich",
      "tokens": ["ZÜRICH"],
      "type": "LOC",
      "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
      }
    ),
    (
     {"name": "Zürich",
      "tokens": ["ZÜRICH"],
      "type": "LOC",
      "references": {
              (4, "abc", 2): [(5, "123", "123")]  # (pageNo, pageNames, pid)
          }
      },
     {"name": "Zürich",
      "tokens": ["ZÜRICH"],
      "type": "LOC",
      "pageNo": 7,
      "pageNames": "efg",
      "pid": 8,
      "sentenceNo": 6,
      "positions": "456",
      "articles": "456"
      },
     {"name": "Zürich",
      "tokens": ["ZÜRICH"],
      "type": "LOC",
      "references": {
              (4, "abc", 2): [(5, "123", "123")],
              (7, "efg", 8): [(6, "456", "456")]
          }
      }
    )
]
PARAMS_aggregate_places = [
    (
     [{"tokens": ["ZÜRICH"],
       "type": "LOC",
       "pageNo": 7,
       "pageNames": "efg",
       "pid": 8,
       "sentenceNo": 6,
       "positions": "456",
       "articles": "456"
       },
      {"tokens": ["BASEL"],
       "type": "LOC",
       "pageNo": 4,
       "pageNames": "abc",
       "pid": 5,
       "sentenceNo": 7,
       "positions": "123",
       "articles": "123"}],
     [{"tokens": ["ZÜRICH"],
       "type": "LOC",
       "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
       }],
     [{
      'articles': '456',
      'pageNames': 'efg',
      'pageNo': 7,
      'pid': 8,
      'positions': '456',
      'sentenceNo': 6,
      'tokens': ['ZÜRICH'],
      'type': 'LOC',
      },
      {
      'articles': '123',
      'pageNames': 'abc',
      'pageNo': 4,
      'pid': 5,
      'positions': '123',
      'sentenceNo': 7,
      'tokens': ['BASEL'],
      'type': 'LOC',
      }],
     [{
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')],
          (7, 'efg', 8): [(6, '456', '456')],
       },
      'tokens': ['ZÜRICH'],
      'type': 'LOC',
      },
      {'name': "Basel",
       'references': {
         (4, 'abc', 5): [(7, '123', '123')],
        },
       'tokens': ['BASEL'],
       'type': 'LOC',
       }]
    ),
]
PARAMS_map_genitive_places = [
    (["zürich", "basel"],
     [{
      "tokens": ["ZÜRICHS"],
      "type": "LOC",
      "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
      },
      {
       "tokens": ["BASELS"],
       "type": "LOC",
       "references": {
               (7, "mnl", 8): [(10, "159", "159"), (11, "753", "753")]
           }
       }],
     [{
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')],
        },
      'tokens': ['ZÜRICH'],
      'type': 'LOC',
      },
      {
      'references': {
          (7, 'mnl', 8): [(10, '159', '159'), (11, '753', '753')],
        },
      'tokens': ['BASEL'],
      'type': 'LOC',
      }]),
    (["zürich", "basel"],
     [{
      "tokens": ["URIS"],
      "type": "LOC",
      "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
      }],
     [{
      "tokens": ["URIS"],
      "type": "LOC",
      "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
      }])
]
PARAMS_clean_up_aggregation_places = [
    (
    [{"name": "zurich", "references": {}},
     {"name": "basel", "references": {}}], 0,
    [{'name': 'basel', 'references': {}, 'id': 1},
     {'name': 'zurich', 'references': {}, 'id': 2}]
   ), (
    [{"name": "zurich", "references":
        {
          "ab1":
          [(0, "123", ["elem1", "elem2"]),
           (1, "456", ["elem1", "elem2"])]
        }
      },
     {"name": "zurich", "references":
        {
          "cd2":
          [(3, "789", ["elem1", "elem2"]), (4, "000", ["elem1", "elem2"])]
        }
      }], 5,
    [{'name': 'zurich', 'references':
      {
          'b':
          {
              'pid': '1', 'refs':
              [
                  {
                      'sent': 0, 'coords': '123'
                  }, {
                      'sent': 1, 'coords': '456'
                  }
              ],
              'elements':
              [
                  'elem1', 'elem2'
              ]
          }
      },
      'id': 6},
     {'name': 'zurich', 'references':
      {
          'd':
          {
              'pid': '2', 'refs':
              [
                  {
                      'sent': 3, 'coords': '789'
                  }, {
                      'sent': 4, 'coords': '000'
                  }
               ],
              'elements':
              [
                  'elem1', 'elem2'
              ]
           }
       },
      'id': 7}]
   ),
]
PARAMS_find_place_match = [
    ("zürich", "LOC",
     [{"tokens": ["ZÜRICH"],
       "type": "LOC",
       "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
       }],
     {
      'references': {
          (4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')],
      },
      'tokens': ['ZÜRICH'],
      'type': 'LOC',
      }),
    ("basel", "LOC",
     [{"tokens": ["ZÜRICH"],
       "type": "LOC",
       "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
       }],
     False)
]
PARAMS_clean_up_aggregation = [
    ([{"firstname": {("Anna", "Maria"), ()},
      "lastname": "Müller",
      "abbr_firstname": {()},
      "titles": {("Dr.", "Frau")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", "2"): [(5, "123", [{"123":{}}]), (6, "456", [{"456":{}}])]
           }
      },
    {"firstname": {("Kat", "Man")},
      "lastname": "Bil",
      "abbr_firstname": "",
      "titles": {("Prof.", "Herr"), ()},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", "2"): [(5, "123", [{"123":{}}]), (6, "456", [{"456":{}}])]
           }
     }],
    [{'abbr_firstname': [], 'address': ['a', 'b'],
      'firstname': ['Kat Man'], 'id': 0, 'lastname': 'Bil',
      'other': ['e'], 'profession': ['c', 'd'],
      'references': {
          'abc': {
              'elements': ['1', '2', '3', '4', '5', '6'],
              'pid': 2,
              'refs': [{'coords': '123', 'sent': 5},
                       {'coords': '456', 'sent': 6}]}},
      'titles': ['Herr Prof.']
      },
     {'abbr_firstname': [], 'address': ['a', 'b'],
      'firstname': ['Anna Maria'], 'id': 1, 'lastname': 'Müller',
      'other': ['e'], 'profession': ['c', 'd'],
      'references': {
        'abc': {
          'elements': ['1', '2', '3', '4', '5', '6'],
          'pid': 2,
          'refs': [{'coords': '123', 'sent': 5}, {'coords': '456', 'sent': 6}]
        }},
      'titles': ['Frau Dr.']
      }
     ])
]
PARAMS_others_match = [({"info": {"lastnames": "z", "firstnames": "x",
              "abbr_firstnames": "y",
              "titles": "", "address": "", "occupations": "",
              "others": "e"},
     "pageNo": 4, "sentenceNo": 5, "pageNames": "", "pid": "",
     "positions": "", "articles": "", 'type': 'PER'},
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": set(),
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": set(()),
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
    [{'abbr_firstname': set(),
      'address': {('a', 'b')},
      'firstname': {('Anna', 'Maria')},
      'lastname': 'Müller',
      'other': {'e'},
      'profession': {('c', 'd')},
      'references': {(4, 'abc', 2): [(5, '123', '123'), (6, '456', '456')]},
      'titles': {('Frau', 'Dr.')}}])
]
PARAMS_only_abbrev_firstname_match = [({"info": {"lastnames": "z", "firstnames": "x",
              "abbr_firstnames": "A",
              "titles": "", "address": "", "occupations": "",
              "others": "e"},
     "pageNo": 4, "sentenceNo": 5, "pageNames": "", "pid": "",
     "positions": "", "articles": "", 'type': 'PER'
     },
    [{'firstname': {('Anna', 'Maria')},
      "lastname": "Müller",
      "abbr_firstname": {("A")},
      "titles": {("Frau", "Dr.")},
      "address": {("a", "b")},
      "profession": {("c", "d")},
      "other": {("e")},
      "references": {
               (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
           }
      },
    {"firstname": {("Kat", "Man")},
     "lastname": "Bil",
     "abbr_firstname": set(),
     "titles": {("Herr", "Prof")},
     "address": {("a", "b")},
     "profession": {("c", "d")},
     "other": {},
     "references": {
              (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
          }
     }],
      [{'firstname': {('Anna', 'Maria')},
        "lastname": "Müller",
        "abbr_firstname": {("A")},
        "titles": {("Frau", "Dr.")},
        "address": {("a", "b")},
        "profession": {("c", "d")},
        "other": {("e")},
        "references": {
                 (4, "abc", 2): [(5, "123", "123"), (6, "456", "456")]
             }
        }]
    )
]
PARAMS_compare_linking_person = [([{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": "",
        "titles": "",
        "profession": "",
        "other": [],
        "id": "",
        "references": {},
        "gnd_ids": []}],
      [{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": "",
        "titles": "",
        "profession": "",
        "other": [],
        "id": "",
        "references": {},
        "gnd_ids": []}]),
     ([{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": ["frau", "dr."],
        "titles": "",
        "profession": "",
        "other": [],
        "id": "",
        "references": {},
        "gnd_ids": []}],
      [{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": ["dr.", "frau"],  # address can be reordered
        "titles": "",
        "profession": "",
        "other": [],
        "id": "",
        "references": {},
        "gnd_ids": []}]),
     ([{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": "",
        "titles": ["dr.", "prof."],
        "profession": "",
        "other": [],
        "id": "",
        "references": {},
        "gnd_ids": []}],
      [{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": "",
        "titles": ["prof.", "dr."],  # titles can be reordered
        "profession": "",
        "other": [],
        "id": "",
        "references": {},
        "gnd_ids": []}]),
     ([{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": "",
        "titles": "",
        "profession": ["a", "b"],
        "other": [],
        "id": "",
        "references": {},
        "gnd_ids": []}],
      [{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": "",
        "titles": "",
        "profession": ["b", "a"],  # professions can be reordered
        "other": [],
        "id": "",
        "references": {},
        "gnd_ids": []}]),
     ([{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": "",
        "titles": "",
        "profession": "",
        "other": [["a"], ["b"]],
        "id": "",
        "references": {},
        "gnd_ids": []}],
      [{"type": "PER",
        "lastname": "",
        "firstname": "",
        "abbr_firstname": "",
        "address": "",
        "titles": "",
        "profession": "",
        "other": [["b"], ["a"]],  # can be reordered wrt the flattened list
        "id": "",
        "references": {},
        "gnd_ids": []}]),
     ([{"type": "GPE"}],
      [{"type": "GPE"}])
     # if type is not per it just returns true bc this compares people
]

gt_dict_with_gnd = {
    'lastname': 'z',
    'firstname': ['x y'],
    'abbr_firstname': [],
    'address': ["Frau"],
    'titles': [],
    'profession': [],
    'other': [],
    'references': {
        'aaa-001_2004_000_0012.txt': {
            'refs': [{'sent': 0, 'coords': ['a']}]}},
    'type': 'PER',
    'id': 0,
    'gt_gnd_id': 'a'}
gt_dict_without_gnd = {
    'lastname': 'z',
    'firstname': ['x y'],
    'abbr_firstname': [],
    'address': ["Frau"],
    'titles': [],
    'profession': [],
    'other': [],
    'references': {
        'aaa-001_2004_000_0012.txt': {
            'refs': [{'sent': 0, 'coords': ['a']}]}},
    'type': 'PER',
    'id': 0,
    'gt_gnd_id': ''}
entity_dict_without_gnd = {
    'lastname': 'z',
    'firstname': ['x y'],
    'abbr_firstname': [],
    'address': ["Frau"],
    'titles': [],
    'profession': [],
    'other': [],
    'references': {
        'aaa-001_2004_000_0012.txt': {
            'refs': [{'sent': 0, 'coords': ['a']}]}},
    'type': 'PER',
    'id': 0,
    'gnd_ids': []}
entity_dict_with_gnd = {
    'lastname': 'z',
    'firstname': ['x y'],
    'abbr_firstname': [],
    'address': ["Frau"],
    'titles': [],
    'profession': [],
    'other': [],
    'references': {
        'aaa-001_2004_000_0012.txt': {
            'refs': [{'sent': 0, 'coords': ['a']}]}},
    'type': 'PER',
    'id': 0,
    'gnd_ids': ["a", "b"]}
conf = {
    "PATH_TO_INPUT_FOLDERS": "./data/input/",
    "PATH_TO_NER_MODEL_1": "./models/ner-bio.pt",
    "PATH_TO_NER_MODEL_2": "./models/ner-det.pt",
    "PATH_TO_OUTFILE_FOLDER": "./data/output/",
    "PATH_TO_ABBREVIATION_FILE": "./src/preprocessing/abbrevs.txt",
    "PATH_TO_GROUND_TRUTH": "./data/ground_truth_linked/with_fuzzy_matching/"
    # which path to use as GT is set via command line option and based on the
    # config
    # "--fuzzy True" for instance sets
    # PATH_TO_GROUND_TRUTH = PATH_TO_GROUND_TRUTH_FUZZY
    # here i am skipping that part and simulating setting the GT path in main
}

PARAMS_clean_raw = [
     ([entity_dict_with_gnd,
       {"firstname": ["a b"],
        "lastname": "c",
        "abbr_firstname": [],
        "address": ["Frau"],
        "titles": [],
        "profession": [],
        "other": [],
        "references": {
            # old ref style
            "aaa-001_2004_000_0013.txt": [{"sent": "a", "coords": ["b:main"]}]
        },
        "type": "PER",
        "id": 1,
        "gnd_ids": ["y", "x"]}],
      10,
      False,
      [[{'lastname': 'z',
         'firstname': 'x y',
         'abbr_firstname': [],
         'other': [],
         'name': 'x y z',
         'profession': [],
         'places': [],
         'gnd_candidates': ["a", "b"],
         'page': 'aaa-001_2004_000_0012.txt',
         'year': '2004',
         'coord': 'a'}],
      [{'lastname': 'c',
        'firstname': 'a b',
        'abbr_firstname': [],
        'other': [],
        'name': 'a b c',
        'profession': [],
        'places': [],
        'gnd_candidates': ["y", "x"],
        'page': 'aaa-001_2004_000_0013.txt',
        'year': '2004',
        'coord': 'b'}]]),
     ([gt_dict_without_gnd,
       {"firstname": ["a b"],
        "lastname": "c",
        "abbr_firstname": [],
        "address": ["Frau"],
        "titles": [], "profession": [],
        "other": [],
        "references": {
            "aaa-001_2004_000_0013.txt": {
                "refs": [{"sent": "a", "coords": "b"}]}},
        "type": "PER",
        "id": 1}],
      10,
      True,
      [[{'lastname': 'z',
         'firstname': 'x y',
         'abbr_firstname': [],
         'other': [],
         'name': 'x y z',
         'profession': [],
         'places': [],
         'gt_gnd_id': "",
         'page': 'aaa-001_2004_000_0012.txt',
         'year': '2004',
         'coord': 'a'}],
      [{'lastname': 'c',
        'firstname': 'a b',
        'abbr_firstname': [],
        'other': [],
        'name': 'a b c',
        'profession': [],
        'places': [],
        'gt_gnd_id': [],
        'page': 'aaa-001_2004_000_0013.txt',
        'year': '2004',
        'coord': 'b'}]])
]

linked_dict_without_gnd = {
    'lastname': 'z',
    'firstname': ['x y'],
    'abbr_firstname': [],
    'address': ["Frau"],
    'titles': [],
    'profession': [],
    'other': [],
    'references': {
        'aaa-001_2004_000_0012.txt': {
            'refs': [{'sent': 0, 'coords': ['a']}]}
    },
    'type': 'PER',
    'id': 0,
    'gnd_ids': []
}
gt_dict_with_multiple_refs = {
    'lastname': 'z',
    'firstname': ['x y'],
    'abbr_firstname': [],
    'address': ["Frau"],
    'titles': [],
    'profession': [],
    'other': [],
    'references': {
        'aaa-001_2004_000_0012.txt': {
            'refs': [
                {'sent': 0, 'coords': ['a']}, {'sent': 1, 'coords': ['b']}
            ]
        }
    },
    'type': 'PER',
    'id': 0,
    'gt_gnd_id': 'a'
}
linked_dict_with_partial_refs = {
    'lastname': 'z',
    'firstname': ['x y'],
    'abbr_firstname': [],
    'address': ["Frau"],
    'titles': [],
    'profession': [],
    'other': [],
    'references': {
        'aaa-001_2004_000_0012.txt': {
            'refs': [{'sent': 0, 'coords': ['a']}]}
    },
    'type': 'PER',
    'id': 0,
    'gnd_ids': ["a"]
}
linked_dict_with_extra_refs = {
    'lastname': 'z',
    'firstname': ['x y'],
    'abbr_firstname': [],
    'address': ["Frau"],
    'titles': [],
    'profession': [],
    'other': [],
    'references': {
        'aaa-001_2004_000_0012.txt': {
            'refs': [
                {'sent': 0, 'coords': ['a']}, {'sent': 2, 'coords': ['c']}
            ]
        }
    },
    'type': 'PER',
    'id': 0,
    'gnd_ids': ['a']
}
PARAMS_evaluate_person = [
     ([gt_dict_with_gnd],
      [entity_dict_with_gnd],
      True,
      3,
      False,
      {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}),
     ([gt_dict_with_gnd],
      [entity_dict_with_gnd],
      True,
      3,
      True,
      {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}),
     ([gt_dict_without_gnd],
      [entity_dict_with_gnd],
      True,
      3,
      False,
      {'tp': 0, 'fp': 1, 'fn': 0, 'tn': 0}),
     ([gt_dict_without_gnd],
      [entity_dict_with_gnd],
      True,
      3,
      True,
      {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}),
     ([gt_dict_with_gnd],
      [entity_dict_without_gnd],
      True,
      3,
      False,
      {'tp': 0, 'fp': 0, 'fn': 1, 'tn': 0}),
     ([gt_dict_with_gnd],
      [entity_dict_without_gnd],
      True,
      3,
      True,
      {'tp': 0, 'fp': 0, 'fn': 1, 'tn': 0}),
     ([gt_dict_without_gnd],
      [entity_dict_without_gnd],
      True,
      3,
      False,
      {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 1}),
     ([gt_dict_without_gnd],
      [entity_dict_without_gnd],
      True,
      3,
      True,
      {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}),
     # Ground truth has multiple references, linked has partial matches
     # This case covers differences in aggregation for instance
     ([gt_dict_with_multiple_refs],
      [linked_dict_with_partial_refs],
      True,
      3,
      False,
      {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}),
     ([gt_dict_with_multiple_refs],
      [linked_dict_with_partial_refs],
      True,
      3,
      True,
      {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}),
     # Ground truth has multiple references, linked has extra references
     ([gt_dict_with_multiple_refs],
      [linked_dict_with_extra_refs],
      True,
      3,
      False,
      {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}),
     ([gt_dict_with_multiple_refs],
      [linked_dict_with_extra_refs],
      True,
      3,
      True,
      {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}),
     # Ground truth and linked entity match with GND ID
     ([gt_dict_with_gnd],
      [linked_dict_with_partial_refs],
      False,
      3,
      False,
      {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}),
     ([gt_dict_with_gnd],
      [linked_dict_with_partial_refs],
      False,
      3,
      True,
      {'tp': 1, 'fp': 0, 'fn': 0, 'tn': 0}),
     # Ground truth has no GND ID, but linked entity has GND ID
     ([gt_dict_without_gnd],
      [linked_dict_with_partial_refs],
      False,
      3,
      False,
      {'tp': 0, 'fp': 1, 'fn': 0, 'tn': 0}),
     ([gt_dict_without_gnd],
      [linked_dict_with_partial_refs],
      False,
      3,
      True,
      {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}),
     # Ground truth has GND ID, but linked entity has no GND ID
     ([gt_dict_with_gnd],
      [linked_dict_without_gnd],
      False,
      3,
      False,
      {'tp': 0, 'fp': 0, 'fn': 1, 'tn': 0}),
     ([gt_dict_with_gnd],
      [linked_dict_without_gnd],
      False,
      3,
      True,
      {'tp': 0, 'fp': 0, 'fn': 1, 'tn': 0}),
     # Neither ground truth nor linked entity has GND ID
     ([gt_dict_without_gnd],
      [linked_dict_without_gnd],
      False,
      3,
      False,
      {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 1}),
     ([gt_dict_without_gnd],
      [linked_dict_without_gnd],
      False,
      3,
      True,
      {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0})
]
PARAMS_get_main_name = [({"firstname": "x y",
       "lastname": "z",
       "abbr_firstname": [],
       "other": []},
      'x y z'),
     ({"firstname": "x y",
       "lastname": "z",
       "abbr_firstname": ["b"],
       "other": []},
      'x y z'),
     ({"firstname": "",
       "lastname": "z",
       "abbr_firstname": ["b"],
       "other": []},
      'b z'),
     ({"firstname": "x y",
       "lastname": "",
       "abbr_firstname": ["b"],
       "other": []},
      'x y b'),
     ({"firstname": "",
       "lastname": "",
       "abbr_firstname": ["b"],
       "other": []},
      'b'),
     ({"firstname": "",
       "lastname": "",
       "abbr_firstname": [],
       "other": ["d"]},
      'd'),
     ({"firstname": "",
       "lastname": "",
       "abbr_firstname": [],
       "other": []},
      "--"),
     ({}, "--"),
]

PARAMS_fuse_hyphens = [
        (
            """Wort¬ 111
teile 222
Maschi- 333
nen 444
""",
            [
                {"word": "Wortteile", "coord": ["111", "222"]},
                {"word": "Maschinen", "coord": ["333", "444"]},
            ],
        ),
        (
            """Fish- 100
Bus 101
End- 202
Case 203
""",
            [
                {"word": "Fish-Bus", "coord": ["100", "101"]},
                {"word": "End-Case", "coord": ["202", "203"]},
            ],
        ),
        (
            """Hello 111
World 222
NoSplit 333
""",
            [
                {"word": "Hello", "coord": ["111"]},
                {"word": "World", "coord": ["222"]},
                {"word": "NoSplit", "coord": ["333"]},
            ],
        ),
]
PARAMS_check_for_abbrev = [
        (
            1,
            [("Dr.", "coord1"), ("John", "coord2"), ("Smith", "coord3")],
            False,
        ),
        (
            2,
            [("Dr.", "coord1"), ("John", "coord2"), ("Smith", "coord3")],
            False,
        ),
        (
            0,
            [("Prof.", "coord1"), ("Jane", "coord2"), ("Doe", "coord3")],
            True,
        ),
        (
            1,
            [("Prof.", "coord1"), ("Jane", "coord2"), ("Doe", "coord3")],
            False,
        ),
        (
            1,
            [("vgl.", "coord1"), ("u.a.", "coord2"), ("etc.", "coord3")],
            False,
        ),
        (
            0,
            [("vgl.", "coord1"), ("u.a.", "coord2"), ("etc.", "coord3")],
            True,
        ),
        (
            2,
            [("vgl.", "coord1"), ("u.a.", "coord2"), ("etc.", "coord3")],
            True,
        ),
]
PARAMS_tokenize = [
        (
            [
                {"word": "Hello", "coord": "1209745"},
                {"word": "v.a.", "coord": "1908234"},
            ],
            [
                {
                    "token": "Hello",
                    "coord": "1;2;0;9;7;4;5:main",
                },
                {"token": "v.", "coord": "1;9;0;8;2;3;4:main"},
                {"token": "a.", "coord": "1;9;0;8;2;3;4:main"},
            ],
        ),
        (
            [
                {"word": "HANS", "coord": "1234567"},
                {"word": "WORLD.", "coord": "7654321"},
            ],
            [
                {
                    "token": "HANS",
                    "coord": "1;2;3;4;5;6;7:main",
                    "normalized": "Hans"
                },
                {
                    "token": "WORLD",
                    "coord": "7;6;5;4;3;2;1:main",
                    "normalized": "World",
                },
                {"token": ".", "coord": "7;6;5;4;3;2;1:rpunc"},
            ],
        ),
        (
            [
                {"word": "Prof.", "coord": "1111111"},
                {"word": "Jane", "coord": "2222222"},
                {"word": "Doe", "coord": "3333333"},
            ],
            [
                {"token": "Prof.", "coord": "1;1;1;1;1;1;1:main"},
                {"token": "Jane", "coord": "2;2;2;2;2;2;2:main"},
                {"token": "Doe", "coord": "3;3;3;3;3;3;3:main"},
            ],
        ),
        (
            [
                {"word": "vgl.", "coord": "4444444"},
                {"word": "u.a.", "coord": "5555555"},
                {"word": "etc.", "coord": "6666666"},
            ],
            [
                {"token": "vgl.", "coord": "4;4;4;4;4;4;4:main"},
                {"token": "u.", "coord": "5;5;5;5;5;5;5:main"},
                {"token": "a.", "coord": "5;5;5;5;5;5;5:main"},
                {"token": "etc.", "coord": "6;6;6;6;6;6;6:main"},
            ],
        ),
        (
            [
                {"word": "xvii.", "coord": "7777777"},
                {"word": "abc.", "coord": "8888888"},
            ],
            [
                {"token": "xvii.", "coord": "7;7;7;7;7;7;7:main"},
                {"token": "abc", "coord": "8;8;8;8;8;8;8:main"},
                {"token": ".", "coord": "8;8;8;8;8;8;8:rpunc"},
            ],
        ),
]
PARAMS_split_sentences = [
        (
            [
                {"token": "Hello", "coord": "1;2;0;9;7;4;5:main"},
                {"token": ".", "coord": "1;2;0;9;7;4;5:rpunc"},
                {"token": "World", "coord": "1;2;0;9;7;4;6:main"},
                {"token": "!", "coord": "1;2;0;9;7;4;6:rpunc"},
            ],
            [
                [
                    {"token": "Hello", "coord": "1;2;0;9;7;4;5:main"},
                    {"token": ".", "coord": "1;2;0;9;7;4;5:rpunc"},
                ],
                [
                    {"token": "World", "coord": "1;2;0;9;7;4;6:main"},
                    {"token": "!", "coord": "1;2;0;9;7;4;6:rpunc"},
                ],
            ],
        ),
        (
            [
                {"token": "This", "coord": "1;2;0;9;7;4;5:main"},
                {"token": "is", "coord": "1;2;0;9;7;4;6:main"},
                {"token": "a", "coord": "1;2;0;9;7;4;7:main"},
                {"token": "test", "coord": "1;2;0;9;7;4;8:main"},
                {"token": ".", "coord": "1;2;0;9;7;4;8:rpunc"},
            ],
            [
                [
                    {"token": "This", "coord": "1;2;0;9;7;4;5:main"},
                    {"token": "is", "coord": "1;2;0;9;7;4;6:main"},
                    {"token": "a", "coord": "1;2;0;9;7;4;7:main"},
                    {"token": "test", "coord": "1;2;0;9;7;4;8:main"},
                    {"token": ".", "coord": "1;2;0;9;7;4;8:rpunc"},
                ],
            ],
        ),
        (
            [
                {"token": "Sentence", "coord": "1;2;0;9;7;4;5:main"},
                {"token": "one", "coord": "1;2;0;9;7;4;6:main"},
                {"token": ".", "coord": "1;2;0;9;7;4;6:rpunc"},
                {"token": "Sentence", "coord": "1;2;0;9;7;4;7:main"},
                {"token": "two", "coord": "1;2;0;9;7;4;8:main"},
                {"token": "!", "coord": "1;2;0;9;7;4;8:rpunc"},
            ],
            [
                [
                    {"token": "Sentence", "coord": "1;2;0;9;7;4;5:main"},
                    {"token": "one", "coord": "1;2;0;9;7;4;6:main"},
                    {"token": ".", "coord": "1;2;0;9;7;4;6:rpunc"},
                ],
                [
                    {"token": "Sentence", "coord": "1;2;0;9;7;4;7:main"},
                    {"token": "two", "coord": "1;2;0;9;7;4;8:main"},
                    {"token": "!", "coord": "1;2;0;9;7;4;8:rpunc"},
                ],
            ],
        ),
        (
            [
                {"token": "No", "coord": "1;2;0;9;7;4;5:main"},
                {"token": "punctuation", "coord": "1;2;0;9;7;4;6:main"},
            ],
            [
                [
                    {"token": "No", "coord": "1;2;0;9;7;4;5:main"},
                    {"token": "punctuation", "coord": "1;2;0;9;7;4;6:main"},
                ],
            ],
        ),
]
PARAMS_prep_year_data_for_tagging = [
        (("abc-1234",
         ["abc-1234/1234_0001.txt",
          "abc-1234/1234_0002.txt",
          "abc-1234/1234_0003.txt"]),
         ({'1234_0001.txt':
           [
                [
                    {'coord': '12345:main', 'token': 'This'},
                    {'coord': '67891:main', 'token': 'is'},
                    {'coord': '12345:main', 'token': 'a'},
                    {'coord': '67891:main', 'token': 'test'},
                    {'coord': '67891:main', 'token': 'sentence'},
                    {'coord': '67891:rpunc', 'token': '.'}
                ],
                [
                    {'coord': '12345:main', 'token': 'Another'},
                    {'coord': '67891:main', 'token': 'line'},
                    {'coord': '67891;67891:main', 'token': 'withhyphen'},
                    {'coord': '67891;67891:rpunc', 'token': '.'}
                ]
            ],
           '1234_0002.txt':
           [
                [
                    {'coord': '12345:main', 'token': 'This'},
                    {'coord': '67891:main', 'token': 'is'},
                    {'coord': '12345:main', 'token': 'a'},
                    {'coord': '67891:main', 'token': 'test'},
                    {'coord': '67891:main', 'token': 'sentence'},
                    {'coord': '67891:rpunc', 'token': '.'}
                ],
                [
                    {'coord': '12345:main', 'token': 'Another'},
                    {'coord': '67891:main', 'token': 'line'},
                    {'coord': '67891;67891:main', 'token': 'withhyphen'},
                    {'coord': '67891;67891:rpunc', 'token': '.'}]
                    ],
           '1234_0003.txt':
           [
                [
                    {'coord': '12345:main', 'token': 'This'},
                    {'coord': '67891:main', 'token': 'is'},
                    {'coord': '12345:main', 'token': 'a'},
                    {'coord': '67891:main', 'token': 'test'},
                    {'coord': '67891:main', 'token': 'sentence'},
                    {'coord': '67891:rpunc', 'token': '.'}
                ],
                [
                    {'coord': '12345:main', 'token': 'Another'},
                    {'coord': '67891:main', 'token': 'line'},
                    {'coord': '67891;67891:main', 'token': 'withhyphen'},
                    {'coord': '67891;67891:rpunc', 'token': '.'}
                ]
               ]
           }, 'abc-1234'))
]

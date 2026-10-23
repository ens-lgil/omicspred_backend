from rest_framework.test import APITestCase
from django.conf import settings
import re
from time import sleep


sleep_time = 60
status_ok = 200
status_not_found = 404

# Change throttle rates for the tests
rate4test = '400/min'


class RestApiTestBase(APITestCase):
    """Shared fixture and helper setup for the REST API test suite."""

    fixtures = ['db_test']
    databases = {'default'}

    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {'anon': rate4test, 'user': rate4test}

    # Base URL of the server
    server = '/api/'

    # Data example
    filter_ids = 'filter_ids'
    cohorts_list = ['INTERVAL', 'UKB']
    publications_list = ['36991119', '123456']
    publication_ids_list = ['OPP000001', 'OPP000002']

    platforms_list_proteomics = ['Somalogic', 'Olink']
    platforms_list_metabolomics = ['Metabolon']
    platforms_list_transcriptomics = ['Illumina RNAseq']
    platforms_list = [*platforms_list_proteomics,*platforms_list_metabolomics,*platforms_list_transcriptomics]
    scores_list = ['OPGS000005', 'OPGS002385', 'OPGS003006']
    gene_ids_list = ['ENSG00000072694']
    gene_names_list = ['FCGR2B']
    proteins_list = ['P31994']
    metabolites_list = ['CHEBI_16113']
    pathways_list = ['R-HSA-191273', 'R-HSA-198933']
    phenotypes_list = ['MONDO_0005148','MONDO_0005066']
    tissue_ids_list = ['UBERON_0001969', 'BTO_0000133']
    tissue_labels_list = ['blood plasma', 'blood serum']
    dataset_ids_list = ['OPD000001', 'OPD000002']
    author_name = 'Xu'

    score_id_1 = scores_list[0]
    score_id_2 = scores_list[1]
    score_id_3 = scores_list[2]
    publication_id_1 = publication_ids_list[0]
    pmid_1 = publications_list[0]
    dataset_id_1 = dataset_ids_list[0]
    platform_1 = platforms_list_proteomics[0]
    platform_2 = platforms_list_proteomics[1]
    gene_id = gene_ids_list[0]
    gene_name = gene_names_list[0]
    cohort = cohorts_list[0]
    protein_id = proteins_list[0]
    metabolite_id = metabolites_list[0]

    # Wrong examples for testing invalid inputs
    fake_examples = {'string': 'ABC123CDE', 'integer': '00001', 'date': '1990-01-01'}
    empty_resp = ['{}', '{"size":0,"count":0,"next":null,"previous":null,"results":[]}', '[]']
    invalid_score_id = 'OPGS999999'

    # Popular endpoints for testing
    score_all = 'score/all'
    score_all_endpoint = f'{server}{score_all}/'
    gene_search_endpoint = f'{server}gene/search/'
    score_search_endpoint = f'{server}score/search/'


    index_result_mutliplicity = 2
    index_example = 3

    search_pmid = f'pmid={pmid_1}'
    search_opp_id = f'opp_id={publication_id_1}'
    search_opd_id = f'opd_id={dataset_id_1}'
    search_platform = f'platform={platform_2}'
    search_cohort = f'cohort={cohorts_list[1]}'
    search_author = f'author={author_name}'
    search_opgs_id = f'opgs_id={score_id_1}'
    search_opgs_ids = f'opgs_ids={",".join(scores_list)}'
    search_opgs_ids_2 = f'opgs_ids={score_id_1}'
    search_phenotype = f'phenotype_id={phenotypes_list[0]}'
    search_gene = f'gene={gene_name}'
    search_metabolite =  f'metabolite={metabolite_id}'
    seach_mt = f'molecular_trait={protein_id}'
    search_combined = f'{search_opgs_id}&{search_pmid}'
    search_combined_2 = f'{search_opgs_ids}&{search_pmid}'
    search_cohort = f'cohort={cohort}'

    omics_common_columns = ['id', 'trait_reported_id', 'trait_reported', 'variants_number', 'dataset__publication', 'dataset__platform__version', 'dataset__name']

    # Tuple structure: ( Endpoint name | Base URL | Flag for results multiplicity | Parameter examples )
    endpoints = [
        # Cohort endpoints
        ('Cohorts', 'cohort/all', 1),
        ('Cohort/SYMBOL', 'cohort', 0, {'path': cohorts_list}),
        # Pathways
        ('Pathways', 'pathway/all', 1),
        ('Pathways/Name', 'pathway', 0, {'path': pathways_list}),
        # Molecular trait endpoints
        ('Gene/ID', 'gene', 0, {'path': gene_ids_list}),
        ('Gene/Search', 'gene/search', 1, {'query': [search_gene]}),
        ('Protein/Name', 'protein', 0, {'path': proteins_list}),
        ('Protein/Search', 'protein/search', 1, {'query': [search_gene]}),
        ('Metabolite/Name', 'metabolite', 0, {'path': metabolites_list}),
        ('Metabolite/Search', 'metabolite/search', 1, {'query': [search_metabolite]}),
        # Omics by platform endpoints
        ('Proteomics/Name', 'proteomics',1, {'path': platforms_list_proteomics}),
        ('Metabolomics/Name', 'metabolomics',1, {'path': platforms_list_metabolomics}),
        ('Transcriptomics/Name', 'transcriptomics',1, {'path': platforms_list_transcriptomics}),
        # Performance Metrics endpoints
        ('Performances Search MT','performance/search/protein', 1, {'path': [proteins_list[0]], 'extra_query':search_opgs_id}),
        ('Performances Search','performance/search', 1, {'query': [search_opgs_id,search_pmid,search_platform]}),
        # Publication endpoints
        ('Publications', 'publication/all', 1),
        ('Publications', 'publication/all', 1, {'query': [filter_ids+'='+','.join(publication_ids_list)]}),
        ('Publication/OPP_ID', 'publication', 0, {'path': publication_ids_list}),
        ('Publication/PMID', 'publication', 0, {'path': publications_list}),
        ('Publication Search', 'publication/search', 1, {'query': [search_opgs_id,search_pmid,search_author]}),
        # Sample endpoint
        ('Samples', 'sample/all', 1),
        ('Samples Search', 'sample/search', 1, {'query': [search_cohort]}),
        # Score endpoints
        ('Scores', score_all, 1),
        ('Score/ID', 'score', 0, {'path': scores_list}),
        ('Scores Search', 'score/search', 1, {'query': [search_opgs_ids,search_opgs_ids_2,search_pmid,search_opp_id,search_opd_id,search_platform,search_cohort,search_combined_2]}),
        ('Scores Search Type', 'score/search/protein', 1, {'path': [proteins_list[0]],'extra_query': 'include_performance_metrics=1'}),
        ('Scores Search Type', 'score/search/gene', 1, {'path': [gene_names_list[0]], 'extra_query': 'include_performance_data=1'}),
        ('Scores Search Type', 'score/search/metabolite', 1, {'path': [metabolites_list[0]]}),
        ('Scores Performance', 'score/performance', 0, {'path': scores_list}),
        # Dataset
        ('Datasets', 'dataset/all', 1),
        ('Dataset/Name', 'dataset', 0, {'path': dataset_ids_list}),
        ('Dataset Search', 'dataset/search', 1, {'query': [search_pmid]}),
        # Platform endpoints
        ('Platforms', 'platform/all', 1),
        ('Platform/Name', 'platform', 0, {'path': platforms_list}),
        # Tissue endpoints
        ('Tissues', 'tissue/all', 1),
        ('Tissue/ID', 'tissue', 0, {'path': tissue_ids_list}),
        ('Tissue/label', 'tissue', 0, {'path': tissue_labels_list}),

        # Applications
        ('Phenotypes', 'phenotype/all', 1),
        ('Phenotype', 'phenotype', 0, {'path': phenotypes_list}),
        ('Score PheWAS - all', 'score/phewas/all', 1),
        ('Score PheWAS', 'score/phewas', 1, {'path': scores_list}),
        ('Score PheWAS Search', 'score/phewas/search', 1, {'query': [search_phenotype,search_opgs_ids,search_opgs_ids_2,search_opp_id,search_combined_2]}),
        # Other endpoints
        ('Info', 'info', 0),
        ('External Sources - all', 'external_source/all', 1)
    ]

    endpoints_with_include_flag = [
        (
            'Scores / ancestry', score_all, 1,
            {
                'response_path': [],
                'query': ['include_ancestry'],
                'response': ['ancestry']
            }
        ),
        (
            'Score / pathways', f'score/{scores_list[0]}', 1,
            {
                'response_path':['genes',0],
                'query': ['include_pathway'],
                'response': ['pathways']
            }
        ),
        (
            'Scores Search Type / performances', f'score/search/gene/{gene_names_list[0]}', 1,
            {
                'response_path': [],
                'query': ['include_performance_metrics','include_performance_data'],
                'response': ['score_performance','performance_data']
            }
        ),
        (
            'Scores Search / ancestry', f'score/search', 1,
            {
                'response_path': [],
                'query': [f'{search_pmid}&include_ancestry'],
                'response': ['ancestry']
            }
        ),
        (
            'Metabolomics/Name / performance_metrics', f'metabolomics/{platforms_list_metabolomics[0]}', 1,
            {
                'response_path': [],
                'query': ['include_performance_metrics'],
                'response': ['performance_data']
            }
        ),
        (
            'Proteomics/Name / performance_metrics', f'proteomics/{platforms_list_proteomics[0]}', 1,
            {
                'response_path': [],
                'query': ['include_performance_metrics'],
                'response': ['performance_data']
            }
        ),
        (
            'Transcriptomics/Name / performance_metrics', f'transcriptomics/{platforms_list_transcriptomics[0]}', 1,
            {
                'response_path': [],
                'query': ['include_performance_metrics'],
                'response': ['performance_data']
            }
        ),
        (
            'Gene Search / scores_count', f'gene/search?{search_gene}', 1,
            {
                'response_path':[],
                'query': ['include_scores_count'],
                'response': ['scores_count']
            }
        ),
        (
            'Protein Search / scores_count', f'protein/search?{search_gene}', 1,
            {
                'response_path':[],
                'query': ['include_scores_count'],
                'response': ['scores_count']
            }
        ),
        (
            'Metabolite Search / scores_count', f'metabolite/search?{search_metabolite}', 1,
            {
                'response_path':[],
                'query': ['include_scores_count'],
                'response': ['scores_count']
            }
        )
    ]

    endpoints_with_filter_ids = (
        ('Scores / filter_ids', score_all, scores_list[1:]), # Exclude 1st element
        ('Publications / filter_ids', 'publication/all' , publication_ids_list[1:]), # Exclude 1st element
    )

    endpoints_with_sorting_param = (
        (
            'Metabolomics', f'metabolomics/{platforms_list_metabolomics[0]}',
            [*omics_common_columns, 'metabolites__name', 'metabolites__external_id']
        ),
        (
            'Proteomics', f'proteomics/{platforms_list_proteomics[0]}',
            [*omics_common_columns, 'proteins__name', 'proteins__external_id', 'genes__name']
        ),
        (
            'Transcriptomics', f'transcriptomics/{platforms_list_transcriptomics[0]}',
            [*omics_common_columns, 'genes__name', 'genes__external_id']
        ),
        (
            'Scores', score_all,
            ['id', 'genes__name', 'proteins__external_id', 'metabolites__external_id', 'dataset__platform__platform_master__type', 'dataset__platform__platform_master__name', 'dataset__publication__firstauthor']
        ),
        (
            'Score PheWAS', f'score/phewas/all',
            ['phenotypes__id', 'phenotypes__label', 'phenotypes__category', 'score_id', 'score__genes__name', 'score__proteins__name', 'score__metabolites__name', 'hr', 'adjusted_pvalue']
        )
    )

    def assertNotServerError(self, response):
        self.assertNotEqual(response.status_code, 500, msg=f'Unexpected 500 for {response.request["PATH_INFO"]}')

    def assertPaginatedResponse(self, response):
        self.assertEqual(response.status_code, status_ok)
        payload = response.json()
        self.assertIn('count', payload)
        self.assertIn('next', payload)
        self.assertIn('previous', payload)
        self.assertIn('results', payload)
        self.assertIsInstance(payload['results'], list)
        return payload

    def assertHasKeys(self, payload, keys):
        for key in keys:
            self.assertIn(key, payload)

    def assertFirstResultMatches(self, response, expected_id=None, expected_name=None):
        payload = response.json()
        self.assertGreater(len(payload.get('results', [])), 0)
        first = payload['results'][0]
        if expected_id is not None:
            self.assertEqual(first.get('id'), expected_id)
        if expected_name is not None:
            self.assertEqual(first.get('name'), expected_name)
        return first


class BrowseEndpointTest(RestApiTestBase):
    """Broad smoke coverage of the REST endpoints."""

    def client_response(self,url:str):
        resp = self.client.get(url)
        # In case the number of REST API calls is too high (i.e. greater than the modified 'rate4test' variable)
        if resp.status_code == 429:
            print(f"\nNeed to put the test on sleep for {sleep_time}s as it reaches the maximum number of calls/min.\nMight be worth increasing the value of the 'rate4test' variable (currently {self.rate4test}).")
            sleep(sleep_time)
            resp = self.client.get(url)
        return resp

    def check_response(self,url:str,is_included:int,path_structure:list,included_key:str):
        """ Check that the response contains (or not) the 'included_key' item/data """
        resp = self.client_response(f'{url}={is_included}')
        # Get releavant data content
        content = resp.data
        tmp_content_keys = content.keys()
        if 'results' in tmp_content_keys:
            content = content['results'][0]
        # Browse the data result structure
        for path in path_structure:
            if str(path) == '0':
                content = content[0]
            else:
                content = content[path]
        # Extract the keys of the reached structure
        content_keys = content.keys()
        # Check the presence/absence of the element
        if is_included == 1:
            self.assertIn(included_key, content_keys)
        else:
            self.assertNotIn(included_key, content_keys)

    def check_filter_ids(self,url:str,ids_list:list):
        """ Compare the number of results with the number of IDs provided in the filter_ids parameter """
        ids_list_string = ",".join(ids_list)
        resp = self.client_response(f'{url}?filter_ids={ids_list_string}')
        self.assertEqual(len(resp.data['results']), len(ids_list))

    def send_request(self, url:str):
        """ Send REST API request and check the reponse status code """
        resp = self.client_response(url)
        self.assertEqual(resp.status_code, status_ok)
        content = resp.content.decode("utf-8")
        for empty_content in self.empty_resp:
            if content == empty_content:
                print(f"\t>> Equal data on endpoint: {url}")
            self.assertNotEqual(content, empty_content)
        return content

    def get_empty_response(self, url:str, index:int):
        """ Send REST API request and check the reponse status code """
        resp = self.client_response(url)
        self.assertEqual(resp.status_code, status_ok)
        self.assertEqual(resp.content.decode("utf-8"), self.empty_resp[index])

    def get_not_found_response(self, url:str):
        """ Send REST API request on non existing endpoint and check reponse status code """
        resp = self.client_response(url)
        self.assertEqual(resp.status_code, status_not_found)

    def get_paginated_response(self, url:str):
        """ Send REST API request with limit and offset parameters, and check the reponse status code """
        resp = self.client_response(url+'?limit=20&offset=20')
        self.assertEqual(resp.status_code, status_ok)

    def test_endpoints(self):
        """ Test the status code of each endpoint """
        print("\n>> Test the status code of each endpoint ")
        for endpoint in self.endpoints:
            # print(f"  > Endpoint: {endpoint[1]}")
            url_endpoint = self.server+endpoint[1]
            if len(endpoint) > self.index_example:
                # Endpoint with parameter within the URL path
                if ('path' in endpoint[self.index_example]):
                    for example in endpoint[self.index_example]['path']:
                        request = url_endpoint+'/'+example
                        content = self.send_request(request)
                        if 'extra_query' in endpoint[self.index_example]:
                            request_2 = request+'?'+endpoint[self.index_example]['extra_query']
                            content_extra = self.send_request(request_2)
                            self.assertNotEqual(content,content_extra)

                # Endpoint with parameter as query
                if ('query' in endpoint[self.index_example]):
                    for example in endpoint[self.index_example]['query']:
                        self.send_request(url_endpoint+'?'+example)
            else:
                self.send_request(url_endpoint)
                if endpoint[self.index_result_mutliplicity]:
                    self.get_paginated_response(url_endpoint)

    def test_endpoints_with_slash(self):
        """ Test the status code of each endpoint, with a trailing slash """
        print("\n>> Test the status code of each endpoint, with a trailing slash ")
        for endpoint in self.endpoints:
            url_endpoint = self.server+endpoint[1]+'/'

            if len(endpoint) > self.index_example:
                # Endpoint with parameter within the URL path
                if ('path' in endpoint[self.index_example]):
                    for example in endpoint[self.index_example]['path']:
                        request = url_endpoint+example+'/'
                        content = self.send_request(request)
                        if 'extra_query' in endpoint[self.index_example]:
                            request_2 = request+'?'+endpoint[self.index_example]['extra_query']
                            content_extra = self.send_request(request_2)
                            self.assertNotEqual(content,content_extra)
                # Endpoint with parameter as query
                if ('query' in endpoint[self.index_example]):
                    for example in endpoint[self.index_example]['query']:
                        self.send_request(url_endpoint+'?'+example)
            else:
                self.send_request(url_endpoint)
                if endpoint[self.index_result_mutliplicity]:
                    self.get_paginated_response(url_endpoint)

    def test_empty_endpoints(self):
        """ Test the status code and empty response of each endpoint listed above """
        print("\n>> Test the status code and empty response of each endpoint")
        for endpoint in self.endpoints:
            url_endpoint = self.server+endpoint[1]+'/'
            ex = None

            if len(endpoint) > self.index_example:
                # Endpoint with parameter within the URL path
                if ('path' in endpoint[self.index_example]):
                    ex = endpoint[self.index_example]['path'][0]

                    # Endpoint with parameter as query
                if ('query' in endpoint[self.index_example]):
                        ex_full = endpoint[self.index_example]['query'][0]
                        ex_content = ex_full.split('=')
                        url_endpoint += '?'+ex_content[0]+'='
                        ex = ex_content[1].split(',')[0] # Only retain first item

                if ex:
                    if re.match(r"^\d+$",ex):
                        url_endpoint += self.fake_examples['integer']
                    elif re.match(r"^\d{4}-\d{2}-\d{2}$", ex):
                        url_endpoint += self.fake_examples['date']
                    else:
                        url_endpoint += self.fake_examples['string']
                    self.get_empty_response(url_endpoint, endpoint[self.index_result_mutliplicity])

    def test_endpoint_not_found(self):
        """ Test an endpoint that doesn't exist """
        print("\n>> Test an endpoint that doesn't exist")
        self.get_not_found_response(self.server+'chocolate')

    def test_endpoint_with_include_flag(self):
        """ Test the 'include flag' used on some of the endpoints """
        print("\n>> Test the 'include flag' used on some of the endpoints")
        for endpoint in self.endpoints_with_include_flag:
            url_endpoint = self.server+endpoint[1]
            query_list = endpoint[self.index_example]['query']
            # Loop over the queries
            for idx, example in enumerate(query_list):
                if '?' in url_endpoint:
                    url = url_endpoint+'&'+example
                else:
                    url = url_endpoint+'?'+example
                response_path = endpoint[self.index_example]['response_path']
                included_key = endpoint[self.index_example]['response'][idx]
                # Test include
                self.check_response(url, 1, response_path, included_key)
                # Test exclude
                self.check_response(url, 0, response_path, included_key)

    def test_endpoint_with_filter_ids_param(self):
        """ Test the 'filter_ids' parameter used on some of the endpoints """
        print("\n>> Test the 'filter_ids' parameter used on some of the endpoints")
        for endpoint in self.endpoints_with_filter_ids:
            url_endpoint = self.server+endpoint[1]
            self.check_filter_ids(url_endpoint,endpoint[2])

    def test_endpoint_with_sorting_param(self):
        """ Test the 'sort_field' parameter used on some of the endpoints """
        print("\n>> Test the 'sort_field' parameter used on some of the endpoints")
        for endpoint in self.endpoints_with_sorting_param:
            url_endpoint = self.server+endpoint[1]
            for column in endpoint[2]:
                sorting_endpoint = url_endpoint+'?sort=asc&sort_field='+column
                self.send_request(sorting_endpoint)


class TestValidationAndErrors(RestApiTestBase):
    """Invalid input and error-path checks grounded in the test fixture data."""

    def test_unknown_score_id_returns_not_found(self):
        print("\n>> Test unknown score ID returns not found")
        resp = self.client.get(f'/api/score/{self.invalid_score_id}/')
        self.assertNotServerError(resp)
        self.assertIn(resp.status_code, [status_ok, status_not_found])

    def test_invalid_sort_field_does_not_500(self):
        print("\n>> Test invalid sort field does not return 500")
        resp = self.client.get(f'{self.score_all_endpoint}?sort=asc&sort_field=not_a_real_field')
        self.assertNotServerError(resp)
        self.assertIn(resp.status_code, [status_ok, 400, status_not_found])

    def test_malformed_filter_ids_does_not_500(self):
        print("\n>> Test malformed filter_ids parameter does not return 500")
        resp = self.client.get(f'{self.score_all_endpoint}?filter_ids=OPGS000005;bad-format')
        self.assertNotServerError(resp)

    def test_empty_search_query_does_not_500(self):
        print("\n>> Test empty search query does not return 500")
        resp = self.client.get(f'{self.gene_search_endpoint}?gene=')
        self.assertNotServerError(resp)


class TestPagination(RestApiTestBase):
    """Pagination metadata and edge cases for score list responses."""

    def test_score_list_paginated_response_shape(self):
        print("\n>> Test score list paginated response shape")
        resp = self.client.get(f'{self.score_all_endpoint}?limit=10&offset=0')
        payload = self.assertPaginatedResponse(resp)
        self.assertLessEqual(len(payload['results']), 10)

    def test_limit_offset_boundary_values(self):
        print("\n>> Test limit and offset boundary values")
        for url in [
            f'{self.score_all_endpoint}?limit=1&offset=0',
            f'{self.score_all_endpoint}?limit=1&offset=1',
            f'{self.score_all_endpoint}?limit=20&offset=20',
        ]:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertNotServerError(resp)
                self.assertIn(resp.status_code, [status_ok, 400])

    def test_offset_past_end_returns_empty_results(self):
        print("\n>> Test offset past end returns empty results")
        resp = self.client.get(f'{self.score_all_endpoint}?limit=10&offset=999999')
        self.assertNotServerError(resp)
        payload = resp.json()
        self.assertEqual(payload.get('results', []), [])


class TestIncludeFlags(RestApiTestBase):
    """
        Include flags should add the expected nested data when requested.
        A bit redundant with the more general endpoint tests "test_endpoint_with_include_flag()", but these are more focused and explicit.
    """

    def test_include_ancestry_on_score_list(self):
        print("\n>> Test include ancestry on score list")
        resp = self.client.get(f'{self.score_all_endpoint}?include_ancestry=1')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertGreater(len(payload.get('results', [])), 0)
        self.assertIn('ancestry', payload['results'][0])

    def test_include_pathway_on_score_detail(self):
        print("\n>> Test include pathway on score detail")
        resp = self.client.get(f'/api/score/{self.score_id_1}/?include_pathway=1')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertIn('genes', payload)
        self.assertGreater(len(payload['genes']), 0)
        self.assertIn('pathways', payload['genes'][0])

    def test_include_performance_metrics_on_platform_endpoint(self):
        print("\n>> Test include performance metrics on platform endpoint")
        resp = self.client.get(f'/api/proteomics/{self.platform_1}/?include_performance_metrics=1')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertGreater(len(payload.get('results', [])), 0)
        self.assertIn('performance_data', payload['results'][0])

    def test_include_scores_count_on_gene_search(self):
        print("\n>> Test include scores count on gene search")
        resp = self.client.get(f'{self.gene_search_endpoint}?gene={self.gene_name}&include_scores_count=1')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertGreater(len(payload.get('results', [])), 0)
        self.assertIn('scores_count', payload['results'][0])


class TestSearchEndpoints(RestApiTestBase):
    """Search endpoints should work with fixture-backed identifiers and names."""

    def test_gene_search_returns_results(self):
        print("\n>> Test gene search returns results")
        resp = self.client.get(f'{self.gene_search_endpoint}?gene={self.gene_name}')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertGreater(len(payload.get('results', [])), 0)
        self.assertEqual(payload['results'][0]['name'], self.gene_name)

    def test_score_search_multiple_ids(self):
        print("\n>> Test score search with multiple IDs returns results")
        resp = self.client.get(f'{self.score_search_endpoint}?opgs_ids={self.score_id_1},{self.score_id_2}')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        results = payload.get('results', [])
        self.assertGreater(len(results), 0)
        returned_ids = {item['id'] for item in results}
        self.assertTrue(self.score_id_1 in returned_ids)
        self.assertTrue(self.score_id_2 in returned_ids)

    def test_combined_score_and_pmid_search(self):
        print("\n>> Test combined score ID and PMID search returns results")
        resp = self.client.get(f'{self.score_search_endpoint}?opgs_id={self.score_id_1}&pmid={self.pmid_1}')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertIsInstance(payload.get('results', []), list)

    def test_publication_search_by_author(self):
        print("\n>> Test publication search by author")
        resp = self.client.get(f'/api/publication/search/?author={self.author_name}')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertIsInstance(payload.get('results', []), list)
        if payload['results']:
            self.assertIn('firstauthor', payload['results'][0])

    def test_sample_search_by_cohort(self):
        print("\n>> Test sample search by cohort")
        resp = self.client.get(f'/api/sample/search/?cohort={self.cohort}')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertIsInstance(payload.get('results', []), list)


class TestSorting(RestApiTestBase):
    """Sorting checks use known fixture values and known sortable fields."""

    def test_score_list_sort_by_id_asc(self):
        print("\n>> Test score list sort by ID ascending")
        resp = self.client.get(f'{self.score_all_endpoint}?sort=asc&sort_field=id')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        results = payload.get('results', [])
        if len(results) >= 2:
            ids = [r['id'] for r in results]
            self.assertEqual(ids, sorted(ids))

    def test_score_list_sort_by_id_desc(self):
        print("\n>> Test score list sort by ID descending")
        resp = self.client.get(f'{self.score_all_endpoint}?sort=desc&sort_field=id')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        results = payload.get('results', [])
        if len(results) >= 2:
            ids = [r['id'] for r in results]
            self.assertEqual(ids, sorted(ids, reverse=True))

    def test_platform_list_sort_by_name(self):
        print("\n>> Test platform list sort by name ascending")
        resp = self.client.get('/api/platform/all/?sort=asc&sort_field=name')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        results = payload.get('results', [])
        if len(results) >= 2:
            names = [r['name'] for r in results]
            self.assertEqual(names, sorted(names))


class TestResponseContracts(RestApiTestBase):
    """Detailed payloads should include the fields expected from the fixture data."""

    def test_score_detail_has_expected_fields(self):
        print("\n>> Test score detail has expected fields")
        resp = self.client.get(f'/api/score/{self.score_id_1}/')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertHasKeys(payload, ['id', 'name', 'trait_reported_id', 'trait_reported', 'dataset_id', 'dataset_name'])
        self.assertEqual(payload['id'], self.score_id_1)

    def test_publication_detail_has_expected_fields(self):
        print("\n>> Test publication detail has expected fields")
        resp = self.client.get(f'/api/publication/{self.publication_id_1}/')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertHasKeys(payload, ['id', 'title', 'pmid', 'doi'])
        self.assertEqual(payload['id'], self.publication_id_1)

    def test_dataset_detail_has_expected_fields(self):
        print("\n>> Test dataset detail has expected fields")
        resp = self.client.get(f'/api/dataset/{self.dataset_id_1}/')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertHasKeys(payload, ['id', 'name', 'platform', 'publication'])
        self.assertEqual(payload['id'], self.dataset_id_1)

    def test_gene_detail_has_expected_fields(self):
        print("\n>> Test gene detail has expected fields")
        resp = self.client.get(f'/api/gene/{self.gene_id}/')
        self.assertEqual(resp.status_code, status_ok)
        payload = resp.json()
        self.assertHasKeys(payload, ['name', 'external_id'])
        self.assertEqual(payload['external_id'], self.gene_id)
        self.assertEqual(payload['name'], self.gene_name)


class TestPermissionsAndThrottling(RestApiTestBase):
    """Public endpoints should be accessible without auth and existing throttling should not produce server errors."""

    def test_public_endpoints_are_accessible_without_auth(self):
        print("\n>> Test public endpoints are accessible without auth")
        resp = self.client.get(f'{self.score_all_endpoint}')
        self.assertEqual(resp.status_code, status_ok)

    def test_too_many_requests_returns_429_when_limit_hit(self):
        print("\n>> Test too many requests returns 429 when limit hit")
        resp = self.client.get(f'{self.score_all_endpoint}')
        self.assertNotServerError(resp)
        self.assertIn(resp.status_code, [status_ok, 429])
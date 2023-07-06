from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from rest_framework.serializers import ValidationError
from django.db.models import Prefetch, Q
from omicspred.models import *
from .serializers import *


generic_defer = ['curation_notes']
only_dict = {
    'scores_table': ['id','platform_id','variants_number','platform__id','platform__name'],
    'metabolite': ['id','name','external_id','pathway_group_id','pathway_subgroup_id','pathway_group__id','pathway_group__name','pathway_subgroup__id','pathway_subgroup__name']
}

performance_metric = [Prefetch('performance_metric', queryset=Metric.objects.only('id','performance_id','name_short','estimate').all())]
related_dict = {
    'metabolites': [Prefetch('metabolites', queryset=Metabolite.objects.only(*only_dict['metabolite']).select_related('pathway_group','pathway_subgroup').all().order_by('id'))],
    'proteins': [Prefetch('proteins', queryset=Protein.objects.only('id','name','external_id').all().order_by('id'))],
    'genes': [Prefetch('genes', queryset=Gene.objects.only('id','name','external_id').all().order_by('id'))],
    'genes_sources': [Prefetch('genes', queryset=Gene.objects.only('id','name','external_id','external_id_source').all().order_by('id'))],
    'performances': [Prefetch('score_performance', queryset=Performance.objects.defer('publication','efo').select_related('sample').all().prefetch_related('sample__cohorts','performance_metric').order_by('id'))],
    'performance_cohorts': [Prefetch('score_performance', queryset=Performance.objects.only('id','score_id','cohort_label').all().prefetch_related(*performance_metric).order_by('id'))],
    'perf_select': ['score', 'publication', 'platform', 'efo'],
    'publication_defer': [*generic_defer,'curation_status']
}
missing_index = 0

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Over the fixed rate limit
    if isinstance(exc, Throttled): # check that a Throttled exception is raised
        response.data = { # custom response data
            'message': 'request limit exceeded',
            'availableIn': '%d seconds'%exc.wait
        }
    # Over the maximum number of results per page (limit parameter)
    elif isinstance(exc, ValidationError):
        formatted_exc = ''
        for type in exc.detail.keys():
            if formatted_exc != '':
                formatted_exc += '; '
            formatted_exc += exc.detail[type]
        response.data = { # custom response data
            'status_code': response.status_code,
            'message': formatted_exc
        }
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        response.data = { # custom response data
            'status_code': status.HTTP_404_NOT_FOUND,
            'message': 'This REST endpoint does not exist'
        }
    elif response is not None:
        response.data = { # custom response data
            'status_code': response.status_code,
            'message': str(exc)
        }
    else:
        response.data = {
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Internal Server Error'
        }
    return response


def get_ids_list(object):
    ids_list = []

    # List of IDs provided in the URL
    ids = object.request.query_params.get('filter_ids')
    if ids and ids is not None:
        ids = ids.upper()
        ids_list = ids.split(',')
    # List of IDs provided in a JSON object
    elif 'filter_ids' in object.request.data:
        ids_list = [ x.upper() for x in object.request.data['filter_ids']]
    return ids_list


## Cohorts ##

class RestListCohorts(generics.ListAPIView):
    """
    Retrieve all the Cohorts
    """
    serializer_class = CohortSerializer

    def get_queryset(self):
        queryset = Cohort.objects.all().order_by('name_short')
        # 'filter_ids' parameter: fetch the cohorts from the list of cohort short names
        names_list = get_ids_list(self)
        # Filter the query depending on the parameters used
        if names_list:
            names_list = r'^('+'|'.join(names_list)+')$'
            queryset = queryset.filter(name_short__iregex=names_list)

        return queryset


## Performance metrics ##

class RestListPerformances(generics.ListAPIView):
    """
    Retrieve the PGS Performance Metrics
    """
    queryset = Performance.objects.all().order_by('id')
    serializer_class = PerformanceSerializer


class RestPerformanceSearch(generics.ListAPIView):
    """
    Retrieve the Performance metric(s) using query
    """
    serializer_class = PerformanceSerializer


    def get_queryset(self):

        queryset = Performance.objects.select_related(*related_dict['perf_select']).all().prefetch_related('performance_metric').order_by('id')
        params = 0

        # Search by Score ID
        opgs_id = self.request.query_params.get('opgs_id')
        if opgs_id and opgs_id is not None:
            opgs_id = opgs_id.upper()
            queryset = queryset.filter(score__id=opgs_id)
            params += 1

        # Search by PubMed ID
        pmid = self.request.query_params.get('pmid')
        if pmid and pmid.isnumeric():
            queryset = queryset.filter(publication__pmid=pmid)
            params += 1

        # Search by Platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name=platform)
            params += 1

        if params == 0:
            queryset = []

        return queryset


## Platforms ##

class RestListPlatforms(generics.ListAPIView):
    """
    Retrieve all the Platforms
    """
    queryset = Platform.objects.all().order_by('name')
    serializer_class = PlatformExtendedSerializer


## Publications ##

class RestListPublications(generics.ListAPIView):
    """
    Retrieve the PGS Publications
    """
    serializer_class = PublicationExtendedSerializer

    def get_queryset(self):
        # Fetch all the Publications
        queryset = Publication.objects.defer(*related_dict['publication_defer']).all().order_by('id')

        # Filter by list of Publications IDs
        pmids_list = get_ids_list(self)
        if pmids_list:
            queryset = queryset.filter(pmid__in=pmids_list)

        return queryset


class RestPublicationSearch(generics.ListAPIView):
    """
    Retrieve the Publication(s) using query
    """
    serializer_class = PublicationExtendedSerializer

    def get_queryset(self):
        queryset = Publication.objects.defer(*related_dict['publication_defer']).all().order_by('id')
        params = 0

        # Search by Score ID
        pgs_id = self.request.query_params.get('opgs_id')
        if pgs_id and pgs_id is not None:
            pgs_id = pgs_id.upper()
            try:
                score = Score.objects.only('id','publication__id').select_related('publication').get(id=pgs_id)
                queryset = queryset.filter(id=score.publication.id)
                params += 1
            except Score.DoesNotExist:
                queryset = []

        # Search by Author
        author = self.request.query_params.get('author')
        if author and author is not None:
            queryset = queryset.filter(authors__icontains=author)
            params += 1

        # Search by Pubmed ID
        pmid = self.request.query_params.get('pmid')
        if pmid and pmid.isnumeric():
            queryset = queryset.filter(pmid=pmid)
            params += 1

        if params == 0:
            queryset = []
        return queryset


## Samples ##

class RestListSamples(generics.ListAPIView):
    """
    Retrieve all the Samples
    """
    queryset = Sample.objects.all().order_by('id')
    serializer_class = SampleSerializer


## Scores ##

class RestListScores(generics.ListAPIView):
    """
    Retrieve the Polygenic Scores
    """
    serializer_class = ScoreSerializer

    def get_queryset(self):
        # Fetch all the Scores
        # queryset = Score.objects.defer(*related_dict['score_defer']).select_related('publication').all().prefetch_related(*related_dict['score_prefetch']).order_by('num')
        queryset = Score.objects.select_related('publication','platform').all().order_by('num')

        # Filter by list of Score IDs
        ids_list = get_ids_list(self)
        if ids_list:
            queryset = queryset.filter(id__in=ids_list)

        return queryset


class RestScore(generics.RetrieveAPIView):
    """
    Retrieve one Polygenic Score (PGS)
    """

    def get(self, request, opgs_id):
        opgs_id = opgs_id.upper()
        try:
            queryset = Score.objects.select_related('publication','platform').get(id=opgs_id)
            # queryset = Score.objects.defer(*related_dict['score_defer']).select_related('publication').prefetch_related(*related_dict['score_prefetch']).get(id=pgs_id)
        except Score.DoesNotExist:
            queryset = None
        serializer = ScoreSerializer(queryset,many=False)
        return Response(serializer.data)


class RestScoreSearchByGene(generics.ListAPIView):
    """
    Search the Polygenic Score(s) using gene name/id
    """
    serializer_class = ScoreSerializer

    def get_queryset(self):
        try:
            gene = self.kwargs['gene']
            # Database filtering
            queryset = Score.objects.select_related('publication','platform').filter(Q(genes__name__iexact=gene) | Q(genes__external_id__iexact=gene)).prefetch_related('genes').order_by('num')
        except Score.DoesNotExist:
            queryset = []
        return queryset


class RestScoreSearchByProtein(generics.ListAPIView):
    """
    Search the Polygenic Score(s) using protein name/id
    """
    serializer_class = ScoreSerializer

    def get_queryset(self):
        try:
            protein = self.kwargs['protein']
            # Database filtering
            queryset = Score.objects.select_related('publication','platform').filter(Q(proteins__name__iexact=protein) | Q(proteins__external_id__iexact=protein)).prefetch_related('proteins').order_by('num')
        except Score.DoesNotExist:
            queryset = []
        return queryset


class RestScoreSearchByMetabolite(generics.ListAPIView):
    """
    Search the Polygenic Score(s) using metabolite name/id
    """
    serializer_class = ScoreSerializer

    def get_queryset(self):
        try:
            metabolite = self.kwargs['metabolite']
            # Database filtering
            queryset = Score.objects.select_related('publication','platform').filter(Q(metabolites__name__iexact=metabolite) | Q(metabolites__external_id__iexact=metabolite)).prefetch_related('metabolites').order_by('num')
            print(queryset.query)
        except Score.DoesNotExist:
            queryset = []
        return queryset


class RestScoreSearch(generics.ListAPIView):
    """
    Search the Polygenic Score(s) using query
    """
    serializer_class = ScoreSerializer

    def get_queryset(self):
        queryset = Score.objects.select_related('publication','platform').all().order_by('num')
        params = 0

        # Search by list of Score IDs
        opgs_ids = self.request.query_params.get('opgs_ids')
        if opgs_ids and opgs_ids is not None:
            opgs_ids = opgs_ids.upper()
            opgs_ids_list = opgs_ids.split(',')
            queryset = queryset.filter(id__in=opgs_ids_list)
            params += 1

        # Search by Pubmed ID
        pmid = self.request.query_params.get('pmid')
        if pmid and pmid.isnumeric():
            queryset = queryset.filter(publication__pmid=pmid)
            params += 1

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
            params += 1

        if params == 0:
            queryset = []

        return queryset


## Tables ##

class RestTableSearch(generics.ListAPIView):
    serializer_class = ScoreExtendedSerializer

    def get_queryset(self):
        queryset = Score.objects.select_related('publication','platform').all().order_by('num')
        params = 0

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
            params += 1

        if params == 0:
            queryset = []

        return queryset


class RestMetaboliteTableSearch(generics.RetrieveAPIView):

    def get(self,request):
        #queryset = Score.objects.select_related('platform').all().prefetch_related('metabolites').order_by('num')
        queryset = Score.objects.only(*only_dict['scores_table']).select_related('platform').all().prefetch_related(*related_dict['performances'],*related_dict['metabolites']).order_by('num')

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
        else:
            queryset = []

        data = []
        score_col = { "name": "OMICSPRED ID", "data": {} }

        if platform == 'Metabolon':
            metabolon_col = { "name": "Metabolon ID", "data": {} }
        else:
            metabolon_col = None

        metabo_col = { "name": "Biochemical Name", "data": {} }
        pathway_grp_col = { "name": "Pathway Group", "data": {} }
        pathway_subgrp_col = { "name": "Pathway Subgroup", "data": {} }
        variants_nb_col = { "name": "#SNP", "data": {} }
        cohort_cols = {}
        cohort_cols_names = []

        idx = 0
        for score in queryset:
            # OMICPRED ID
            score_col["data"][idx] = score.id

            # Metabolite Information
            metabolite = score.metabolites.all()[0]
            # - Metabolon ID
            if metabolon_col:
                metabolon_col["data"][idx] = metabolite.external_id
            # - Biochemical Name
            metabo_col["data"][idx] = metabolite.name
            # - Pathway Group
            pathway_group = None
            if metabolite.pathway_group:
                pathway_group = metabolite.pathway_group.name
            pathway_grp_col["data"][idx] = pathway_group
            # - Pathway Subgroup
            pathway_subgroup = None
            if metabolite.pathway_subgroup:
                pathway_subgroup = metabolite.pathway_subgroup.name
            pathway_subgrp_col["data"][idx] = pathway_subgroup

            # #SNP
            variants_nb_col["data"][idx] = score.variants_number

            for perf in score.score_performance.all():
                cohort_name = perf.sample.cohorts.all()[0].name_short
                for metric in perf.performance_metrics:
                    metric_name = metric['name_short']
                    if 'estimate' in metric.keys():
                        estimate = metric['estimate']
                    else:
                        estimate = ''

                    colname = f'{cohort_name}_{metric_name}'
                    collabel = f'{cohort_name} {metric_name}'
                    # Cohort estimate
                    if colname not in cohort_cols_names:
                        cohort_cols[colname] = { "name": collabel, "data": {} }
                        cohort_cols_names.append(colname)
                    cohort_cols[colname]["data"][idx] = estimate
                    # Cohort pvalue
                    # if 'pvalue' in metric.keys():
                    #     pvalue = metric['pvalue']
                    # else:
                    #     pvalue = ''
                    # pval_colname = f'{colname}_pvalue'
                    # pval_collabel = f'{colname} (p-value)'
                    # if pval_colname not in cohort_cols_names:
                    #     cohort_cols[pval_colname] = { "name": pval_collabel, "data": {} }
                    #     cohort_cols_names.append(pval_colname)
                    # cohort_cols[pval_colname]["data"][idx] = pvalue
            for col in cohort_cols.keys():
                if idx not in cohort_cols[col]["data"].keys():
                    cohort_cols[col]["data"][idx] = ''
                if idx != 0:
                    if missing_index not in cohort_cols[col]["data"].keys():
                        cohort_cols[col]["data"][missing_index] = ''
            idx += 1

        data.append(score_col)
        if metabolon_col:
            data.append(metabolon_col)
        data.append(metabo_col)
        data.append(pathway_grp_col)
        data.append(pathway_subgrp_col)
        data.append(variants_nb_col)

        for colname in cohort_cols_names:
            data.append(cohort_cols[colname])

        return Response(data)


class RestProteinTableSearch(generics.RetrieveAPIView):
    def get(self,request):
        queryset = Score.objects.only(*only_dict['scores_table']).select_related('platform').all().prefetch_related(*related_dict['performances'],*related_dict['genes'],*related_dict['proteins']).order_by('num')

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
        else:
            queryset = []

        data = []
        score_col = { "name": "OMICSPRED ID", "data": {} }

        if platform == 'Somalogic':
            somascan_col = { "name": "SOMAscan ID", "data": {} }
        else:
            somascan_col = None

        uniprot_col = { "name": "UniProt ID", "data": {} }
        gene_col = { "name": "Gene", "data": {} }
        protein_col = { "name": "Protein", "data": {} }
        variants_nb_col = { "name": "#SNP", "data": {} }
        cohort_cols = {}
        cohort_cols_names = []

        idx = 0
        for score in queryset:
            # idx = f'"{idx}"'
            # OMICPRED ID
            score_col["data"][idx] = score.id
            # SOMAscan ID
            if somascan_col:
                somascan_col["data"][idx] = score.name

            # Protein Information
            # Sorting later instead of using the queryset method "order_by" to avoid generating more SQL queries
            proteins = [x for x in score.proteins.all()]
            # - UniProt ID(s)
            uniprot_ids = set()
            for protein_id in sorted([x.external_id for x in proteins]):
                if protein_id:
                    uniprot_ids.add(protein_id)
            uniprot_col["data"][idx] = ';'.join(uniprot_ids)
            # - Protein name(s)
            protein_names = set()
            for protein_name in sorted([x.name for x in proteins]):
                if protein_name:
                    protein_names.add(protein_name)
            protein_col["data"][idx] = ';'.join(protein_names)

            # Gene informatiom
            gene_names = set()
            # Sorting later instead of using the queryset method "order_by" to avoid generating more SQL queries
            for gene_name in sorted([x.name for x in score.genes.all()]):
                if gene_name:
                    gene_names.add(gene_name)
            gene_col["data"][idx] = ';'.join(gene_names)

            # #SNP
            variants_nb_col["data"][idx] = score.variants_number

            for perf in score.score_performance.all():
                cohort_name = perf.sample.cohorts.all()[0].name_short
                for metric in perf.performance_metrics:
                    metric_name = metric['name_short']
                    if 'estimate' in metric.keys():
                        estimate = metric['estimate']
                    else:
                        estimate = ''

                    colname = f'{cohort_name}_{metric_name}'
                    collabel = f'{cohort_name} {metric_name}'
                    # Cohort estimate
                    if colname not in cohort_cols_names:
                        cohort_cols[colname] = { "name": collabel, "data": {} }
                        cohort_cols_names.append(colname)
                    cohort_cols[colname]["data"][idx] = estimate
            #         # Cohort pvalue
            #         # if 'pvalue' in metric.keys():
            #         #     pvalue = metric['pvalue']
            #         # else:
            #         #     pvalue = ''
            #         # pval_colname = f'{colname}_pvalue'
            #         # pval_collabel = f'{colname} (p-value)'
            #         # if pval_colname not in cohort_cols_names:
            #         #     cohort_cols[pval_colname] = { "name": pval_collabel, "data": {} }
            #         #     cohort_cols_names.append(pval_colname)
            #         # cohort_cols[pval_colname]["data"][idx] = pvalue
            for col in cohort_cols.keys():
                if idx not in cohort_cols[col]["data"].keys():
                    cohort_cols[col]["data"][idx] = ''
                if idx != 0:
                    if missing_index not in cohort_cols[col]["data"].keys():
                        cohort_cols[col]["data"][missing_index] = ''
            idx += 1

        data.append(score_col)
        if somascan_col:
            data.append(somascan_col)
        data.append(uniprot_col)
        data.append(gene_col)
        data.append(protein_col)
        data.append(variants_nb_col)

        for colname in cohort_cols_names:
            data.append(cohort_cols[colname])

        return Response(data)


class RestTranscriptTableSearch(generics.RetrieveAPIView):

    def get(self,request):
        # queryset = Score.objects.select_related('platform').all().prefetch_related('genes').order_by('num')
        queryset = Score.objects.only(*only_dict['scores_table']).select_related('platform').all().prefetch_related(*related_dict['performances'],*related_dict['genes_sources']).order_by('num') # transcripts

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
        else:
            queryset = []

        data = []
        score_col = { "name": "OMICSPRED ID", "data": {} }

        ensembl_col = { "name": "Ensembl ID", "data": {} }
        gene_col = { "name": "Gene", "data": {} }
        # transcript_col = { "name": "Transcript", "data": {} }
        variants_nb_col = { "name": "#SNP", "data": {} }
        cohort_cols = {}
        cohort_cols_names = []

        idx = 0
        for score in queryset:
            # idx = f"{idx}"
            # OMICPRED ID
            score_col["data"][idx] = score.id

            # Gene informatiom
            ensembl_ids = set()
            gene_names = set()
            # Sorting later instead of using the queryset method "order_by" to avoid generating more SQL queries
            genes = score.genes.all()
            for gene in sorted(genes, key=lambda x: x.name):
                if gene.external_id and gene.external_id_source == 'Ensembl':
                        ensembl_ids.add(gene.external_id)
                if gene.name:
                    gene_names.add(gene.name)
            ensembl_col["data"][idx] = ';'.join(ensembl_ids)
            gene_col["data"][idx] = ';'.join(gene_names)

            # # Transcript informatiom
            # transcript_names = set()
            # for transcript in score.transcripts.all().order_by('name'):
            #     if transcript.name:
            #         transcript_names.add(transcript.name)
            # transcript_col["data"][idx] = ';'.join(transcript_names)
            # #SNP
            variants_nb_col["data"][idx] = score.variants_number

            for perf in score.score_performance.all():
                cohort_name = perf.sample.cohorts.all()[0].name_short
                for metric in perf.performance_metrics:
                    metric_name = metric['name_short']
                    if 'estimate' in metric.keys():
                        estimate = metric['estimate']
                    else:
                        estimate = ''

                    colname = f'{cohort_name}_{metric_name}'
                    collabel = f'{cohort_name} {metric_name}'
                    # Cohort estimate
                    if colname not in cohort_cols_names:
                        cohort_cols[colname] = { "name": collabel, "data": {} }
                        cohort_cols_names.append(colname)
                    cohort_cols[colname]["data"][idx] = estimate

                    # Cohort pvalue
                    # if 'pvalue' in metric.keys():
                    #     pvalue = metric['pvalue']
                    # else:
                    #     pvalue = ''
                    # pval_colname = f'{colname}_pvalue'
                    # pval_collabel = f'{colname} (p-value)'
                    # if pval_colname not in cohort_cols_names:
                    #     cohort_cols[pval_colname] = { "name": pval_collabel, "data": {} }
                    #     cohort_cols_names.append(pval_colname)
                    # cohort_cols[pval_colname]["data"][idx] = pvalue

            for col in cohort_cols.keys():
                if idx not in cohort_cols[col]["data"].keys():
                    cohort_cols[col]["data"][idx] = ''
                if idx != 0:
                    if missing_index not in cohort_cols[col]["data"].keys():
                        cohort_cols[col]["data"][missing_index] = ''
            idx += 1

        data.append(score_col)
        data.append(ensembl_col)
        data.append(gene_col)
        data.append(variants_nb_col)

        for colname in cohort_cols_names:
            data.append(cohort_cols[colname])

        return Response(data)


## Plots ##

class RestPlotSearch(generics.RetrieveAPIView):

    def get(self,request):
        # score_performance = [Prefetch('score_performance', queryset=Score.objects.only('num').all())]
        #queryset = Score.objects.only('num','platform_id','platform__id','platform__name','score_performance').select_related('platform').all().order_by('num')
        #print(Performance.objects.only('score_id','platform_id','platform__id','platform__name','sample_id','sample__id').select_related('platform','sample').all().order_by('score_id').query)

        queryset = Performance.objects.only('score_id','platform_id','platform__id','platform__name','sample_id','sample__id').select_related('platform','sample').all().prefetch_related('sample__cohorts').order_by('score_id')
        # print(Performance.objects.only('score_id','platform_id','platform__id','platform__name','sample_id','sample__cohort').select_related('platform','sample').all().order_by('score_id').query)
        params = 0

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
            params += 1

        if params == 0:
            queryset = []

        data = []
        cohort_cols = {}
        cohort_cols_names = []

        score_ids_list = [x.score_id for x in queryset]
        score_ids = set(score_ids_list)
        # print(score_ids)
        score_idx = {}
        new_score_ids = list(score_ids)
        for idx, score_id in enumerate(new_score_ids):
            # print(f'{idx}: {score_id}')
            score_idx[score_id] = idx
        # print(score_idx)
        # for score in queryset:
        for perf in queryset:
            perf_score_id = perf.score_id
            idx = score_idx[perf_score_id]
            #print(score.score_performance.all().query)
        # for perf in score.score_performance.all():
            cohort_name = perf.sample.cohorts.all()[0].name_short
            cohort_name = cohort_name.replace(' ','_')
            for metric in perf.performance_metrics:
                metric_name = metric['name_short']
                if 'estimate' in metric.keys():
                    estimate = metric['estimate']
                else:
                    estimate = None
                colname = f'{cohort_name}_{metric_name}'
                # Cohort estimate
                if colname not in cohort_cols_names:
                    cohort_cols[colname] = { "name": cohort_name, "title": colname, "type": f'_{metric_name}' ,  "data": {} }
                    cohort_cols_names.append(colname)
                cohort_cols[colname]["data"][idx] = estimate
            for col in cohort_cols.keys():
                if idx not in cohort_cols[col]["data"].keys():
                    cohort_cols[col]["data"][idx] = None
                if idx != 0:
                    if missing_index not in cohort_cols[col]["data"].keys():
                        cohort_cols[col]["data"][missing_index] = None

        for colname in cohort_cols_names:
            data.append(cohort_cols[colname])

        return Response(data)


## Gene ##



## Tests ##
class RestTestMetabolite(generics.ListAPIView):
    serializer_class = ScoreMetaboliteSerializer

    def get_queryset(self):
        queryset = Score.objects.only(*only_dict['scores_table']).select_related('platform').all().prefetch_related(*related_dict['metabolites'],*related_dict['performance_cohorts']).order_by('num')

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
        else:
            queryset = []

        return queryset

class RestTestProtein(generics.ListAPIView):
    serializer_class = ScoreProteinSerializer

    def get_queryset(self):
        queryset = Score.objects.only(*only_dict['scores_table']).select_related('platform').all().prefetch_related(*related_dict['proteins'],*related_dict['genes'],*related_dict['performance_cohorts']).order_by('num')

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
        else:
            queryset = []

        return queryset


class RestTestTranscript(generics.ListAPIView):
    serializer_class = ScoreTranscriptSerializer

    def get_queryset(self):
        queryset = Score.objects.only(*only_dict['scores_table']).select_related('platform').all().prefetch_related(*related_dict['genes'],*related_dict['performance_cohorts']).order_by('num')

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
        else:
            queryset = []

        return queryset

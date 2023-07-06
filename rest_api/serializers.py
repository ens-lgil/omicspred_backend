from rest_framework import serializers
from omicspred.models import *


class CohortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cohort
        meta_fields = ('name_short', 'name_full', 'name_others', 'url')
        fields = meta_fields
        read_only_fields = meta_fields


# class CohortExtendedSerializer(CohortSerializer):
#
#     class Meta(CohortSerializer.Meta):
#         meta_fields = ('associated_pgs_ids',)
#         fields = CohortSerializer.Meta.fields + meta_fields
#         read_only_fields = CohortSerializer.Meta.read_only_fields + meta_fields


class SampleSerializer(serializers.ModelSerializer):
    cohorts = CohortSerializer(many=True, read_only=True)

    class Meta:
        model = Sample
        meta_fields = ('sample_number', 'sample_percent_male', 'sample_age', 'sample_age_sd',
                    'ancestry_broad', 'ancestry_free', 'ancestry_country', 'ancestry_additional',
                    'source_gwas_catalog', 'source_pmid','source_doi', 'cohorts_additional','cohorts','tissue_name')
        fields = meta_fields
        read_only_fields = meta_fields


class MetricSerializer(serializers.ModelSerializer):

    class Meta:
        model = Metric
        meta_fields = ('name', 'name_short', 'performance_type', 'estimate', 'pvalue')
        fields = meta_fields
        read_only_fields = meta_fields


class PublicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publication
        meta_fields = ('title', 'doi', 'pmid', 'journal', 'firstauthor', 'date_publication')
        fields = meta_fields
        read_only_fields = meta_fields


class PublicationExtendedSerializer(PublicationSerializer):
    date_release = serializers.SerializerMethodField('get_date_released')

    class Meta(PublicationSerializer.Meta):
        model = Publication
        meta_fields = ('date_release', 'authors')
        fields = PublicationSerializer.Meta.fields + meta_fields
        read_only_fields = PublicationSerializer.Meta.read_only_fields + meta_fields

    def get_date_released(self, obj):
        return obj.date_released


class PlatformSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = Platform
        meta_fields = ('id', 'name', 'full_name', 'version', 'technic', 'type')
        fields = meta_fields
        read_only_fields = meta_fields

    def get_full_name(self, obj):
        if obj.full_name:
            return obj.full_name
        else:
            return obj.name


class PlatformExtendedSerializer(PlatformSerializer):
    class Meta:
        model = Platform
        meta_fields = ('scores_count',)
        fields = PlatformSerializer.Meta.fields + meta_fields
        read_only_fields = PlatformSerializer.Meta.read_only_fields + meta_fields


class EFOSerializer(serializers.ModelSerializer):

    class Meta:
        model = EFO
        meta_fields = ('id', 'label', 'description', 'url', 'type')
        fields = meta_fields
        read_only_fields = meta_fields


class PathwaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathway
        meta_fields = ('name', 'external_id', 'external_id_source')
        fields = meta_fields
        read_only_fields = meta_fields


class GeneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gene
        meta_fields = ('name', 'external_id', 'external_id_source')
        fields = meta_fields
        read_only_fields = meta_fields


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        meta_fields = ('name', 'external_id', 'external_id_source')
        fields = meta_fields
        read_only_fields = meta_fields


class ProteinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protein
        meta_fields = ('name', 'external_id', 'external_id_source')
        fields = meta_fields
        read_only_fields = meta_fields


class MetaboliteSerializer(serializers.ModelSerializer):
    pathway_group = PathwaySerializer(many=False, read_only=True)
    pathway_subgroup = PathwaySerializer(many=False, read_only=True)
    class Meta:
        model = Metabolite
        meta_fields = ('name', 'external_id', 'external_id_source', 'pathway_group', 'pathway_subgroup')
        fields = meta_fields
        read_only_fields = meta_fields


class ScoreSerializer(serializers.ModelSerializer):
    publication = PublicationSerializer(many=False, read_only=True)
    platform = PlatformSerializer(many=False, read_only=True)

    genes = GeneSerializer(many=True, read_only=True)
    transcripts = TranscriptSerializer(many=True, read_only=True)
    proteins = ProteinSerializer(many=True, read_only=True)
    metabolites = MetaboliteSerializer(many=True, read_only=True)
    # efos = EFOSerializer(many=True, read_only=True)

    date_release = serializers.SerializerMethodField('get_date_released')

    class Meta:
        model = Score
        meta_fields = ('id', 'name', 'trait_reported', 'trait_additional', 'method_name', 'method_params',
                    'trait_reported', 'trait_additional', 'method_name', 'method_params', 'variants_number',
                    'publication', 'platform', 'genes', 'transcripts', 'proteins', 'metabolites', #'efos',
                    'variants_interactions', 'variants_genomebuild', 'date_release')
        fields = meta_fields
        read_only_fields = meta_fields

    def get_date_released(self, obj):
        return obj.date_released


# class ScoreIdSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Score
#         meta_fields = ('num','id')
#         fields = meta_fields
#         read_only_fields = meta_fields


class PerformanceSerializer(serializers.ModelSerializer):
    publication = PublicationSerializer(many=False, read_only=True)
    sample = SampleSerializer(many=False, read_only=True)
    platform = PlatformSerializer(many=False, read_only=True)
    efo = EFOSerializer(many=False, read_only=True)

    evaluation_type = serializers.SerializerMethodField('get_eval_type_label')

    class Meta:
        model = Performance
        meta_fields = ('id', 'associated_pgs_id','publication','sample', 'platform', 'efo',
                'performance_metrics',
                'evaluation_type', 'performance_additional', 'covariates')
        fields = meta_fields
        read_only_fields = meta_fields

    def get_eval_type_label(self, obj):
        return obj.get_eval_type_display()


class PerformanceLightSerializer(serializers.ModelSerializer):
    sample = SampleSerializer(many=False, read_only=True)
    class Meta:
        model = Performance
        meta_fields = ('sample', 'performance_metrics', 'performance_additional', 'eval_type', 'covariates')
        fields = meta_fields
        read_only_fields = meta_fields



###########
## TESTS ##
###########
class ScoreExtendedSerializer(serializers.ModelSerializer):
    publication = PublicationSerializer(many=False, read_only=True)
    platform = PlatformSerializer(many=False, read_only=True)

    genes = GeneSerializer(many=True, read_only=True)
    transcripts = TranscriptSerializer(many=True, read_only=True)
    proteins = ProteinSerializer(many=True, read_only=True)
    metabolites = MetaboliteSerializer(many=True, read_only=True)
    score_performance = PerformanceLightSerializer(many=True, read_only=True)

    date_release = serializers.SerializerMethodField('get_date_released')

    class Meta:
        model = Score
        meta_fields = ('id', 'name', 'trait_reported', 'trait_additional', 'method_name', 'method_params',
                    'trait_reported', 'trait_additional', 'method_name', 'method_params', 'variants_number',
                    'publication', 'platform', 'score_performance', 'genes', 'transcripts', 'proteins', 'metabolites', #'efos',
                    'variants_interactions', 'variants_genomebuild', 'date_release')
        fields = meta_fields
        read_only_fields = meta_fields

    def get_date_released(self, obj):
        return obj.date_released


class OmicsScoreSerializer(serializers.ModelSerializer):
    publication = PublicationSerializer(many=False, read_only=True)
    platform = PlatformSerializer(many=False, read_only=True)

    metabolites = MetaboliteSerializer(many=True, read_only=True)
    score_performance = PerformanceLightSerializer(many=True, read_only=True)

    class Meta:
        model = Score
        meta_fields = ('id', 'name', 'trait_reported', 'trait_additional', 'method_name', 'method_params',
                    'trait_reported', 'trait_additional', 'method_name', 'method_params', 'variants_number',
                    'publication', 'platform', 'score_performance',
                    'variants_interactions', 'variants_genomebuild')
        fields = meta_fields
        read_only_fields = meta_fields


class MetaboliteScoreSerializer(OmicsScoreSerializer):
    metabolites = MetaboliteSerializer(many=True, read_only=True)

    class Meta(OmicsScoreSerializer):
        meta_fields = ('metabolites',)
        fields = OmicsScoreSerializer.Meta.fields + meta_fields
        read_only_fields = OmicsScoreSerializer.Meta.read_only_fields + meta_fields


class ProteinScoreSerializer(OmicsScoreSerializer):
    genes = GeneSerializer(many=True, read_only=True)
    proteins = ProteinSerializer(many=True, read_only=True)

    class Meta(OmicsScoreSerializer):
        meta_fields = ('genes', 'proteins')
        fields = OmicsScoreSerializer.Meta.fields + meta_fields
        read_only_fields = OmicsScoreSerializer.Meta.read_only_fields + meta_fields


class TranscriptScoreSerializer(OmicsScoreSerializer):
    genes = GeneSerializer(many=True, read_only=True)

    class Meta(OmicsScoreSerializer):
        meta_fields = ('genes',) # transcripts
        fields = OmicsScoreSerializer.Meta.fields + meta_fields
        read_only_fields = OmicsScoreSerializer.Meta.read_only_fields + meta_fields


# class OmicsPlotSerializer(serializers.ModelSerializer):
#     platform = PlatformSerializer(many=False, read_only=True)
#     score_performance = PerformanceLightSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Score
#         meta_fields = ('platform', 'score_performance')
#         fields = meta_fields
#         read_only_fields = meta_fields
class OmicsPlotSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(many=False, read_only=True)
    sample = SampleSerializer(many=False, read_only=True)

    class Meta:
        model = Performance
        meta_fields = ('score_id', 'platform', 'sample', 'performance_metrics')
        fields = meta_fields
        read_only_fields = meta_fields

#### Table ####

class MetaboliteLightSerializer(serializers.ModelSerializer):
    pathway_group = serializers.SerializerMethodField()
    pathway_subgroup = serializers.SerializerMethodField()
    class Meta:
        model = Metabolite
        meta_fields = ('name','external_id','pathway_group','pathway_subgroup')
        fields = meta_fields
        read_only_fields = meta_fields

    def get_pathway_group(self, obj):
        if obj.pathway_group:
            return obj.pathway_group.name
        else:
            return None

    def get_pathway_subgroup(self, obj):
        if obj.pathway_subgroup:
            return obj.pathway_subgroup.name
        else:
            return None


class ProteinLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protein
        meta_fields = ('name','external_id')
        fields = meta_fields
        read_only_fields = meta_fields


class GeneLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gene
        meta_fields = ('name','external_id')
        fields = meta_fields
        read_only_fields = meta_fields

# class PerformanceTestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Performance
#         # meta_fields = ('score', 'score__metabolites', 'cohort_metrics')
#         meta_fields = ('cohort_metrics',)
#         fields = meta_fields
#         read_only_fields = meta_fields


class ScoreMetaboliteSerializer(serializers.ModelSerializer):
    metabolites = MetaboliteLightSerializer(many=True, read_only=True)
    class Meta:
        model = Score
        meta_fields = ('id','variants_number','metabolites','performance_data')
        fields = meta_fields
        read_only_fields = meta_fields


class ScoreProteinSerializer(serializers.ModelSerializer):
    proteins = ProteinLightSerializer(many=True, read_only=True)
    genes = GeneLightSerializer(many=True, read_only=True)
    class Meta:
        model = Score
        meta_fields = ('id','variants_number','proteins','genes','performance_data')
        fields = meta_fields
        read_only_fields = meta_fields


class ScoreTranscriptSerializer(serializers.ModelSerializer):
    genes = GeneLightSerializer(many=True, read_only=True)
    class Meta:
        model = Score
        meta_fields = ('id','variants_number','genes','performance_data')
        fields = meta_fields
        read_only_fields = meta_fields

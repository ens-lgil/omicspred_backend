from rest_framework import serializers
from catalog.models import *


class CohortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cohort
        meta_fields = ('name_short', 'name_full', 'name_others','url')
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
        meta_fields = ('sample_number', 'sample_percent_male', 'sample_age',
                    'ancestry_broad', 'ancestry_free', 'ancestry_country', 'ancestry_additional',
                    'source_gwas', 'source_pmid','source_doi', 'cohorts', 'cohorts_additional')
        fields = meta_fields
        read_only_fields = meta_fields


class MetricSerializer(serializers.ModelSerializer):

    class Meta:
        model = Metric
        meta_fields = ('name', 'name_short', 'performance_type', 'estimate')
        fields = meta_fields
        read_only_fields = meta_fields


class PublicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publication
        meta_fields = ('id', 'title', 'doi', 'pmid', 'journal', 'firstauthor', 'date_publication')
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
    class Meta:
        model = Platform
        meta_fields = ('name', 'version', 'technic', 'type')
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

    gene = GeneSerializer(many=True, read_only=True)
    transcript = TranscriptSerializer(many=True, read_only=True)
    protein = ProteinSerializer(many=True, read_only=True)
    metabolite = MetaboliteSerializer(many=True, read_only=True)

    date_release = serializers.SerializerMethodField('get_date_released')

    class Meta:
        model = Score
        meta_fields = ('id', 'name', 'trait_reported', 'trait_additional', 'method_name', 'method_params',
                    'trait_reported', 'trait_additional', 'method_name', 'method_params', 'variants_number',
                    'publication', 'platform', 'gene', 'transcript', 'protein', 'metabolite',
                    'variants_interactions', 'variants_genomebuild', 'date_release')
        fields = meta_fields
        read_only_fields = meta_fields

    def get_date_released(self, obj):
        return obj.date_released


class PerformanceSerializer(serializers.ModelSerializer):
    phenotype_efo = EFOTraitSerializer(many=True, read_only=True)
    publication = PublicationSerializer(many=False, read_only=True)
    sample = SampleSerializer(many=False, read_only=True)

    class Meta:
        model = Performance
        meta_fields = ('id', 'associated_pgs_id', 'publication', 'sample',
                'eval_type', 'performance_metrics', 'performance_additional')
        fields = meta_fields
        read_only_fields = meta_fields

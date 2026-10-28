from django.test import TestCase

from imports.omicspred.parsers.metadata import MetadataTemplate
from imports.tests.config import *
from omicspred.models import *
from search_es.documents import score


class ImportMetadataTest(TestCase):
    """Metadata import tests."""

    # Keep the expected values close to the real fixture data.
    data_counts = {
        "cohort": 2,
        "dataset": 5,
        "metric": 2,
        "performance": 12,
        "platform": 5,
        "sample": 11,
        "sample_performance": 6,
        "score_dataset": 2,
        "score_performance": 2,
        "score": 6,
    }

    expected_score = {
        "name": "genetic_score_e_selectine",
        "trait_reported": "E-selectin",
        "trait_reported_id": "P16581",
        "method_name": "Bayesian Ridge regression",
        "method_params": "LD/SNP r2 threshold",
        "variants_genomebuild": "GRCh38",
        "variants_number": 121,
    }

    expected_platform = {
        "name": "Olink",
        "version": "Explore",
    }

    expected_tissue = {
        "id": "UBERON_0001969",
        "label": "blood plasma",
    }

    expected_gene = {
        "external_id": "ENSG00000113303",
        "name": "BTNL8",
    }

    expected_protein = {
        "external_id": "P16581",
        "name": "E-selectin",
    }

    expected_sample = {
        "sample_number": 1856,
        "sample_percent_male": 45.1,
        "sample_age": 52.5,
        "sample_age_sd": 6.4,
        "ancestry_broad": "European",
        "ancestry_free": "Finnish",
        "ancestry_country": "UK",
    }

    expected_cohort = {
        "name_short": "UKB",
        "name_full": "UK Biobank",
        "url": "https://www.ukbiobank.ac.uk/",
    }

    expected_performance_parser = {
        "eval_type": "External Validation",
        "covariates": "40 PEER Factors; sex; age",
    }

    expected_performance_import = {
        "eval_type": "EV",
        "covariates": "40 PEER Factors; sex; age",
    }

    expected_metric_r2 = {
        "type": "Pearson's correlation",
        "estimate": 0.48,
        "name": "Proportion of the variance explained",
        "name_short": "R2",
        "pvalue": 2.56e-75,
    }

    expected_metric_rho = {
        "type": "Spearman's rank correlation",
        "estimate": 0.66,
        "name": "Spearman correlation coefficient",
        "name_short": "Rho",
    }

    pmid = 36991119

    @classmethod
    def setUpTestData(cls):
        cls.metadata_template = MetadataTemplate(file_loc, platform_types, license, species)
        cls.metadata_template.read_curation(dataset_prefix)

    def assert_record_matches(self, record, expected):
        for key, expected_value in expected.items():
            if isinstance(expected_value, float):
                self.assertEqual(float(getattr(record, key)), float(expected_value))
            else:
                self.assertEqual(getattr(record, key), expected_value)

    def assert_dict_matches(self, payload, expected):
        for key, expected_value in expected.items():
            if isinstance(expected_value, float):
                self.assertEqual(float(payload[key]), float(expected_value))
            else:
                self.assertEqual(payload[key], expected_value)

    def get_score_by_name(self, name):
        scores = self.metadata_template.parsed_scores
        try:
            return next(score for score in scores.values() if score.data["name"] == name)
        except StopIteration:
            self.fail(f"Score not found: {name}")

    def get_dataset_by_platform(self, platform_name):
        datasets = self.metadata_template.parsed_datasets
        try:
            return next(dataset for dataset in datasets.values() if dataset.platform.name == platform_name)
        except StopIteration:
            self.fail(f"Dataset for platform {platform_name} not found")

    def get_score_sample_performance(self, score_name):
        sample_performance = self.metadata_template.parsed_sample_performance
        if score_name not in sample_performance:
            self.fail(f"score_name {score_name} not found in parsed_sample_performance")
        return sample_performance[score_name]

    def get_performance_by_eval_type(self, score_model, eval_type):
        performances = score_model.score_performance.all()
        try:
            return next(perf for perf in performances if perf.eval_type == eval_type)
        except StopIteration:
            self.fail(f"Performance {eval_type} not found for score {score_model.name}")

    # ------------------------------------------------------------------
    # Parser tests
    # ------------------------------------------------------------------

    def test_read_curation_parses_species_and_publication(self):
        print("> TEST: Import parsing of species and publication")
        self.assertEqual(self.metadata_template.species.name_latin, species)

        publication = self.metadata_template.parsed_publication
        self.assertIsNotNone(publication)
        self.assertEqual(publication.pmid, self.pmid)

    def test_read_curation_parses_scores(self):
        print("> TEST: Import parsing of scores")
        scores = self.metadata_template.parsed_scores
        self.assertEqual(len(scores), self.data_counts["score"])

        score = self.get_score_by_name(self.expected_score["name"])
        self.assert_dict_matches(score.data, self.expected_score)

        protein = score.additional_data["proteins"][0]
        self.assertEqual(protein.external_id, self.expected_protein["external_id"])
        self.assertEqual(protein.name, self.expected_protein["name"])

    def test_read_curation_parses_cohorts_and_datasets(self):
        print("> TEST: Import parsing of cohorts and datasets")
        cohorts = self.metadata_template.parsed_cohorts
        self.assertEqual(len(cohorts), self.data_counts["cohort"])

        cohort = next(
            cohort for cohort in cohorts.values()
            if cohort.name_short == self.expected_cohort["name_short"]
        )
        self.assert_dict_matches(cohort.data, self.expected_cohort)

        datasets = self.metadata_template.parsed_datasets
        self.assertEqual(len(datasets), self.data_counts["dataset"])

        dataset = self.get_dataset_by_platform("Olink")
        self.assert_dict_matches(dataset.tissue.data, self.expected_tissue)
        self.assert_dict_matches(dataset.platform.data, self.expected_platform)

    def test_read_curation_parses_samples_and_performance(self):
        print("> TEST: Import parsing of samples and performance metrics")
        score_name = self.expected_score["name"]
        sample_performances = self.get_score_sample_performance(score_name)
        self.assertEqual(len(sample_performances), self.data_counts["score_performance"])

        sample_performance = next(
            item for item in sample_performances
            if item["sample"].data["sample_number"] == self.expected_sample["sample_number"]
        )

        sample = sample_performance["sample"]
        self.assert_dict_matches(sample.data, self.expected_sample)

        self.assertEqual(sample.data["cohorts"][0].name_short, self.expected_cohort["name_short"])

        performance = sample_performance["performance"]
        self.assert_dict_matches(performance.data, self.expected_performance_parser)

        metrics = performance.metrics
        self.assertEqual(len(metrics), self.data_counts["metric"])

        metric_r2 = next(metric for metric in metrics if metric.name == "R2")
        metric_rho = next(metric for metric in metrics if metric.name == "Rho")

        self.assert_dict_matches(metric_r2.data, self.expected_metric_r2)
        self.assert_dict_matches(metric_rho.data, self.expected_metric_rho)

    # ------------------------------------------------------------------
    # Import tests
    # ------------------------------------------------------------------

    def test_import_curation_creates_expected_models(self):
        print("> TEST: Import creates expected models")
        self.metadata_template.import_curation()

        species_model = Species.objects.get(name_latin=species)
        self.assertIsInstance(species_model, Species)

        publication_model = Publication.objects.get(pmid=self.pmid)
        self.assertIsInstance(publication_model, Publication)

        score_count = Score.objects.count()
        self.assertEqual(score_count, self.data_counts["score"])

        score_model = Score.objects.get(name=self.expected_score["name"])
        self.assertIsInstance(score_model, Score)
        self.assert_record_matches(score_model, self.expected_score)

        gene_model = Gene.objects.get(name=self.expected_gene["name"])
        self.assertIsInstance(gene_model, Gene)
        self.assert_record_matches(gene_model, self.expected_gene)

        cohort_count = Cohort.objects.count()
        self.assertEqual(cohort_count, self.data_counts["cohort"])

        cohort_model = Cohort.objects.get(name_short=self.expected_cohort["name_short"])
        self.assert_record_matches(cohort_model, self.expected_cohort)

        platform_count = Platform.objects.count()
        self.assertEqual(platform_count, self.data_counts["platform"])

        platform_model = Platform.objects.get(
            name=self.expected_platform["name"],
            version=self.expected_platform["version"],
        )
        self.assertIsInstance(platform_model, Platform)

        tissue_model = Tissue.objects.get(id=self.expected_tissue["id"])
        self.assertIsInstance(tissue_model, Tissue)
        self.assert_record_matches(tissue_model, self.expected_tissue)

        dataset_count = Dataset.objects.count()
        self.assertEqual(dataset_count, self.data_counts["dataset"])

        dataset_model = Dataset.objects.get(
            platform=platform_model,
            publication=publication_model,
            tissue=tissue_model,
            license=license,
        )
        self.assertIsInstance(dataset_model, Dataset)
        self.assertEqual(Score.objects.filter(dataset=dataset_model).count(), self.data_counts["score_dataset"])

        sample_count = Sample.objects.count()
        self.assertEqual(sample_count, self.data_counts["sample"])

        sample_model = Sample.objects.get(
            sample_number=self.expected_sample["sample_number"],
            sample_age_sd=self.expected_sample["sample_age_sd"],
        )
        self.assertIsInstance(sample_model, Sample)
        self.assert_record_matches(sample_model, self.expected_sample)
        self.assertEqual(sample_model.cohorts.first(), cohort_model)

        performance_count = Performance.objects.count()
        self.assertEqual(performance_count, self.data_counts["performance"])

        performance_model = self.get_performance_by_eval_type(score_model, self.expected_performance_import["eval_type"])
        self.assertIsInstance(performance_model, Performance)
        self.assert_record_matches(performance_model, self.expected_performance_import)

        metric_models = performance_model.performance_metric.all()
        self.assertEqual(len(metric_models), self.data_counts["metric"])

        metric_r2 = next(metric for metric in metric_models if metric.name_short == "R2")
        metric_rho = next(metric for metric in metric_models if metric.name_short == "Rho")

        self.assert_record_matches(metric_r2, self.expected_metric_r2)
        self.assert_record_matches(metric_rho, self.expected_metric_rho)

    # def test_import_curation_is_idempotent(self):
    #     self.metadata_template.import_curation()
    #     self.metadata_template.import_curation()

    #     self.assertEqual(Score.objects.count(), self.data_counts["score"])
    #     self.assertEqual(Cohort.objects.count(), self.data_counts["cohort"])
    #     self.assertEqual(Dataset.objects.count(), self.data_counts["dataset"])
    #     self.assertEqual(Sample.objects.count(), self.data_counts["sample"])
    #     self.assertEqual(Performance.objects.count(), self.data_counts["performance"])
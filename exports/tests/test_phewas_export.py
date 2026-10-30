import csv
import gzip
import os
import tempfile
from django.test import TestCase
from omicspred.models import Dataset, ScorePheWAS
from exports.phewas_export import PheWASExport


class ExportPheWASTest(TestCase):
    """Regression tests for the PheWAS export."""

    fixtures = ["db_test"]
    databases = {"default"}

    @staticmethod
    def read_gzip_tsv(path):
        with gzip.open(path, "rt", newline="") as fh:
            return list(csv.DictReader(fh, delimiter="\t"))

    def test_phewas_export_generates_expected_columns_and_counts(self):
        print('> Test PheWAS export generates expected columns and counts')
        dataset = Dataset.objects.filter(num__in=[1, 3]).order_by("num").first()
        filename = f"{dataset.id}_phewas.txt"
        output_dir = tempfile.mkdtemp(prefix="phewas_")
        filepath = os.path.join(output_dir, f"{filename}.gz")

        exporter = PheWASExport(filename, output_dir, dataset)
        exporter.generate_export()

        self.assertTrue(os.path.isfile(filepath))
        self.assertGreater(os.path.getsize(filepath), 0)

        rows = self.read_gzip_tsv(filepath)
        self.assertGreater(len(rows), 0)

        required_cols = {
            "omicspred_id",
            "phenotype_ids",
            "phenotype_labels",
            "method_description",
            "phewas_publication_id",
            "sample_number",
            "cohorts",
            "effect_size",
            "p-value",
            "adjusted_p-value",
        }

        self.assertTrue(required_cols.issubset(set(rows[0].keys())))

        expected_rows = ScorePheWAS.objects.filter(dataset_id=dataset.num).count()
        self.assertEqual(len(rows), expected_rows)

        for row in rows:
            for key in required_cols:
                self.assertIn(key, row)
                self.assertIsNotNone(row[key])
                self.assertNotEqual(row[key], "")

    # def test_phewas_export_handles_empty_queryset(self):
    #     print('> Test PheWAS export handles empty queryset')
    #     dataset = Dataset.objects.filter(num=9999).first()
    #     if dataset is None:
    #         self.skipTest("No dataset with num=9999 in test fixtures")

    #     filename = f"{dataset.id}_phewas.txt"
    #     output_dir = tempfile.mkdtemp(prefix="phewas_empty_")
    #     filepath = os.path.join(output_dir, f"{filename}.gz")

    #     exporter = PheWASExport(filename, output_dir, dataset)
    #     exporter.generate_export()

    #     self.assertTrue(os.path.isfile(filepath))
    #     rows = self.read_gzip_tsv(filepath)
    #     self.assertEqual(rows, [])

    # def test_phewas_export_uses_valid_gzip_format(self):
    #     print('> Test PheWAS export uses valid gzip format')
    #     dataset = Dataset.objects.filter(num__in=[1, 3]).order_by("num").first()
    #     filename = f"{dataset.id}_phewas.txt"
    #     output_dir = tempfile.mkdtemp(prefix="phewas_gzip_")
    #     filepath = os.path.join(output_dir, f"{filename}.gz")

    #     exporter = PheWASExport(filename, output_dir, dataset)
    #     exporter.generate_export()

    #     with gzip.open(filepath, "rt", newline="") as fh:
    #         reader = csv.reader(fh, delimiter="\t")
    #         header = next(reader)
    #         self.assertTrue(header)
    #         self.assertIn("omicspred_id", header)

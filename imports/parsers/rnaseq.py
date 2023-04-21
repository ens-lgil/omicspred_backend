import pandas as pd
from imports.models.score import ScoreData
from imports.models.performance import PerformanceData
from imports.models.omics import GeneData
from omicspred.models import Platform



class RNAseqParser():

    def __init__(self, data_info:dict):
        self.study = data_info['name']
        self.filepath = data_info['filepath']
        self.platform = data_info['platform']
        self.omicstype = data_info['type']
        self.samples = data_info['samples_info']
        self.publication = data_info['publication']
        self.genomebuild = data_info['genomebuild']


    def parse_performance_metric(self,score,data_values,cohort_name,ancestry,type):
        ''' Parse performance and metric data '''
        sample = None
        extra = None
        performance_model = None

        for sample_info in self.samples:
            if sample_info['cohort'] == cohort_name and sample_info['ancestry'] == ancestry:
                sample = sample_info['sample']
                extra = sample_info['entities_count']+' genes'
        if sample:
            performance_data = PerformanceData(score,self.publication,sample,type,extra)
            performance_data.add_metric(data_values)
            performance_model = performance_data.create_model()

        return performance_model


    def parse_data(self):
        df = pd.read_csv(self.filepath)
        for index, row in df.iterrows():
            # Gene info
            gene_id = row['Ensembl ID']
            gene_name = row['Gene']
            # Score info
            score_id = row['OMICSPRED ID']
            variants_number = row['#SNP']

            print(f"- {score_id} | {gene_id}")

            # Gene model
            gene_data = GeneData(external_id=gene_id,name=gene_name)
            gene_model = gene_data.create_model()

            # Score model
            score_data = ScoreData(score_id,variants_number,self.publication,self.platform,self.genomebuild)
            score_model = score_data.create_model()
            score_model.save()
            score_model.gene.add(gene_model)
            score_model.save()

            # Performance & Metric models
            # - Training
            training_values = {
                'R2': row['Internal_R2'],
                'R2_pvalue': row['Internal_R2_pvalue'],
                'Rho': row['Internal_Rho'],
                'Rho_pvalue': row['Internal_Rho_pvalue']
            }
            self.parse_performance_metric(score_model,training_values,'Internal','European','T')
            # - Validations
            cohort_info = {
                'INTERVAL_Withheld_Set': {'name': 'INTERVAL withheld subset', 'ancestry': 'European', 'vtype': 'IV'},
            }
            for cohort in cohort_info.keys():
                validation_values = {
                    'R2': row[f'{cohort}_R2'],
                    'R2_pvalue': row[f'{cohort}_R2_pvalue'],
                    'Rho': row[f'{cohort}_Rho'],
                    'Rho_pvalue': row[f'{cohort}_Rho_pvalue'],
                    'MissingRate': row[f'{cohort}_MissingRate']
                }
                cohort_entry = cohort_info[cohort]
                self.parse_performance_metric(score_model,validation_values,cohort_entry['name'],cohort_entry['ancestry'],cohort_entry['vtype'])

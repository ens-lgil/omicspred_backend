import pandas as pd
import numpy as np
from imports.models.score import ScoreData
from imports.models.performance import PerformanceData
from imports.models.omics import GeneData, ProteinData, MetaboliteData, PathwayData
from omicspred.models import Platform



class MetaboliteParser():

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

        # Nightingale
        meta_name_col = 'Biomarker Name'
        meta_gp_col = 'Group'
        meta_subgp_col = 'Subgroup'
        # Metabolonx
        if self.platform.name == 'Metabolon':
            meta_name_col = 'Biochemical Name'
            meta_gp_col = 'Super Pathway'
            meta_subgp_col = 'Sub Pathway'

        for index, row in df.iterrows():
            # Metabolite info
            metabolite_id = None
            if 'Metabolon ID' in row:
                metabolite_id = row['Metabolon ID']
            metabolite_name = row[meta_name_col]

            # Pathway info
            pathway = row[meta_gp_col]
            subpathway = row[meta_gp_col]

            # Score info
            score_id = row['OMICSPRED ID']
            variants_number = row['#SNP']

            print(f"- {score_id} | {metabolite_name}")

            # Pathway model
            pathway_model = None
            if pathway:
                pathway_data = PathwayData(name=pathway)
                pathway_model = pathway_data.create_model()

            # Subpathway model
            subpathway_model = None
            if subpathway:
                subpathway_data = PathwayData(name=subpathway)
                subpathway_model = subpathway_data.create_model()

            # Metabolite model
            metabolite_data = MetaboliteData(
                name = metabolite_name,
                external_id = metabolite_id,
                pathway_group = pathway_model,
                pathway_subgroup = subpathway_model
            )
            metabolite_model = metabolite_data.create_model()


            # Score model
            score_data = ScoreData(score_id,variants_number,self.publication,self.platform,self.genomebuild)
            score_model = score_data.create_model()
            score_model.save()
            score_model.metabolite.add(metabolite_model)
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
            cohort_info = {}
            if self.platform.name == 'Nightingale':
                cohort_info = {
                    'UKB': {'name': 'UKB', 'ancestry': 'European', 'vtype': 'EV'},
                    'ORCADES': {'name': 'ORCADES', 'ancestry': 'European', 'vtype': 'EV'},
                    'VIKING': {'name': 'VIKING', 'ancestry': 'European', 'vtype': 'EV'},
                    'MEC_CN': {'name': 'MEC', 'ancestry': 'East Asian', 'vtype': 'EV'},
                    'MEC_IN': {'name': 'MEC', 'ancestry': 'South Asian', 'vtype': 'EV'},
                    'MEC_MA': {'name': 'MEC', 'ancestry': 'Additional Asian Ancestries', 'vtype': 'EV'}
                }
            elif self.platform.name == 'Metabolon':
                cohort_info = {
                    'INTERVAL_Withheld_Set': {'name': 'INTERVAL withheld subset', 'ancestry': 'European', 'vtype': 'IV'},
                    'ORCADES': {'name': 'ORCADES', 'ancestry': 'European', 'vtype': 'EV'}
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

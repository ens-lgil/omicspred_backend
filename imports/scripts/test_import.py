from imports.parsers.summary import SummaryParser
from imports.parsers.rnaseq import RNAseqParser
from imports.parsers.protein import ProteinParser
from imports.parsers.metabolite import MetaboliteParser
from omicspred.models import Publication, Platform


genomebuild = 'GRCh38'

def add_publication():

    pmid = 36991119
    try:
        publication = Publication.objects.get(pmid=pmid)
    except Publication.DoesNotExist:
        publication = Publication()
        publication.pmid = 36991119
        publication.doi = '10.1038/s41586-023-05844-9'
        publication.firstauthor = 'Xu Y'
        publication.authors = 'Xu Y, Ritchie SC, Liang Y, Timmers PRHJ, Pietzner M, Lannelongue L, Lambert SA, Tahir UA, May-Wilson S, Foguet C, Johansson Å, Surendran P, Nath AP, Persyn E, Peters JE, Oliver-Williams C, Deng S, Prins B, Luan J, Bomba L, Soranzo N, Di Angelantonio E, Pirastu N, Tai ES, van Dam RM, Parkinson H, Davenport EE, Paul DS, Yau C, Gerszten RE, Mälarstig A, Danesh J, Sim X, Langenberg C, Wilson JF, Butterworth AS, Inouye M.'
        publication.journal = 'Nature'
        publication.title = 'An atlas of genetic scores to predict multi-omic traits.'
        publication.date_publication = '2023-03-29'
        publication.save()
    return publication


def add_platform(platform_name,platform_type):
    try:
        platform = Platform.objects.get(name__iexact=platform_name, type__iexact=platform_type)
    except Platform.DoesNotExist:
        platform = Platform()
        platform.name = platform_name
        platform.type = platform_type
        platform.save()
    return platform

def run():


    path = '/Users/lg10/Workspace/git/clone/OmicsPred/src/data'

    studies = [
        'Proteomics_Somalogic',
        'Proteomics_Olink',
        'Metabolomics_Nightingale',
        'Metabolomics_Metabolon',
        'Transcriptomics_Illumina_RNAseq'
    ]

    publication = add_publication()

    for study in studies:
        print(f'\n\n##### {study} #####\n')
        # Summary
        summary_info = { 'name': study, 'filepath': f'{path}/{study}/sumarry.json'}
        summary = SummaryParser(summary_info)
        summary.parse_summary_file()
        samples_info = summary.import_to_database()

        # Data
        platform = study.split('_',1)[1]
        filename = study.split('_')[-1]
        type = study.split('_')[0]
        platform_model = add_platform(platform.replace('_',' '),type)
        data_info = {
            'name': study,
            'type': type,
            'platform': platform_model,
            'filepath': f'{path}/paper_data/{filename}.csv',
            'samples_info': samples_info,
            'publication': publication,
            'genomebuild': genomebuild
        }
        if study.startswith('Transcriptomics'):
            rnaseq = RNAseqParser(data_info)
            rnaseq.parse_data()
        elif study.startswith('Proteomics'):
            protein = ProteinParser(data_info)
            protein.parse_data()
        elif study.startswith('Metabolomics'):
            metabolite = MetaboliteParser(data_info)
            metabolite.parse_data()

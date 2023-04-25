from imports.parsers.summary import SummaryParser
from imports.parsers.rnaseq import RNAseqParser
from imports.parsers.protein import ProteinParser
from imports.parsers.metabolite import MetaboliteParser
from omicspred.models import Publication, Platform


genomebuild = 'GRCh37'

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


def add_platform(platform_name,platform_type,extra_data):
    try:
        platform = Platform.objects.get(name__iexact=platform_name, type__iexact=platform_type)
    except Platform.DoesNotExist:
        platform = Platform()
        platform.name = platform_name
        platform.type = platform_type
        if 'version' in extra_data.keys():
            platform.version = extra_data['version']
        if 'full_name' in extra_data.keys():
            platform.full_name = extra_data['full_name']
        if 'technic' in extra_data.keys():
            platform.technic = extra_data['technic']
        platform.save()
    return platform

def run():

    path = '/Users/lg10/Workspace/git/clone/OmicsPred/src/data'

    method_name = 'Bayesian Ridge regression'

    studies = {
        'Proteomics_Somalogic': {
            'tissue': {
                'id': 'UBERON_0001969',
                'label': 'blood plasma',
                'description': 'The liquid component of blood, in which erythrocytes are suspended.',
                'url': 'http://purl.obolibrary.org/obo/UBERON_0001969',
                'type': 'tissue'
            },
            'version': '3.0',
            'method_name': method_name,
            'technic': 'aptamer-based multiplex protein assay'
        },
        'Proteomics_Olink': {
            'tissue': {
                'id': 'UBERON_0001969',
                'label': 'blood plasma',
                'description': 'The liquid component of blood, in which erythrocytes are suspended.',
                'url': 'http://purl.obolibrary.org/obo/UBERON_0001969',
                'type': 'tissue'
            },
            'method_name': method_name,
            'full_name': 'Olink Target',
            'technic': 'antibody-based proximity extension assay for proteins'
        },
        'Metabolomics_Nightingale': {
            'tissue': {
                'id': 'BTO_0000133',
                'label': 'blood serum',
                'description': 'The cell-free portion of the blood from which the fibrinogen has been separated in the process of clotting.',
                'url': 'http://purl.obolibrary.org/obo/BTO_0000133',
                'type': 'tissue'
            },
            'method_name': method_name,
            'technic': 'proton nuclear magnetic resonance (NMR) spectroscopy platform'
        },
        'Metabolomics_Metabolon': {
            'tissue': {
                'id': 'UBERON_0001969',
                'label': 'blood plasma',
                'description': 'The liquid component of blood, in which erythrocytes are suspended.',
                'url': 'http://purl.obolibrary.org/obo/UBERON_0001969',
                'type': 'tissue'
            },
            'method_name': method_name,
            'full_name': 'Metabolon HD4',
            'technic': 'untargeted mass spectrometry metabolomics platform'
        },
        'Transcriptomics_Illumina_RNAseq': {
            'tissue': {
                'id': 'UBERON_0000178',
                'label': 'blood',
                'description': 'A fluid that is composed of blood plasma and erythrocytes.',
                'url': 'http://purl.obolibrary.org/obo/UBERON_0000178',
                'type': 'tissue'
            },
            'method_name': method_name,
            'full_name': 'Illumina NovaSeq 6000'
        }
    }

    publication = add_publication()

    for study in studies.keys():
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
        platform_model = add_platform(platform.replace('_',' '),type, studies[study])
        data_info = {
            'name': study,
            'study_info': studies[study],
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

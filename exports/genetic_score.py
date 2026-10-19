from omicspred.models import Score,Dataset


def generate_scoring_file_header(score:Score, dataset:Dataset):
    ''' Generate a scoring file header '''
    # Setup 'trait_reported'
    reported_trait = ''
    if score.trait_reported and score.trait_reported_id:
        reported_trait = f'{score.trait_reported} ({score.trait_reported_id})'
    elif score.trait_reported:
            reported_trait = score.trait_reported
    else:
        reported_trait = score.trait_reported_id

    trait_type = dataset.platform.platform_master.type

    publication_model = dataset.publication

    # Setup 'trait_mapped'
    molecular_traits = []
    trait_mapped = set()
    match trait_type:
        case 'Proteomics':
            molecular_traits = score.proteins.all()
        case 'Transcriptomics':
            molecular_traits = score.genes.all()
        case 'Metabolomics':
            molecular_traits = score.metabolites.all()
        case _:
            print("Can't find a valid platform type.")  # Default case
            exit()
    for mt in molecular_traits:
        if mt.name and mt.external_id:
            trait_mapped.add(f'{mt.name} ({mt.external_id})')
        elif mt.name:
            trait_mapped.add(mt.name)
        elif mt.external_id:
            trait_mapped.add(mt.external_id)

    # Setup 'note'
    score_note = ''
    if score.comment:
        score_note = f'\n#note={score.comment}'

    platform_version = f' ({dataset.platform.version})' if dataset.platform.version else ''
    return f'''###GENETIC SCORING FILE - see https://www.pgscatalog.org/downloads/#dl_ftp_scoring for additional information
#format_version=2.0
##GENETIC SCORE (OPGS) INFORMATION
#omicspred_id={score.id}
#pgs_name={score.name}
#trait_type={trait_type}
#measurement_tissue={dataset.tissue.label} ({dataset.tissue.id})
#measurement_platform={dataset.platform.name}{platform_version}
#trait_mapped={'|'.join(sorted(trait_mapped))}
#trait_reported={reported_trait}
#genome_build={score.variants_genomebuild}
#variants_number={score.variants_number}{score_note}
##SOURCE INFORMATION
#pgp_id={publication_model.id}
#citation={publication_model.firstauthor} et al. {publication_model.journal} ({publication_model.pub_year}). doi:{publication_model.doi}
#license={score.license}'''
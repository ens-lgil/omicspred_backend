from omicspred.models import Performance, Sample, Cohort


def run():
    performances = Performance.objects.defer('score','publication','platform','efo').select_related('sample').all().prefetch_related('sample__cohorts')

    ancestries = {
        'East Asian': 'CN',
        'South Asian': 'IN',
        'Additional Asian Ancestries': 'MA'
    }

    for perf in performances:

        cohorts = [x.name_short for x in perf.sample.cohorts.all()]
        cohort_label = '_'.join(sorted(cohorts))
        if cohort_label == 'MEC':
            sample_anc = perf.sample.ancestry_broad
            if sample_anc in ancestries.keys():
                cohort_label = f'{cohort_label}-{ancestries[sample_anc]}'
        perf.cohort_label = cohort_label
        perf.save()
        print(f"PERF {perf.id}: {cohort_label} / {perf.cohort_label}")

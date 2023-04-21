from django.db import IntegrityError, transaction
from imports.models.generic import GenericData
from imports.models.metric import MetricData
from omicspred.models import Performance

class PerformanceData(GenericData):

    def __init__(self,score,publication,sample,type,extra=None):
        GenericData.__init__(self)
        self.metrics = []
        # self.metric_models = []
        self.data = {
            'score': score,
            'publication': publication,
            'sample': sample,
            'eval_type': type
        }
        if extra:
            self.data['performance_additional'] = extra


    def add_metric(self,metric_values):
        '''
        Method creating MetricData objects and add them to the metrics array.
        '''
        for metric_type in metric_values.keys():
            metric_data = MetricData(metric_type,metric_values[metric_type])
            self.metrics.append(metric_data)


    @transaction.atomic
    def create_model(self):
        '''
        Create an instance of the Performance model.
        Return type: Performance model
        '''
        try:
            with transaction.atomic():
                self.model = Performance()
                for field, val in self.data.items():
                    setattr(self.model, field, val)
                self.model.save()

            # Create associated Metric objects
            for metric in self.metrics:
                metric_model = metric.create_model(self.model)
                #self.metric_models.append(metric_model)

        except IntegrityError as e:
            self.model = None
            self.parsing_report_error_import(e)
            print('Error with the creation of the Performance(s) and/or the Metric(s)')

        return self.model

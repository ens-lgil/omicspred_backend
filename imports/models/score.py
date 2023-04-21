from django.db import IntegrityError, transaction
from imports.models.generic import GenericData
from omicspred.models import Score


class ScoreData(GenericData):

    def __init__(self,score_id,variants_number,publication,platform,genomebuild,score_name=None):
        GenericData.__init__(self)
        num = score_id.replace('OPGS','').lstrip('0')
        self.data = {
            'num': int(num),
            'id': score_id,
            'variants_number': variants_number,
            'publication': publication,
            'platform': platform,
            'variants_genomebuild': genomebuild
        }
        if score_name:
            self.data['name'] = score_name


    @transaction.atomic
    def create_model(self):
        '''
        Create an instance of the Score model.
        Return type: Score model
        '''
        try:
            with transaction.atomic():
                self.model = Score()
                for field, val in self.data.items():
                    setattr(self.model, field, val)
                self.model.save()

        except IntegrityError as e:
            self.model = None
            print(f'Error with the creation of the Score(s): {e}')
        return self.model

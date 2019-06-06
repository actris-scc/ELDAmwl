from ELDAmwl.base import Params


class BackscatterParams(Params):

    def __init__(self):
        self.sub_params = ['general_params',
                            'backscatter_params']
        self.general_params = None
        self.extinction_params = None

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params
        # extinction_params.from_db()
        return result

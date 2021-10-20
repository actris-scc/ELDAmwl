from copy import deepcopy

import zope

from ELDAmwl.bases.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.component.interface import IMonteCarlo, IExtOp
from ELDAmwl.component.registry import registry
import numpy as np


class MonteCarlo:
    """
    Implementation of monte carlo algorithm
    """

    sample_results = None
    sample_input = None

    def __init__(self, op):
        self.op = op

    def get_sample_input(self, orig):
        mc_generator = CreateMCCopies()


    def get_sample_results(self):
        results = []
        for i in range(self.mc_params.nb_of_iterations):
            sample = self.op.run(data=self.sample_input[i])
            results.append(sample.data)

            return np.array(results)

    def calc_mc_error(self):
        all = np.concatenate(self.sample_results,
                             axis=0)
        return np.nanstd(all)

    def __call__(self, mc_params):
        self.mc_params = mc_params
        orig_data = self.get_data()

        self.get_sample_inputs(orig_data)
        self.get_sample_results()

        return self.calc_mc_error()


@zope.component.adapter(IExtOp)
@zope.interface.implementer(IMonteCarlo)
class MonteCarloExtAdapter(MonteCarlo):

    def get_data(self):
        """
        Returns the data monte carlo has to operate on.
        Usually this is a list of columns
        """
        return [self.op.signal]

    def run(self, data):
        """
        sets the shuffled data on the operation and runs the operation
        Returns the operation result on the shuffeled data
        """
        return self.op.run(data)


class CreateMCCopies(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which creates a copy of the original(Columns).

    The data values of the copy are randomly varied within the uncertainty range of the original.
    In this case, it returns always an instance of CreateMCCopiesDefault().
    """

    name = 'CreateMCCopies'

    def __call__(self, **kwargs):
        assert 'original' in kwargs
        assert 'n' in kwargs

        res = super(CreateMCCopies, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CreateMCCopiesDefault' .
        """
        return 'CreateMCCopiesDefault'


class CreateMCCopiesDefault(BaseOperation):
    """
    Returns n copies of the original(Columns).

    The data values of the copies are randomly varied within the uncertainty range of the original.
    """

    name = 'CreateMCCopiesDefault'

    def run(self):
        """
        """
        original = self.kwargs['original']
        num_samples = self.kwargs['original']

        data = original.data
        err = original.error

        sample_data = np.ones((original.num_times,
                               original.num_levels,
                               num_samples)) * np.nan

        for t in original.num_times:
            fvb = original.first_valid_bin(t)
            lvb = original.last_valid_bin(t)
            for idx in range(fvb, lvb):
                sample_data[t, idx, :] = np.random.normal(
                    loc=data[t, idx],
                    scale=err[t, idx],
                    size=num_samples
                )

        result = []
        for n in range(num_samples):
            mc_copy = deepcopy(original)
            mc_copy.data[:, :] = sample_data[:, :, n]
            result.append(mc_copy)

        return result


gsm = zope.component.getGlobalSiteManager()
gsm.registerAdapter(MonteCarloExtAdapter, (IExtOp,), IMonteCarlo)

registry.register_class(CreateMCCopies,
                        CreateMCCopiesDefault.__name__,
                        CreateMCCopiesDefault)

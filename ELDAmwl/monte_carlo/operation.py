from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import ICfg
from ELDAmwl.component.interface import IElastBscOp
from ELDAmwl.component.interface import IExtOp
from ELDAmwl.component.interface import ILogger
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.products import Products
from ELDAmwl.utils.constants import FIXED
from multiprocessing.pool import Pool
from zope import component

import numpy as np
import sys
import zope


class MonteCarlo:
    """
    Implementation of monte carlo algorithm
    """

    sample_results = None
    sample_inputs = None

    def __init__(self, op):
        self.op = op

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    def get_sample_inputs(self, orig):
        # orig is a dict with signals used for the retrieval. e.g., Raman sig and elast sig

        # self.sample_inputs is a list of dictionaries with one set of signals for each iteration
        self.sample_inputs = []

        for sig in orig.keys():
            mc_generator = CreateMCCopies()(original=orig[sig],
                                            n=self.mc_params.nb_of_iterations,
                                            )
            samples = mc_generator.run()

            # if the list of samples is empty: create a dictionary for each iteration
            if len(self.sample_inputs) == 0:
                for n in range(self.mc_params.nb_of_iterations):
                    self.sample_inputs.append({sig: samples[n]})

            # if the list already exists: add a new key with the new sample for each iteration
            else:
                for n in range(self.mc_params.nb_of_iterations):
                    self.sample_inputs[n][sig] = samples[n]

    def get_sample_results(self):
        if self.cfg.PARALLEL:
            pool = Pool(self.cfg.NUM_CPU)
            self.sample_results = []
            results = pool.imap_unordered(self.run, self.sample_inputs)
            for result in results:
                if isinstance(result, Products):
                    self.sample_results.append(result.data.values)
                else:
                    self.logger.error('{} terminated due to errors'.format(result))
                    sys.exit(1)
            pool.close()
            pool.join()

        else:
            results = []
            for n in range(self.mc_params.nb_of_iterations):
                # sample = self.op.run(data=self.sample_inputs[n])
                self.logger.debug('calc sample {}'.format(n))
                sample = self.run(self.sample_inputs[n])
                if isinstance(sample, Products):
                    results.append(sample.data.values)
                else:
                    self.logger.error('{} terminated due to errors'.format(sample))
                    # sys.exit(1)
            self.sample_results = results

    def calc_mc_error(self):
        all = np.array(self.sample_results)
        return np.nanstd(all, axis=0)

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
        Usually this is a dict with Columns
        """
        return {'raman_sig': self.op.signal}

    def run(self, data):
        """
        puts the mc copy of data into the operation and runs the operation
        Returns the operation result
        """
        return self.op.run(data=data['raman_sig'])


@zope.component.adapter(IElastBscOp)
@zope.interface.implementer(IMonteCarlo)
class MonteCarloElastBscAdapter(MonteCarlo):

    def get_data(self):
        """
        Returns the data monte carlo has to operate on.
        Usually this is a dict with Columns
        """
        return {'elast_sig': self.op.elast_sig}

    def run(self, data):
        """
        puts the mc copy of data into the operation and runs the operation
        Returns the operation result
        """
        return self.op.run(data=data['elast_sig'])

    def get_sample_inputs(self, orig):
        super(MonteCarloElastBscAdapter, self).get_sample_inputs(orig)

        if self.op.bsc_params.lr_input_method == FIXED:
            orig_lr = self.op.elast_sig.ds.assumed_particle_lidar_ratio.values.mean()
            orig_lr_uncertainty = self.op.elast_sig.ds.assumed_particle_lidar_ratio_error.values.mean()

            if np.isnan(orig_lr_uncertainty):
                self.logger.warning('no lidar ratio uncertainty provided for product {}'.format(self.op.bsc_params.prod_id_str))
                return

            lr_samples = np.random.normal(loc=orig_lr,
                                          scale=orig_lr_uncertainty,
                                          size=self.mc_params.nb_of_iterations)

            for sample in range(self.mc_params.nb_of_iterations):
                self.sample_inputs[sample]['elast_sig'].ds.assumed_particle_lidar_ratio[:] = lr_samples[sample]

        # todo: variation in case of lr_input_method == PROFILE


class CreateMCCopies(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which creates a copy of the original(Columns).

    The data values of the copy are randomly varied within the uncertainty range of the original.
    In this case, it returns always an instance of CreateMCCopiesDefault().

     keyword Args:
        original (Columns): the original column instance
        n(int): number of copies

    returns:
        list with copies of the original column instance

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
        num_samples = self.kwargs['n']

        data = original.data
        err = original.err

        sample_data = np.ones((original.num_times,
                               original.num_levels,
                               num_samples)) * np.nan

        for t in range(original.num_times):
            for idx in np.where(~np.isnan(original.data[t]))[0]:
                sample_data[t, idx, :] = np.random.normal(
                    loc=data[t, idx],
                    scale=err[t, idx],
                    size=num_samples,
                )

        result = []
        for n in range(num_samples):
            mc_copy = deepcopy(original)
            mc_copy.data[:, :] = sample_data[:, :, n]
            result.append(mc_copy)

        return result


def register_monte_carlo():
    gsm = zope.component.getGlobalSiteManager()
    gsm.registerAdapter(MonteCarloExtAdapter, (IExtOp,), IMonteCarlo)
    gsm.registerAdapter(MonteCarloElastBscAdapter, (IElastBscOp,), IMonteCarlo)

    registry.register_class(CreateMCCopies,
                            CreateMCCopiesDefault.__name__,
                            CreateMCCopiesDefault)

from ELDAmwl.component.interface import ILogger
from multiprocessing.pool import Pool
from zope import component

import sys


class BaseDispatcher(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = component.queryUtility(ILogger)

    def dispatch_jobs_parallel(self, instrument_files):
        """
        Parallelize the jobs
        """

        list_of_metadata = []
        for instrument in instrument_files:
            list_of_metadata.append((self.cfg, instrument_files[instrument]))

        pool = Pool(self.cfg.CPU_CORES)
        # abortable_func = partial(
        #         abortable_worker,
        #         self.get_do_job(),
        #         timeout=self.cfg.PROCESS_TIMEOUT
        # )
        results = pool.imap_unordered(self.get_do_job(), list_of_metadata)
        for result in results:
            if isinstance(result, list):
                pass
            else:
                self.logger.error('{} terminated due to errors'.format(result))
                sys.exit(1)
        pool.close()
        pool.join()

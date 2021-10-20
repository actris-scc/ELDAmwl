import zope

from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.component.interface import IMonteCarlo, IExtOp


class MonteCarlo:
    """
    Implementation of monte carlo algorithm
    """

    def __init__(self, op):
        self.op = op

    def __call__(self):
        mc_adapter = IMonteCarlo(self.op)

        data = mc_adapter.get_data()

        results = []
        for i in range(30):
            shuffle = shuffle(data)
            results.append(mc_adapter.run(shuffle))

        return average_results(results)


@zope.component.adapter(IExtOp)
@zope.interface.implementer(IMonteCarlo)
class MonteCarloExtAdapter(MonteCarlo):

    def __init__(self, ext_op):
        self.ext_op = ext_op

    def get_data(self):
        """
        Returns the data monte carlo has to operate on.
        Usually this is a list of columns
        """
        return self.ext_op.data[0]

    def run(self, data):
        """
        sets the shuffled data on the operation and runs the operation
        Returns the operation result on the shuffeled data
        """
        return self.ext_op.run(data)


class ExtOp(BaseOperation):

    def run(self, data=None):
        """
        Runs the operatioon with data
        """
        if data is not None:
            result = ... # work with external data
        else:
            result = ... # work with internal data
        return result


class UseExtAdapter:

    def do(self):
        ext_op = ExpOp(data, params, ...)

        mc_ext = MonteCarlo(ext_op)()

import zope

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

    def get_data(self):
        """
        Returns the data monte carlo has to operate on.
        Usually this is a list of columns
        """
        return self.op.raman_signal

    def run(self, data):
        """
        sets the shuffled data on the operation and runs the operation
        Returns the operation result on the shuffeled data
        """
        return self.op.run(data)

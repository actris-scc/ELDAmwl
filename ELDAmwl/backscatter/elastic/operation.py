from ELDAmwl.backscatter.common.operation import BackscatterFactory
from ELDAmwl.backscatter.common.operation import BackscatterFactoryDefault
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry


class ElastBackscatterFactory(BackscatterFactory):
    """

    """

    name = 'ElastBackscatterFactory'

    def get_classname_from_db(self):
        return ElastBackscatterFactoryDefault.__name__


class ElastBackscatterFactoryDefault(BackscatterFactoryDefault):
    """
    derives a single instance of :class:`ElasticBackscatters`.
    """

    name = 'ElastBackscatterFactoryDefault'


class CalcElastBackscatter(BaseOperationFactory):
    """
    creates a class for the calculation of an elastic backscatter coefficient

    Returns an instance of BaseOperation which calculates the particle
    backscatter coefficient from an elastic signal. In this case, it
    will be always an instance of CalcElastBackscatterDefault.

    Keyword Args:
        bsc_params (:class:`ELDAmwl.backscatter.elastic.params.ElastBscParams`): \
                retrieval parameter of the backscatter product
        calibr_window (xarray.DataArray): variable 'backscatter_calibration_range' (time: 2, nv: 2) \
                contains bottom and top height of calibration window for each time slice
        calc_routine (:class:`ELDAmwl.bases.factory.BaseOperation`):
            result of :class:`ELDAmwl.backscatter.elastic.tools.operation.CalcElastBscProfile`
        signal_ratio (:class:`ELDAmwl.signals.Signals`): signal ratio
        empty_bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): \
                instance of RamanBackscatters which has all meta data but profile data are empty arrays

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """

    name = 'CalcElastBackscatter'

    def __call__(self, **kwargs):
        assert 'bsc_params' in kwargs
        assert 'calibr_window' in kwargs
        assert 'calc_routine' in kwargs
#        assert 'signal_ratio' in kwargs
        assert 'empty_bsc' in kwargs

        res = super(CalcElastBackscatter, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcElastBackscatterDefault' .
        """
        return 'CalcElastBackscatterDefault'


# @zope.interface.implementer(IRamBscOp)
class CalcElastBackscatterDefault(BaseOperation):
    """
    Calculates particle backscatter coefficient from elast signal.
    """

    name = 'CalcElastBackscatterDefault'


registry.register_class(CalcElastBackscatter,
                        CalcElastBackscatterDefault.__name__,
                        CalcElastBackscatterDefault)

registry.register_class(ElastBackscatterFactory,
                        ElastBackscatterFactoryDefault.__name__,
                        ElastBackscatterFactoryDefault)

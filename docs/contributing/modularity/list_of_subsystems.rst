Overview on modularized algorithm subsystems
--------------------------------------------

.. list-table:: list of BaseOperationFactories and corresponding BaseOperations

    * - BaseOperationFactory
      - BaseOperation
    * -
      - :class:`~ELDAmwl.elda_mwl_factories.RunELDAmwl`
    * - :class:`~ELDAmwl.get_basic_products.GetBasicProducts`
      - :class:`~ELDAmwl.get_basic_products.GetBasicProductsDefault`
    * - :class:`~ELDAmwl.rayleigh.RayleighLidarRatio`
      - :class:`~ELDAmwl.rayleigh.RayleighLidarRatioFromConst`
    * - :class:`~ELDAmwl.prepare_signals.PrepareSignals`
      - :class:`~ELDAmwl.prepare_signals.PrepareSignalsDefault`
    * - :class:`~ELDAmwl.prepare_signals.PrepareBscSignals`
      - :class:`~ELDAmwl.prepare_signals.PrepareBscSignalsDefault`
    * - :class:`~ELDAmwl.prepare_signals.PrepareExtSignals`
      - :class:`~ELDAmwl.prepare_signals.PrepareExtSignalsDefault`
    * - :class:`~ELDAmwl.extinction_factories.ExtinctionFactory`
      - :class:`~ELDAmwl.extinction_factories.ExtinctionFactoryDefault`
    * - :class:`~ELDAmwl.extinction_factories.SignalSlope`
      - :class:`~ELDAmwl.extinction_factories.WeightedLinearFit`

        :class:`~ELDAmwl.extinction_factories.NonWeightedLinearFit`
    * - :class:`~ELDAmwl.extinction_factories.ExtEffBinRes`
      - :class:`~ELDAmwl.extinction_factories.WeightedLinearFit_EffBinRes`

        :class:`~ELDAmwl.extinction_factories.NonWeightedLinearFit_EffBinRes`
    * - :class:`~ELDAmwl.extinction_factories.ExtUsedBinRes`
      - :class:`~ELDAmwl.extinction_factories.WeightedLinearFit_UsedBinRes`

        :class:`~ELDAmwl.extinction_factories.NonWeightedLinearFit_UsedBinRes`
    * -
      - :class:`~ELDAmwl.extinction_factories.LinFit`
    * -
      - :class:`~ELDAmwl.extinction_factories.LinFit_EffBinRes`
    * -
      - :class:`~ELDAmwl.extinction_factories.LinFit_UsedBinRes`
    * - :class:`~ELDAmwl.extinction_factories.SlopeToExtinction`
      - :class:`~ELDAmwl.extinction_factories.SlopeToExtinctionDefault`
    * - :class:`~ELDAmwl.signals.CombineDepolComponents`
      - :class:`~ELDAmwl.signals.CombineDepolComponentsDefault`
    * - :class:`~ELDAmwl.write_mwl_output.WriteMWLOutput`
      - :class:`~ELDAmwl.write_mwl_output.WriteMWLOutputDefault`



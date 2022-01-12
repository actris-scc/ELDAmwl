Overview on modularized algorithm subsystems
--------------------------------------------

.. list-table:: list of BaseOperationFactories and corresponding BaseOperations

    * - BaseOperationFactory
      - BaseOperation
    * -
      - :class:`~ELDAmwl.elda_mwl.elda_mwl.RunELDAmwl`
    * - :class:`~ELDAmwl.backscatter.common.operation.BackscatterFactory`
      - :class:`~ELDAmwl.backscatter.common.operation.BackscatterFactoryDefault`
    * - :class:`~ELDAmwl.backscatter.elastic.operation.CalcElastBackscatter`
      - :class:`~ELDAmwl.backscatter.elastic.operation.CalcElastBackscatterDefault`
    * - :class:`~ELDAmwl.backscatter.elastic.tools.operation.CalcElastBscProfile`
      - :class:`~ELDAmwl.backscatter.elastic.tools.operation.CalcBscProfileKF`

        :class:`~ELDAmwl.backscatter.elastic.tools.operation.CalcBscProfileIter`
    * - :class:`~ELDAmwl.extinction.operation.CalcExtinction`
      - :class:`~ELDAmwl.extinction.operation.CalcExtinctionDefault`
    * - :class:`~ELDAmwl.lidar_ratio.operation.CalcLidarRatio`
      - :class:`~ELDAmwl.lidar_ratio.operation.CalcLidarRatioDefault`
    * - :class:`~ELDAmwl.backscatter.raman.operation.CalcRamanBackscatter`
      - :class:`~ELDAmwl.backscatter.raman.operation.CalcRamanBackscatterDefault`
    * - :class:`~ELDAmwl.backscatter.raman.tools.operation.CalcRamanBscProfile`
      - :class:`~ELDAmwl.backscatter.raman.tools.operation.CalcRamanBscProfileViaBR`
    * - :class:`~ELDAmwl.signals.CombineDepolComponents`
      - :class:`~ELDAmwl.signals.CombineDepolComponentsDefault`
    * - :class:`~ELDAmwl.monte_carlo.operation.CreateMCCopies`
      - :class:`~ELDAmwl.monte_carlo.operation.CreateMCCopiesDefault`
    * - :class:`~ELDAmwl.backscatter.elastic.operation.ElastBackscatterFactory`
      - :class:`~ELDAmwl.backscatter.elastic.operation.ElastBackscatterFactoryDefault`
    * - :class:`~ELDAmwl.backscatter.common.vertical_resolution.operation.ElastBscEffBinRes`
      - :class:`~ELDAmwl.backscatter.common.vertical_resolution.operation.SavGolayEffBinRes`
    * - :class:`~ELDAmwl.backscatter.common.vertical_resolution.operation.ElastBscUsedBinRes`
      - :class:`~ELDAmwl.backscatter.common.vertical_resolution.operation.SavGolayUsedBinRes`
    * - :class:`~ELDAmwl.extinction.vertical_resolution.operation.ExtEffBinRes`
      - :class:`~ELDAmwl.extinction.vertical_resolution.operation.LinFitEffBinRes`
    * - :class:`~ELDAmwl.extinction.operation.ExtinctionFactory`
      - :class:`~ELDAmwl.extinction.operation.ExtinctionFactoryDefault`
    * - :class:`~ELDAmwl.extinction.vertical_resolution.operation.ExtUsedBinRes`
      - :class:`~ELDAmwl.extinction.vertical_resolution.operation.LinFitUsedBinRes`
    * - :class:`~ELDAmwl.backscatter.common.calibration.operation.FindCommonBscCalibrWindow`
      - :class:`~ELDAmwl.backscatter.common.calibration.operation.FindBscCalibrWindowAsInELDA`
    * - :class:`~ELDAmwl.elda_mwl.get_basic_products.GetBasicProducts`
      - :class:`~ELDAmwl.elda_mwl.get_basic_products.GetBasicProductsDefault`
    * - :class:`~ELDAmwl.elda_mwl.get_derived_products.GetDerivedProducts`
      - :class:`~ELDAmwl.elda_mwl.get_derived_products.GetDerivedProductsDefault`
    * - :class:`~ELDAmwl.elda_mwl.mwl_products.GetProductMatrix`
      - :class:`~ELDAmwl.elda_mwl.mwl_products.GetProductMatrixDefault`
    * - :class:`~ELDAmwl.lidar_ratio.operation.LidarRatioFactory`
      - :class:`~ELDAmwl.lidar_ratio.operation.LidarRatioFactoryDefault`
    * - :class:`~ELDAmwl.prepare_signals.PrepareBscSignals`
      - :class:`~ELDAmwl.prepare_signals.PrepareBscSignalsDefault`
    * - :class:`~ELDAmwl.prepare_signals.PrepareExtSignals`
      - :class:`~ELDAmwl.prepare_signals.PrepareExtSignalsDefault`
    * - :class:`~ELDAmwl.prepare_signals.PrepareSignals`
      - :class:`~ELDAmwl.prepare_signals.PrepareSignalsDefault`
    * - :class:`~ELDAmwl.elda_mwl.mwl_products.QualityControl`
      - :class:`~ELDAmwl.elda_mwl.mwl_products.QualityControlDefault`
    * - :class:`~ELDAmwl.backscatter.raman.operation.RamanBackscatterFactory`
      - :class:`~ELDAmwl.backscatter.raman.operation.RamanBackscatterFactoryDefault`
    * - :class:`~ELDAmwl.backscatter.common.vertical_resolution.operation.RamBscEffBinRes`
      - :class:`~ELDAmwl.backscatter.common.vertical_resolution.operation.SavGolayEffBinRes`
    * - :class:`~ELDAmwl.backscatter.common.vertical_resolution.operation.RamBscUsedBinRes`
      - :class:`~ELDAmwl.backscatter.common.vertical_resolution.operation.SavGolayUsedBinRes`
    * - :class:`~ELDAmwl.rayleigh.RayleighLidarRatio`
      - :class:`~ELDAmwl.rayleigh.RayleighLidarRatioFromConst`
    * - :class:`~ELDAmwl.extinction.tools.operation.SignalSlope`
      - :class:`~ELDAmwl.extinction.tools.operation.WeightedLinearFit`

        :class:`~ELDAmwl.extinction.tools.operation.NonWeightedLinearFit`
    * - :class:`~ELDAmwl.extinction.tools.operation.SlopeToExtinction`
      - :class:`~ELDAmwl.extinction.tools.operation.SlopeToExtinctionDefault`
    * - :class:`~ELDAmwl.products.SmoothRoutine`
      - :class:`~ELDAmwl.products.SmoothSavGolay`

        :class:`~ELDAmwl.products.SmoothSlidingAverage`
    * - :class:`~ELDAmwl.output.write_mwl_output.WriteMWLOutput`
      - :class:`~ELDAmwl.output.write_mwl_output.WriteMWLOutputDefault`



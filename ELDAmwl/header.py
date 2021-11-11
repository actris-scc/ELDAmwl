# -*- coding: utf-8 -*-
"""Classes for header information"""

from addict import Dict
from ELDAmwl.bases.base import ELDABase
from ELDAmwl.errors.exceptions import DifferentHeaderExists
from ELDAmwl.output.mwl_file_structure import MWLFileStructure
from ELDAmwl.utils.constants import NC_FILL_STR
from os.path import basename

import pandas as pd


# TITLE, REFERENCES, PROCESSOR_NAME, HEADER_ATTRS, HEADER_VARS


class Person:

    _name = NC_FILL_STR

    @classmethod
    def from_nc_file(cls, nc_ds, nc_name):
        """creates instance of Person from an ELPP file

        Args:
            nc_ds (xarray.Dataset): content of the ELPP file.
            nc_name (str): role of the person (e.g. 'PI')
        """
        result = cls()

        result.name = nc_ds.attrs[nc_name]
        for info in ['affiliation', 'affiliation_acronym', 'address', 'phone', 'email']:
            var_name = nc_name + '_' + info
            if var_name in nc_ds.attrs:
                result.__dict__[info] = nc_ds.attrs[var_name]

        return result

    def __eq__(self, other):
        result = True
        for a in self.__dict__.keys():
            if getattr(self, a) != getattr(other, a):
                result = False
        return result

    def to_ds_dict(self, ds, nc_name):
        """

        Args:
            ds: Dict, to be converted into ds
            nc_name:

        Returns:

        """
        for att in self.__dict__:
            ds_att_name = nc_name + '_' + att
            ds[ds_att_name] = self.__dict__[att]


class Header(ELDABase):
    attrs = None
    vars = None
    start_time = None
    end_time = None
    class_attrs = Dict({'pi': 'PI',
                        'data_originator': 'Data_Originator'})

    def __init__(self):
        super(Header, self).__init__()
        self.attrs = Dict()
        self.vars = Dict()
        self.mwl_struct = MWLFileStructure()

    @classmethod
    def from_nc_file(cls, nc_file, nc_ds):
        """reads header information from an ELPP file

        Args:
            nc_ds (xarray.Dataset): content of the ELPP file.
        """
        mwl_struct = MWLFileStructure()

        result = cls()
        result.attrs.measurement_ID = nc_ds.measurement_ID
        result.attrs.comment = nc_ds.comment
        result.attrs.title = mwl_struct.TITLE
        result.attrs.source = nc_ds.source
        result.attrs.references = mwl_struct.REFERENCES

        result.attrs.station_ID = nc_ds.station_ID
        result.attrs.location = nc_ds.location
        result.attrs.institution = nc_ds.institution

        result.attrs.pi = Person.from_nc_file(nc_ds, 'PI')
        result.attrs.data_originator = Person.from_nc_file(nc_ds, 'Data_Originator')

        result.attrs.data_processing_institution = nc_ds.data_processing_institution

        result.attrs.system = nc_ds.system
        result.attrs.hoi_system_ID = nc_ds.hoi_system_ID
        result.attrs.hoi_configuration_ID = nc_ds.hoi_configuration_ID

        result.attrs.elpp_history = nc_ds.history
        result.attrs.input_file = basename(nc_file)  # ToDo Volker
        if 'molecular_calculation_source_file' in nc_ds.attrs:
            result.attrs.molecular_calculation_source_file = \
                nc_ds.molecular_calculation_source_file
        result.attrs.processor_name = mwl_struct.PROCESSOR_NAME
        # result.processor_version =
        # result.__file_format_version = cfg.FILE_FORMAT_VERSION
        # result.scc_version = nc_ds.scc_version
        # result.scc_version_description = nc_ds.scc_version_description

        result.vars.cloud_mask_type = nc_ds.cloud_mask_type
        result.vars.cloud_mask_type.load()
        result.vars.scc_product_type = nc_ds.scc_product_type
        result.vars.scc_product_type.load()
        result.vars.molecular_calculation_source = nc_ds.molecular_calculation_source
        result.vars.molecular_calculation_source.load()
        result.vars.station_latitude = nc_ds.latitude
        result.vars.station_latitude.load()
        result.vars.station_longitude = nc_ds.longitude
        result.vars.station_longitude.load()
        result.vars.station_altitude = nc_ds.station_altitude

        # it is really painful to do these conversions. Unfortunately, I found no better solution
        result.start_time = pd.Timestamp(nc_ds.time_bounds[0, 0].values).to_pydatetime()
        result.end_time = pd.Timestamp(nc_ds.time_bounds[-1, -1].values).to_pydatetime()

        return result

    def append(self, new_header):
        not_mwl_attrs = ['input_file', 'elpp_history']

        for att in self.attrs:
            if att not in not_mwl_attrs:
                if self.attrs[att] != new_header.attrs[att]:
                    raise DifferentHeaderExists

        for var in self.vars:
            if bool(self.vars[var] != new_header.vars[var]):
                raise DifferentHeaderExists

        self.attrs.input_file = self.attrs.input_file + ' ' + new_header.attrs.input_file

    def __eq__(self, other):
        result = True
        for a in self.__dict__.keys():
            if getattr(self, a) != getattr(other, a):
                result = False
        return result

    def to_ds_dict(self, ds, group):
        """

        Args:
            ds: dict, to be converted into dataset
            group (str): group of the nc file into which
                    the global attributes and variables
                    shall be written. can be GENERAL or META_DATA
        Returns:

        """

        write_attrs = self.mwl_struct.HEADER_ATTRS[group]
        write_vars = self.mwl_struct.HEADER_VARS[group]

        for att in self.attrs:
            if att in write_attrs:
                if att in self.class_attrs:
                    self.attrs[att].to_ds_dict(ds.attrs, self.class_attrs[att])
                elif self.attrs[att] != {}:
                    ds.attrs[att] = self.attrs[att]
                else:
                    self.logger.warning('cannot write empty attribute {} in mwl file'.format(att))

        if 'measurement_start_datetime' in write_attrs:
            ds.measurement_start_datetime = self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        if 'measurement_stop_datetime' in write_attrs:
            ds.measurement_stop_datetime = self.end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        for var in self.vars:
            nc_varname = self.vars[var].name
            if nc_varname in write_vars:
                ds.data_vars[nc_varname] = self.vars[var]

    @property
    def latitude(self):
        """measurement site latitude in degrees_north"""
        return self.attrs.station.station_latitude

    @property
    def longitude(self):
        """measurement site longitude in degrees_east"""
        return self.attrs.station.station_longitude

    @property
    def altitude(self):
        """measurement site altitude in m a.s.l."""
        return self.attrs.station.station_altitude

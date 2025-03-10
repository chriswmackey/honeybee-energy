# coding=utf-8
"""Temperature (thermostat) and humidity (humidistat) setpoints for a thermal zone."""
from __future__ import division
import random

from honeybee._lockable import lockable
from honeybee.typing import float_positive, float_in_range, clean_and_id_ep_string

from ._base import _LoadBase
from ..schedule.ruleset import ScheduleRuleset
from ..schedule.fixedinterval import ScheduleFixedInterval
from ..reader import parse_idf_string
from ..writer import generate_idf_string
from ..properties.extension import SetpointProperties

import honeybee_energy.lib.scheduletypelimits as _type_lib


@lockable
class Setpoint(_LoadBase):
    """Temperature (thermostat) and humidity (humidistat) setpoints for a thermal zone.

    Args:
        identifier: Text string for a unique Setpoint ID. Must be < 100 characters
            and not contain any EnergyPlus special characters. This will be used to
            identify the object across a model and in the exported IDF.
        heating_schedule: A ScheduleRuleset or ScheduleFixedInterval for the
            heating setpoint.
        cooling_schedule: A ScheduleRuleset or ScheduleFixedInterval for the
            cooling setpoint.
        humidifying_schedule: A ScheduleRuleset or ScheduleFixedInterval for
            the humidification setpoint. If None, no additional humidification
            will be applied by the HVAC system. (Default: None).
        dehumidifying_schedule: A ScheduleRuleset or ScheduleFixedInterval for
            the dehumidification setpoint. If None, no additional dehumidification
            will be performed by the HVAC system. (Default: None).
        setpoint_cutout_difference: An optional positive number for the temperature
            difference between the cutout temperature and the setpoint temperature.
            Specifying a non-zero number here is useful for modeling the throttling
            range associated with a given setup of setpoint controls and HVAC equipment.
            Throttling ranges describe the range where a zone is slightly over-cooled
            or over-heated beyond the thermostat setpoint. They are used to avoid
            situations where HVAC systems turn on only to turn off a few minutes later,
            thereby wearing out the parts of mechanical systems faster. They can
            have a minor impact on energy consumption and can often have significant
            impacts on occupant thermal comfort, though using the default value
            of zero will often yield results that are close enough when trying
            to estimate the annual heating/cooling energy use. Specifying a value
            of zero effectively assumes that the system will turn on whenever
            conditions are outside the setpoint range and will cut out as soon
            as the setpoint is reached. (Default: 0).

    Properties:
        * identifier
        * display_name
        * heating_schedule
        * cooling_schedule
        * humidifying_schedule
        * dehumidifying_schedule
        * setpoint_cutout_difference
        * heating_setpoint
        * cooling_setpoint
        * humidifying_setpoint
        * dehumidifying_setpoint
        * heating_setback
        * cooling_setback
        * humidifying_setback
        * dehumidifying_setback
        * user_data
    """
    __slots__ = ('_heating_schedule', '_cooling_schedule', '_humidifying_schedule',
                 '_dehumidifying_schedule', '_setpoint_cutout_difference')
    _humidifying_schedule_no_limit = ScheduleRuleset.from_constant_value(
        'HumidNoLimit', 0, _type_lib.humidity)
    _dehumidifying_schedule_no_limit = ScheduleRuleset.from_constant_value(
        'DeHumidNoLimit', 100, _type_lib.humidity)

    def __init__(self, identifier, heating_schedule, cooling_schedule,
                 humidifying_schedule=None, dehumidifying_schedule=None,
                 setpoint_cutout_difference=0):
        """Initialize Setpoint."""
        _LoadBase.__init__(self, identifier)
        # defaults that might be overwritten
        self._dehumidifying_schedule = None

        self.heating_schedule = heating_schedule
        self.cooling_schedule = cooling_schedule
        self.humidifying_schedule = humidifying_schedule
        self.dehumidifying_schedule = dehumidifying_schedule
        self.setpoint_cutout_difference = setpoint_cutout_difference
        self._properties = SetpointProperties(self)

    @property
    def heating_schedule(self):
        """Get or set a ScheduleRuleset or ScheduleFixedInterval for the heating setpoint.
        """
        return self._heating_schedule

    @heating_schedule.setter
    def heating_schedule(self, value):
        self._check_temperature_schedule_type(value, 'Heating Setpoint')
        value.lock()   # lock editing in case schedule has multiple references
        self._heating_schedule = value

    @property
    def cooling_schedule(self):
        """Get or set a ScheduleRuleset or ScheduleFixedInterval for the cooling setpoint.
        """
        return self._cooling_schedule

    @cooling_schedule.setter
    def cooling_schedule(self, value):
        self._check_temperature_schedule_type(value, 'Cooling Setpoint')
        value.lock()   # lock editing in case schedule has multiple references
        self._cooling_schedule = value

    @property
    def humidifying_schedule(self):
        """Get or set a ScheduleRuleset or ScheduleFixedInterval for humidification.
        """
        return self._humidifying_schedule

    @humidifying_schedule.setter
    def humidifying_schedule(self, value):
        if value is not None:
            self._check_humidity_schedule_type(value, 'Humidifying Setpoint')
            value.lock()   # lock editing in case schedule has multiple references
            self._humidifying_schedule = value
            if self._dehumidifying_schedule is None:
                self._dehumidifying_schedule = self._dehumidifying_schedule_no_limit
        else:
            self._humidifying_schedule = None if self._dehumidifying_schedule is None \
                else self._humidifying_schedule_no_limit

    @property
    def dehumidifying_schedule(self):
        """Get or set a ScheduleRuleset or ScheduleFixedInterval for dehumidification.
        """
        return self._dehumidifying_schedule

    @dehumidifying_schedule.setter
    def dehumidifying_schedule(self, value):
        if value is not None:
            self._check_humidity_schedule_type(value, 'Dehumidifying Setpoint')
            value.lock()   # lock editing in case schedule has multiple references
            self._dehumidifying_schedule = value
            if self._humidifying_schedule is None:
                self._humidifying_schedule = self._humidifying_schedule_no_limit
        else:
            self._dehumidifying_schedule = None if self._humidifying_schedule is None \
                else self._dehumidifying_schedule_no_limit

    @property
    def setpoint_cutout_difference(self):
        """Get or set the temperature difference between the cutout and the setpoint."""
        return self._setpoint_cutout_difference

    @setpoint_cutout_difference.setter
    def setpoint_cutout_difference(self, value):
        self._setpoint_cutout_difference = float_positive(
            value, 'setpoint cutout difference')

    @property
    def heating_setpoint(self):
        """Get or set a single constant temperature for the heating setpoint [C].

        Note that, if a varying heating_schedule has been assigned to this object, this
        property will be the highest temperature within the heating_schedule.
        """
        return self._max_schedule_value(self._heating_schedule)

    @heating_setpoint.setter
    def heating_setpoint(self, value):
        value = float_in_range(value, -273.15, input_name='heating setpoint')
        schedule = ScheduleRuleset.from_constant_value(
            '{}_HtgSetp'.format(self.identifier), value, _type_lib.temperature)
        self.heating_schedule = schedule

    @property
    def cooling_setpoint(self):
        """Get or set a single constant temperature for the cooling setpoint [C].

        Note that, if a varying cooling_schedule has been assigned to this object, this
        property will be the lowest temperature within the cooling_schedule.
        """
        return self._min_schedule_value(self._cooling_schedule)

    @cooling_setpoint.setter
    def cooling_setpoint(self, value):
        value = float_in_range(value, -273.15, input_name='cooling setpoint')
        schedule = ScheduleRuleset.from_constant_value(
            '{}_ClgSetp'.format(self.identifier), value, _type_lib.temperature)
        self.cooling_schedule = schedule

    @property
    def humidifying_setpoint(self):
        """Get or set a single constant value for the humidifying setpoint [%].

        Note that, if a varying humidifying_schedule has been assigned to this object,
        this property will be the lowest value within the humidifying_schedule.
        """
        return self._max_schedule_value(self._humidifying_schedule) if \
            self._humidifying_schedule is not None else None

    @humidifying_setpoint.setter
    def humidifying_setpoint(self, value):
        if value is not None:
            value = float_in_range(value, 0, 100, 'humidifying setpoint')
            schedule = ScheduleRuleset.from_constant_value(
                '{}_HumidSetp'.format(self.identifier), value, _type_lib.humidity)
            self.humidifying_schedule = schedule
        else:
            self.humidifying_schedule = None

    @property
    def dehumidifying_setpoint(self):
        """Get or set a single constant value for the dehumidifying setpoint [%].

        Note that, if a varying dehumidifying_schedule has been assigned to this object,
        this property will be the lowest value within the dehumidifying_schedule.
        """
        return self._min_schedule_value(self._dehumidifying_schedule) if \
            self._dehumidifying_schedule is not None else None

    @dehumidifying_setpoint.setter
    def dehumidifying_setpoint(self, value):
        if value is not None:
            value = float_in_range(value, 0, 100, 'dehumidifying setpoint')
            schedule = ScheduleRuleset.from_constant_value(
                '{}_DeHumidSetp'.format(self.identifier), value, _type_lib.humidity)
            self.dehumidifying_schedule = schedule
        else:
            self.dehumidifying_schedule = None

    @property
    def heating_setback(self):
        """Get the lowest temperature in the heating setpoint schedule [C].

        Note that, if a constant heating_setpoint has been assigned to this object,
        this property will the same as the heating_setpoint.
        """
        return self._min_schedule_value(self._heating_schedule)

    @property
    def cooling_setback(self):
        """Get the highest temperature in the cooling setpoint schedule [C].

        Note that, if a constant cooling_setpoint has been assigned to this object,
        this property will the same as the cooling_setpoint.
        """
        return self._max_schedule_value(self._cooling_schedule)

    @property
    def humidifying_setback(self):
        """Get the lowest humidity in the humidifying setpoint schedule [%].

        Note that, if a constant humidifying_setpoint has been assigned to this object,
        this property will the same as the humidifying_setpoint.
        """
        return self._min_schedule_value(self._humidifying_schedule) if \
            self._humidifying_schedule is not None else None

    @property
    def dehumidifying_setback(self):
        """Get the highest humidity in the dehumidifying setpoint schedule [%].

        Note that, if a constant dehumidifying_setpoint has been assigned to this object,
        this property will the same as the dehumidifying_setpoint.
        """
        return self._max_schedule_value(self._dehumidifying_schedule) if \
            self._dehumidifying_schedule is not None else None

    def remove_humidity_setpoints(self):
        """Remove all humidity setpoints from this object."""
        self._humidifying_schedule = None
        self._dehumidifying_schedule = None

    def add_humidity_from_idf(self, idf_string, schedule_dict):
        """Add humidity setpoints to this object from an EnergyPlus IDF text string.

        Args:
            idf_string: A text string fully describing an EnergyPlus
                ZoneControl:Humidistat definition.
            schedule_dict: A dictionary with schedule identifiers as keys and honeybee
                schedule objects as values (either ScheduleRuleset or
                ScheduleFixedInterval). These will be used to assign the schedules to
                the Setpoint object.
        """
        # check the inputs
        ep_strs = parse_idf_string(idf_string, 'ZoneControl:Humidistat,')

        # extract the schedules from the string
        try:
            try:
                humid_sched = schedule_dict[ep_strs[2]] if ep_strs[2] != '' else None
                dehumid_sched = schedule_dict[ep_strs[3]] if ep_strs[3] != '' else None
            except KeyError as e:
                raise ValueError('Failed to find {} in the schedule_dict.'.format(e))
        except IndexError:
            pass  # shorter humidistat definition lacking values

        # assign the properties to this object
        self.humidifying_schedule = humid_sched
        self.dehumidifying_schedule = dehumid_sched

    def diversify(self, count, schedule_offset=1, timestep=1, schedule_indices=None):
        """Get an array of diversified Setpoints derived from this "average" one.

        Approximately 2/3 of the schedules in the output objects will be offset
        from the mean by the input schedule_offset (1/3 ahead and another 1/3 behind).

        Args:
            count: An positive integer for the number of diversified objects to
                generate from this mean object.
            schedule_offset: A positive integer for the number of timesteps at which
                the setpoint schedule of the resulting objects will be shifted - roughly
                1/3 of the objects ahead and another 1/3 behind. (Default: 1).
            timestep: An integer for the number of timesteps per hour at which the
                shifting is occurring. This must be a value between 1 and 60, which
                is evenly divisible by 60. 1 indicates that each step is an hour
                while 60 indicates that each step is a minute. (Default: 1).
            schedule_indices: An optional list of integers from 0 to 2 with a length
                equal to the input count, which will be used to set whether a given
                schedule is behind (0), ahead (2), or the same (1). This can be
                used to coordinate schedules across diversified programs. If None
                a random list of integers will be genrated. (Default: None).
        """
        # generate shifted schedules
        heats = self._shift_schedule(self.heating_schedule, schedule_offset, timestep)
        cools = self._shift_schedule(self.cooling_schedule, schedule_offset, timestep)
        if self.humidifying_schedule is not None:
            humids = self._shift_schedule(
                self.humidifying_schedule, schedule_offset, timestep)
            dehumids = self._shift_schedule(
                self.dehumidifying_schedule, schedule_offset, timestep)
        if schedule_indices is None:
            schedule_indices = [random.randint(0, 2) for i in range(count)]

        # generate the new objects and return them
        new_objects = []
        for sch_int in schedule_indices:
            new_obj = self.duplicate()
            new_obj.identifier = clean_and_id_ep_string(self.identifier)
            new_obj.heating_schedule = heats[sch_int]
            new_obj.cooling_schedule = cools[sch_int]
            if self.humidifying_schedule is not None:
                new_obj.humidifying_schedule = humids[sch_int]
                new_obj.dehumidifying_schedule = dehumids[sch_int]
            new_objects.append(new_obj)
        return new_objects

    @classmethod
    def from_idf(cls, idf_string, schedule_dict):
        """Create an Setpoint object from an EnergyPlus IDF text string.

        Note that this method only loads the heating and cooling setpoints from an
        IDF and, to also load humidity setpoints, the add_humidity_from_idf method
        should be used.

        Args:
            idf_string: A text string fully describing an EnergyPlus
                HVACTemplate:Thermostat definition.
            schedule_dict: A dictionary with schedule identifiers as keys and honeybee
                schedule objects as values (either ScheduleRuleset or
                ScheduleFixedInterval). These will be used to assign the schedules to
                the Setpoint object.

        Returns:
            setpoint -- A Setpoint object loaded from the idf_string.
        """
        # check the inputs
        ep_strs = parse_idf_string(idf_string, 'HVACTemplate:Thermostat,')

        # remove the zone id from the thermostat
        setp_obj_id = ep_strs[0].split('..')[0]

        # extract the schedules from the string
        try:
            heat_sched = schedule_dict[ep_strs[1]] if ep_strs[1] != '' else None
            cool_sched = schedule_dict[ep_strs[3]] if ep_strs[3] != '' else None
        except KeyError as e:
            raise ValueError('Failed to find {} in the schedule_dict.'.format(e))

        # return the object and the zone id for the object
        setpoint = cls(setp_obj_id, heat_sched, cool_sched)
        return setpoint

    @classmethod
    def from_dict(cls, data):
        """Create a Setpoint object from a dictionary.

        Note that the dictionary must be a non-abridged version for this classmethod
        to work.

        Args:
            data: A Setpoint dictionary in following the format below.

        .. code-block:: python

            {
            "type": 'Setpoint',
            "identifier": 'Hospital_Patient_Room_Setpoint_210_230',
            "display_name": 'Patient Room Setpoint',
            "heating_schedule": {}, # ScheduleRuleset/FixedInterval dictionary
            "cooling_schedule": {}, # ScheduleRuleset/FixedInterval dictionary
            "humidifying_schedule": {}, # ScheduleRuleset/FixedInterval dictionary
            "dehumidifying_schedule": {}, # ScheduleRuleset/FixedInterval dictionary
            "setpoint_cutout_difference": 0.5  # number for cutout difference
            }
        """
        assert data['type'] == 'Setpoint', \
            'Expected Setpoint dictionary. Got {}.'.format(data['type'])
        heat_sched = cls._get_schedule_from_dict(data['heating_schedule'])
        cool_sched = cls._get_schedule_from_dict(data['cooling_schedule'])
        humid_sched = cls._get_schedule_from_dict(data['humidifying_schedule']) if \
            'humidifying_schedule' in data and \
            data['humidifying_schedule'] is not None else None
        dehumid_sched = cls._get_schedule_from_dict(data['dehumidifying_schedule']) if \
            'dehumidifying_schedule' in data and \
            data['dehumidifying_schedule'] is not None else None
        cut = data['setpoint_cutout_difference'] \
            if 'setpoint_cutout_difference' in data and \
            data['setpoint_cutout_difference'] is not None else 0
        new_obj = cls(data['identifier'], heat_sched, cool_sched,
                      humid_sched, dehumid_sched, cut)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        if 'user_data' in data and data['user_data'] is not None:
            new_obj.user_data = data['user_data']
        if 'properties' in data and data['properties'] is not None:
            new_obj.properties._load_extension_attr_from_dict(data['properties'])
        return new_obj

    @classmethod
    def from_dict_abridged(cls, data, schedule_dict):
        """Create a Setpoint object from an abridged dictionary.

        Args:
            data: A SetpointAbridged dictionary in following the format below.
            schedule_dict: A dictionary with schedule identifiers as keys and
                honeybee schedule objects as values (either ScheduleRuleset or
                ScheduleFixedInterval). These will be used to assign the schedules
                to the Setpoint object.

        .. code-block:: python

            {
            "type": 'SetpointAbridged',
            "identifier": 'Hospital_Patient_Room_Setpoint_210_230',
            "display_name": 'Patient Room Setpoint',
            "heating_schedule": "Hospital Pat Room Heating", # Schedule identifier
            "cooling_schedule": "Hospital Pat Room Cooling", # Schedule identifier
            "humidifying_schedule": "Hospital Pat Room Humidify", # Schedule identifier
            "dehumidifying_schedule": "Hospital Pat Room Dehumidify", # Sched identifier
            "setpoint_cutout_difference": 0.5  # number for cutout difference
            }
        """
        assert data['type'] == 'SetpointAbridged', \
            'Expected SetpointAbridged dictionary. Got {}.'.format(data['type'])
        try:
            heat_sched = schedule_dict[data['heating_schedule']]
            cool_sched = schedule_dict[data['cooling_schedule']]
        except KeyError as e:
            raise ValueError('Failed to find {} in the schedule_dict.'.format(e))

        humid_sched = None
        dehumid_sched = None
        if 'humidifying_schedule' in data and data['humidifying_schedule'] is not None:
            try:
                humid_sched = schedule_dict[data['humidifying_schedule']]
            except KeyError as e:
                raise ValueError('Failed to find {} in the schedule_dict.'.format(e))
        if 'dehumidifying_schedule' in data and data['dehumidifying_schedule'] is not None:
            try:
                dehumid_sched = schedule_dict[data['dehumidifying_schedule']]
            except KeyError as e:
                raise ValueError('Failed to find {} in the schedule_dict.'.format(e))
        cut = data['setpoint_cutout_difference'] \
            if 'setpoint_cutout_difference' in data and \
            data['setpoint_cutout_difference'] is not None else 0
        new_obj = cls(data['identifier'], heat_sched, cool_sched,
                      humid_sched, dehumid_sched, cut)
        if 'display_name' in data and data['display_name'] is not None:
            new_obj.display_name = data['display_name']
        if 'user_data' in data and data['user_data'] is not None:
            new_obj.user_data = data['user_data']
        if 'properties' in data and data['properties'] is not None:
            new_obj.properties._load_extension_attr_from_dict(data['properties'])
        return new_obj

    def to_idf(self, zone_identifier):
        """IDF string representation of Setpoint object's thermostat.

        Note that this method only outputs a string for the HVACTemplate:Thermostat
        object and, to write everything needed to describe the object into an IDF,
        this object's schedules must also be written. If the humidifying or
        dehumidifying schedules are not None, the to_idf_humidistat method should also
        be used to write the humidistat.

        Args:
            zone_identifier: Text for the zone identifier that the Setpoint
                object is assigned to.

        .. code-block:: shell

            ZoneControl:Thermostat,
                AllControlledZones Thermostat,      !- Name
                AllControlledZones,                 !- Zone Name
                Zone Control Type Sched,            !- Control Type Schedule Name
                ThermostatSetpoint:SingleCooling,   !- Control 1 Object Type
                CoolingSetPoint,                    !- Control 1 Name
                ThermostatSetpoint:SingleHeating,   !- Control 2 Object Type
                HeatingSetpoint,                    !- Control 2 Name
                ThermostatSetpoint:DualSetpoint,    !- Control 3 Object Type
                DualSetPoint;                       !- Control 3 Name
        """
        if self.setpoint_cutout_difference == 0:
            values = ('{}..{}'.format(self.identifier, zone_identifier),
                      self.heating_schedule.identifier, '',
                      self.cooling_schedule.identifier, '')
            comments = ('name', 'heating setpoint schedule', 'heating setpoint {C}',
                        'cooling setpoint schedule', 'cooling setpoint {C}')
            return generate_idf_string('HVACTemplate:Thermostat', values, comments)
        else:  # write out detailed objects for the thermostat
            # create the detailed thermostat object
            t_stat_vals = values = (
                '{}..{}'.format(self.identifier, zone_identifier),
                self.heating_schedule.identifier, self.cooling_schedule.identifier)
            ts_com = ('name', 'heating setpoint schedule', 'cooling setpoint schedule')
            t_stat = generate_idf_string(
                'ThermostatSetpoint:DualSetpoint', t_stat_vals, ts_com)
            # create the schedule to indicate heating/cooling is always active
            sch_tl_id = '{} Any Number'.format(zone_identifier)
            sch_tl = generate_idf_string('ScheduleTypeLimits', (sch_tl_id,), ('name',))
            sch_id = '{}-Always 4'.format(zone_identifier)
            sch_vals = (sch_id, sch_tl_id, 'Through: 12/31', 'For: AllDays',
                        'Until: 24:00', '4')
            sch_com = ('name', 'type limits', '', '', '', '')
            sch = generate_idf_string('Schedule:Compact', sch_vals, sch_com)
            # create the zone control object
            ctrl_vals = values = (
                '{} Thermostat'.format(zone_identifier), zone_identifier, sch_id,
                'ThermostatSetpoint:DualSetpoint',
                '{}..{}'.format(self.identifier, zone_identifier),
                '', '', '', '', '', '', self.setpoint_cutout_difference)
            ctrl_com = ('name', 'zone name', 'control type schedule',
                        'control object type', 'control name', '', '', '', '', '', '',
                        'temperature difference between cutout and setpoint')
            z_ctrl = generate_idf_string('ZoneControl:Thermostat', ctrl_vals, ctrl_com)
            return '\n\n'.join((t_stat, sch_tl, sch, z_ctrl))

    def to_idf_humidistat(self, zone_identifier):
        """IDF string representation of Setpoint object's humidistat.

        Note that this method only outputs strings for the ZoneControl:Humidistat
        and, to write everything needed to describe the object into an IDF, this
        object's schedules must also be written.

        Also note that this method will return None if no humidity setpoint schedules
        have been assigned.

        Args:
            zone_identifier: Text for the zone identifier that the Setpoint
                object is assigned to.

        .. code-block:: shell

            ZoneControl:Humidistat,
                Zone 2 Humidistat,   !- Humidistat Name
                EAST ZONE,           !- Zone Name
                Min Rel Hum Set Sch, !- Humidifying Relative Humidity Setpoint SCHEDULE Name
                Max Rel Hum Set Sch; !- Dehumidifying Relative Humidity Setpoint SCHEDULE Name
        """
        if self.humidifying_schedule is not None:
            values = ('{}_{}'.format(self.identifier, zone_identifier), zone_identifier,
                      self.humidifying_schedule.identifier,
                      self.dehumidifying_schedule.identifier)
            comments = ('name', 'zone name', 'humidifying setpoint schedule',
                        'dehumidifying setpoint schedule')
            return generate_idf_string('ZoneControl:Humidistat', values, comments)
        return None

    def to_dict(self, abridged=False):
        """Setpoint dictionary representation.

        Args:
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True),
                which only specifies the identifiers of schedules. Default: False.
        """
        base = {'type': 'Setpoint'} if not abridged else {'type': 'SetpointAbridged'}
        base['identifier'] = self.identifier
        if not abridged:
            base['heating_schedule'] = self.heating_schedule.to_dict()
            base['cooling_schedule'] = self.cooling_schedule.to_dict()
            if self.humidifying_schedule is not None:
                base['humidifying_schedule'] = self.humidifying_schedule.to_dict()
                base['dehumidifying_schedule'] = self.dehumidifying_schedule.to_dict()
        else:
            base['heating_schedule'] = self.heating_schedule.identifier
            base['cooling_schedule'] = self.cooling_schedule.identifier
            if self.humidifying_schedule is not None:
                base['humidifying_schedule'] = self.humidifying_schedule.identifier
                base['dehumidifying_schedule'] = self.dehumidifying_schedule.identifier
        if self.setpoint_cutout_difference != 0:
            base['setpoint_cutout_difference'] = self.setpoint_cutout_difference
        if self._display_name is not None:
            base['display_name'] = self.display_name
        if self._user_data is not None:
            base['user_data'] = self.user_data
        prop_dict = self.properties.to_dict()
        if prop_dict is not None:
            base['properties'] = prop_dict
        return base

    @staticmethod
    def average(identifier, setpoints, weights=None, timestep_resolution=1):
        """Get a Setpoint object that's an average between other Setpoints.

        Args:
            identifier: Text string for a unique ID for the new averaged Setpoint.
                Must be < 100 characters and not contain any EnergyPlus special
                characters. This will be used to identify the object across a model
                and in the exported IDF.
            setpoints: A list of Setpoint objects that will be averaged
                together to make a new Setpoint.
            weights: An optional list of fractional numbers with the same length
                as the input setpoints. These will be used to weight each of the
                Setpoint objects in the resulting average. Note that, if the sum of
                the weights is less than 1, the unaccounted fraction will be assumed
                to be at the weighted average setpoints of the other objects.
                If None, the objects will be weighted equally. Default: None.
            timestep_resolution: An optional integer for the timestep resolution
                at which the schedules will be averaged. Any schedule details
                smaller than this timestep will be lost in the averaging process.
                Default: 1.

        Returns:
            A Setpoint object that represents the (weighted) average between
            the input setpoints.
        """
        weights, u_weights = Setpoint._check_avg_weights(setpoints, weights, 'Setpoint')

        # calculate the average thermostat schedules
        heat_sched = Setpoint._average_schedule(
            '{}_HtgSetp Schedule'.format(identifier),
            [setp.heating_schedule for setp in setpoints], u_weights, timestep_resolution)
        cool_sched = Setpoint._average_schedule(
            '{}_ClgSetp Schedule'.format(identifier),
            [setp.cooling_schedule for setp in setpoints], u_weights, timestep_resolution)

        # calculate the average humidistat schedules
        humid_scheds = [sp.humidifying_schedule for sp in setpoints]
        if all(val is None for val in humid_scheds):
            humid_sched = None
            dehumid_sched = None
        else:
            dehumid_scheds = [sp.dehumidifying_schedule for sp in setpoints]
            humid_sch_id = '{}_Humid Schedule'.format(identifier)
            dehumid_sch_id = '{}_Dehumid Schedule'.format(identifier)
            for i, sch in enumerate(humid_scheds):
                if sch is None:
                    humid_scheds[i] = Setpoint._humidifying_schedule_no_limit
                    dehumid_scheds[i] = Setpoint._dehumidifying_schedule_no_limit
            humid_sched = Setpoint._average_schedule(
                humid_sch_id, humid_scheds, u_weights, timestep_resolution)
            dehumid_sched = Setpoint._average_schedule(
                dehumid_sch_id, dehumid_scheds, u_weights, timestep_resolution)

        # calculate the average setpoint_cutout_difference
        cuts = [sp.setpoint_cutout_difference for sp in setpoints]
        sp_cut = sum(cuts) / len(cuts)

        # return the averaged object
        return Setpoint(identifier, heat_sched, cool_sched,
                        humid_sched, dehumid_sched, sp_cut)

    @staticmethod
    def strictest(identifier, setpoints, timestep_resolution=1):
        """Get a Setpoint object that represents the strictest between several Setpoints.

        For each timestep of the heating setpoint schedule, the highest setpoint
        will govern the result. For each timestep of the cooling setpoint, the
        lowest setpoint will govern. Humidifying and dehumidifying schedules
        will similarly be adjusted. The lowest setpoint_cutout_difference will
        govern because a smaller throttling range tends to be associated
        with tighter/stricter setpoint controls. Also, a lower cutout difference
        helps avoid putting the heating and cooling setpoints in conflict with
        one another when taking the strictest values.

        This method is useful when trying to resolve a set of rooms with different
        setpoint criteria that are placed within the same thermal zone.

        Args:
            identifier: Text string for a unique ID for the new strictest Setpoint.
                Must be < 100 characters and not contain any EnergyPlus special
                characters. This will be used to identify the object across a model
                and in the exported IDF.
            setpoints: A list of Setpoint objects that will be evaluated into a
                new Setpoint that represents the strictest across the input.
            timestep_resolution: An optional integer for the timestep resolution
                at which the schedules will be resolved. Any schedule details smaller
                than this timestep will be lost in the process. (Default: 1).

        Returns:
            A Setpoint object that represents the strictest values between
            the input setpoints.
        """
        # calculate the strictest thermostat schedules
        heat_sched = Setpoint._max_schedule(
            '{}_HtgSetp Schedule'.format(identifier),
            [setp.heating_schedule for setp in setpoints], timestep_resolution)
        cool_sched = Setpoint._min_schedule(
            '{}_ClgSetp Schedule'.format(identifier),
            [setp.cooling_schedule for setp in setpoints], timestep_resolution)

        # calculate the strictest humidistat schedules
        humid_scheds = [sp.humidifying_schedule for sp in setpoints]
        if all(val is None for val in humid_scheds):
            humid_sched = None
            dehumid_sched = None
        else:
            dehumid_scheds = [sp.dehumidifying_schedule for sp in setpoints]
            humid_sch_id = '{}_Humid Schedule'.format(identifier)
            dehumid_sch_id = '{}_Dehumid Schedule'.format(identifier)
            for i, sch in enumerate(humid_scheds):
                if sch is None:
                    humid_scheds[i] = Setpoint._humidifying_schedule_no_limit
                    dehumid_scheds[i] = Setpoint._dehumidifying_schedule_no_limit
            humid_sched = Setpoint._max_schedule(
                humid_sch_id, humid_scheds, timestep_resolution)
            dehumid_sched = Setpoint._min_schedule(
                dehumid_sch_id, dehumid_scheds, timestep_resolution)

        # calculate the minimum setpoint_cutout_difference
        sp_cut = min(sp.setpoint_cutout_difference for sp in setpoints)

        # return the averaged object
        return Setpoint(identifier, heat_sched, cool_sched,
                        humid_sched, dehumid_sched, sp_cut)

    def _check_temperature_schedule_type(self, schedule, obj_name=''):
        """Check that the type limit of an input schedule is temperature."""
        assert isinstance(schedule, (ScheduleRuleset, ScheduleFixedInterval)), \
            'Expected ScheduleRuleset or ScheduleFixedInterval for {} ' \
            'schedule. Got {}.'.format(obj_name, type(schedule))
        if schedule.schedule_type_limit is not None:
            assert schedule.schedule_type_limit.unit == 'C', '{} schedule ' \
                'should be in Temperature units. Got a schedule of unit_type ' \
                '{}.'.format(obj_name, schedule.schedule_type_limit.unit_type)

    def _check_humidity_schedule_type(self, schedule, obj_name=''):
        """Check that the type limit of an input schedule is percent."""
        assert isinstance(schedule, (ScheduleRuleset, ScheduleFixedInterval)), \
            'Expected ScheduleRuleset or ScheduleFixedInterval for {} ' \
            'schedule. Got {}.'.format(obj_name, type(schedule))
        if schedule.schedule_type_limit is not None:
            t_lim = schedule.schedule_type_limit
            assert t_lim.unit == '%', '{} schedule should be in Percent units. ' \
                'Got a schedule of unit_type {}.'.format(obj_name, t_lim.unit_type)
            assert t_lim.lower_limit == 0, '{} schedule should have either no type ' \
                'limit or a lower limit of 0. Got a schedule type with lower limit ' \
                '[{}].'.format(obj_name, t_lim.lower_limit)
            assert t_lim.upper_limit == 100, '{} schedule should have either no type ' \
                'limit or an upper limit of 1. Got a schedule type with upper limit ' \
                '[{}].'.format(obj_name, t_lim.upper_limit)

    def _min_schedule_value(self, schedule):
        """Extract the minimum value from a schedule."""
        try:  # ScheduleRuleset
            vals = []
            for sch in schedule.typical_day_schedules:
                vals.extend(sch.values)
            return min(vals)
        except AttributeError:  # ScheduleFixedInterval
            return min(schedule.values)

    def _max_schedule_value(self, schedule):
        """Extract the maximum value from a schedule."""
        try:  # ScheduleRuleset
            vals = []
            for sch in schedule.typical_day_schedules:
                vals.extend(sch.values)
            return max(vals)
        except AttributeError:  # ScheduleFixedInterval
            return max(schedule.values)

    def __key(self):
        """A tuple based on the object properties, useful for hashing."""
        return (self.identifier, hash(self.heating_schedule), hash(self.cooling_schedule),
                hash(self.humidifying_schedule), hash(self.dehumidifying_schedule),
                self.setpoint_cutout_difference)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(other, Setpoint) and self.__key() == other.__key()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __copy__(self):
        new_obj = Setpoint(
            self.identifier, self.heating_schedule, self.cooling_schedule,
            self.humidifying_schedule, self.dehumidifying_schedule)
        new_obj._setpoint_cutout_difference = self._setpoint_cutout_difference
        new_obj._display_name = self._display_name
        new_obj._user_data = None if self._user_data is None else self._user_data.copy()
        new_obj._properties._duplicate_extension_attr(self._properties)
        return new_obj

    def __repr__(self):
        return 'Setpoint: {} [heating: {}C] [cooling: {}C]'.format(
            self.display_name, round(self.heating_setpoint, 1),
            round(self.cooling_setpoint, 1))

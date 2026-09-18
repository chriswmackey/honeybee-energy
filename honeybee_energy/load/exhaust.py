# coding=utf-8
"""Complete definition of ventilation in a simulation, including schedule and load."""
from __future__ import division

from honeybee._lockable import lockable
from honeybee.typing import float_positive, valid_string

from ._base import _LoadBase
from ..schedule.ruleset import ScheduleRuleset
from ..schedule.fixedinterval import ScheduleFixedInterval
from ..reader import parse_idf_string
from ..writer import generate_idf_string
from ..units import convert_ventilation_flow_per_person, \
    convert_ventilation_flow_per_area, convert_ventilation_flow_per_zone, \
    convert_ventilation_air_changes_per_hour
from ..lib.schedules import always_on
import honeybee_energy.lib.scheduletypelimits as _type_lib
from ..properties.extension import VentilationProperties


@lockable
class ExhaustAir(_LoadBase):
    """A complete definition of exhaust air, including schedules and load.

    Note the the 2 ventilation types (flow_per_area and flow_per_fixture) are
    ultimately added together to yield the final exhaust air flow rate used
    in the simulation.

    Args:
        identifier: Text string for a unique ExhaustAir ID. Must be < 100 characters
            and not contain any EnergyPlus special characters. This will be used to
            identify the object across a model and in the exported IDF.
        flow_per_area: A numerical value for the intensity of exhaust air ventilation
            in m3/s per square meter of floor area. (Default: 0).
        flow_per_fixture: A numerical value for the level of exhaust air ventilation
            in m3/s for each fixture in the room. The term "fixture" is used
            broadly as a way to reference a wide variety of contaminant sources
            such as toilets/urinals, shower heads, kitchen hoods, fume hoods,
            etc. (Default: 0).
        fixture_count: An integer for the number of fixtures in the space. This
            is multiplied by the flow_per_fixture, which is then added to the
            flow_per_area to yield the final exhaust air flow rate (Default: 1).
        schedule: An optional ScheduleRuleset or ScheduleFixedInterval for the
            exhaust air ventilation over the course of the year. The type of this
            schedule should be Fractional and the fractional values get multiplied by
            the total design flow rate to yield a complete ventilation profile.
            Values of 0 in the schedule will shut the fan off completely. If None,
            the design level of ventilation will be used throughout all timesteps
            of the simulation, meaning that this schedule is Always On. (Default: None).
        pressure_rise: A number for the the pressure rise across the fan in Pascals
            (N/m2). This is often a function of the fan speed and the conditions in
            which the fan is operating. It plays an important role in determining
            the amount of energy consumed by the fan. Typical kitchen and bathroom
            exhaust fans have pressure rises around 125 Pa but, in healthcare
            settings where filters create more resistance, higher pressures
            around 250 Pa are more common. (Default: 125).
        efficiency: A number between 0 and 1 for the overall efficiency of the fan.
            Specifically, this is the ratio of the power delivered to the fluid
            to the electrical input power. It is the product of the fan motor
            efficiency and the fan impeller efficiency.
            Fans that have a higher blade diameter, no obstructions or filters,
            and operate at lower speeds with smaller pressure rises for
            their size tend to have higher efficiencies. Because motor efficiencies
            are typically between 0.8 and 0.9, the best overall fan efficiencies
            tend to be around 0.7 with most typical fan efficiencies between 0.5 and
            0.7. When filters are added, which is common for most exhaust fans,
            the total efficiency typically ends up between 0.3 and 0.4. (Default: 0.35).

    Properties:
        * identifier
        * display_name
        * flow_per_area
        * flow_per_fixture
        * fixture_count
        * schedule
        * pressure_rise
        * efficiency
        * user_data
    """
    __slots__ = (
        '_flow_per_person', '_flow_per_area', '_flow_per_zone', '_air_changes_per_hour',
        '_schedule', '_method', '_effectiveness_cooling', '_effectiveness_heating',
        '_secondary_recirculation'
    )

    def __init__(
        self, identifier, flow_per_person=0, flow_per_area=0, flow_per_zone=0,
        air_changes_per_hour=0, schedule=None, method='Sum',
        effectiveness_cooling=1, effectiveness_heating=1, secondary_recirculation=0
    ):
        """Initialize Ventilation."""
        _LoadBase.__init__(self, identifier)
        self.flow_per_person = flow_per_person
        self.flow_per_area = flow_per_area
        self.flow_per_zone = flow_per_zone
        self.air_changes_per_hour = air_changes_per_hour
        self.schedule = schedule
        self.method = method
        self.effectiveness_cooling = effectiveness_cooling
        self.effectiveness_heating = effectiveness_heating
        self.secondary_recirculation = secondary_recirculation
        self._properties = VentilationProperties(self)
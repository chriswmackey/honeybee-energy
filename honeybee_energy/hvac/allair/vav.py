# coding=utf-8
"""Variable Air Volume (VAV) HVAC system."""
from __future__ import division

from ._base import _AllAirBase

from honeybee._lockable import lockable


@lockable
class VAV(_AllAirBase):
    """Variable Air Volume (VAV) HVAC system (aka. System 7 or 8).

    All rooms/zones are connected to a central air loop that is kept at a constant
    central temperature of 12.8C (55F). The central temperature is maintained by a
    cooling coil, which runs whenever the combination of return air and fresh outdoor
    air is greater than 12.8C, as well as a heating coil, which runs whenever
    the combination of return air and fresh outdoor air is less than 12.8C.

    Each air terminal for the connected rooms/zones contains its own reheat coil,
    which runs whenever the room is not in need of the cooling supplied by the 12.8C
    central air.

    The central cooling coil is always a chilled water coil, which is connected to a
    chilled water loop operating at 6.7C (44F). All heating coils are hot water coils
    except when Gas Coil equipment_type is used (in which case coils are gas)
    or when Parallel Fan-Powered (PFP) boxes equipment_type is used (in which case
    coils are electric resistance). Hot water temperature is 82C (180F) for
    boiler/district heating and 49C (120F) when ASHP is used.

    VAV systems are the traditional baseline system for commercial buildings
    taller than 5 stories or larger than 14,000 m2 (150,000 ft2) of floor area.

    Args:
        identifier: Text string for system identifier. Must be < 100 characters
            and not contain any EnergyPlus special characters. This will be used to
            identify the object across a model and in the exported IDF.
        vintage: Text for the vintage of the template system. This will be used
            to set efficiencies for various pieces of equipment within the system.
            Choose from the following.

            * DOE_Ref_Pre_1980
            * DOE_Ref_1980_2004
            * ASHRAE_2004
            * ASHRAE_2007
            * ASHRAE_2010
            * ASHRAE_2013
            * ASHRAE_2016
            * ASHRAE_2019

        equipment_type: Text for the specific type of the system and equipment. (Default:
            the first option below) Choose from.

            * VAV_Chiller_Boiler
            * VAV_Chiller_ASHP
            * VAV_Chiller_DHW
            * VAV_Chiller_PFP
            * VAV_Chiller_GasCoil
            * VAV_ACChiller_Boiler
            * VAV_ACChiller_ASHP
            * VAV_ACChiller_DHW
            * VAV_ACChiller_PFP
            * VAV_ACChiller_GasCoil
            * VAV_DCW_Boiler
            * VAV_DCW_ASHP
            * VAV_DCW_DHW
            * VAV_DCW_PFP
            * VAV_DCW_GasCoil

        economizer_type: Text to indicate the type of air-side economizer used on
            the system. (Default: NoEconomizer). Choose from the following.

            * NoEconomizer
            * DifferentialDryBulb
            * DifferentialEnthalpy
            * DifferentialDryBulbAndEnthalpy
            * FixedDryBulb
            * FixedEnthalpy
            * ElectronicEnthalpy

        sensible_heat_recovery: A number between 0 and 1 for the effectiveness
            of sensible heat recovery within the system. (Default: 0).
        latent_heat_recovery: A number between 0 and 1 for the effectiveness
            of latent heat recovery within the system. (Default: 0).
        demand_controlled_ventilation: Boolean to note whether demand controlled
            ventilation should be used on the system, which will vary the amount
            of ventilation air according to the occupancy schedule of the
            Rooms. (Default: False).

    Properties:
        * identifier
        * display_name
        * vintage
        * equipment_type
        * economizer_type
        * sensible_heat_recovery
        * latent_heat_recovery
        * demand_controlled_ventilation
        * schedules
        * has_district_heating
        * has_district_cooling
        * user_data
        * properties

    Note:
        [1] American Society of Heating, Refrigerating and Air-Conditioning Engineers,
        Inc. (2007). Ashrae standard 90.1. Atlanta, GA. https://www.ashrae.org/\
technical-resources/standards-and-guidelines/read-only-versions-of-ashrae-standards
    """
    __slots__ = ()

    EQUIPMENT_TYPES = (
        'VAV_Chiller_Boiler',
        'VAV_Chiller_ASHP',
        'VAV_Chiller_DHW',
        'VAV_Chiller_PFP',
        'VAV_Chiller_GasCoil',
        'VAV_ACChiller_Boiler',
        'VAV_ACChiller_ASHP',
        'VAV_ACChiller_DHW',
        'VAV_ACChiller_PFP',
        'VAV_ACChiller_GasCoil',
        'VAV_DCW_Boiler',
        'VAV_DCW_ASHP',
        'VAV_DCW_DHW',
        'VAV_DCW_PFP',
        'VAV_DCW_GasCoil'
    )

# coding=utf-8
"""Fan Coil Unit (FCU) with DOAS HVAC system."""
from __future__ import division

from ._base import _DOASBase

from honeybee._lockable import lockable


@lockable
class FCUwithDOAS(_DOASBase):
    """Fan Coil Unit (FCU) with DOAS HVAC system.

    All rooms/zones in the system are connected to a Dedicated Outdoor Air System
    (DOAS) that supplies a constant volume of ventilation air at the same temperature
    to all rooms/zones. The ventilation air temperature will vary from 21.1C (70F)
    to 15.5C (60F) depending on the outdoor air temperature (the DOAS supplies cooler air
    when outdoor conditions are warmer). The ventilation air temperature is maintained
    by a chilled water cooling coil and a heating coil. The heating coil is a hot
    water coil except when electric baseboards or gas heaters are specified, in
    which case the heating coil is a single-speed direct expansion (DX) heat pump
    with a backup electrical resistance coil.

    Each room/zone also receives its own Fan Coil Unit (FCU), which meets the heating
    and cooling loads of the space. The cooling coil in the FCU is always chilled
    water cooling coil, which is connected to a chilled water loop operating
    at 6.7C (44F). The heating coil is a hot water coil except when when electric
    baseboards or gas heaters are specified. Hot water temperature is 82C (180F) for
    boiler/district heating and 49C (120F) when ASHP is used.

    The FCU with DOAS template is relatively close in performance to active chilled
    beams (ACBs). When using this template to represent ACBs, care must be taken
    to ensure that the DOAS ventilation air requirement is sufficient to extract
    the heating cooling from the ACB. If so, then this FCUwithDOAS template can be
    used but with the energy use of the FCU fans ignored.

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

            * DOAS_FCU_Chiller_Boiler
            * DOAS_FCU_Chiller_ASHP
            * DOAS_FCU_Chiller_DHW
            * DOAS_FCU_Chiller_ElectricBaseboard
            * DOAS_FCU_Chiller_GasHeaters
            * DOAS_FCU_Chiller
            * DOAS_FCU_ACChiller_Boiler
            * DOAS_FCU_ACChiller_ASHP
            * DOAS_FCU_ACChiller_DHW
            * DOAS_FCU_ACChiller_ElectricBaseboard
            * DOAS_FCU_ACChiller_GasHeaters
            * DOAS_FCU_ACChiller
            * DOAS_FCU_DCW_Boiler
            * DOAS_FCU_DCW_ASHP
            * DOAS_FCU_DCW_DHW
            * DOAS_FCU_DCW_ElectricBaseboard
            * DOAS_FCU_DCW_GasHeaters
            * DOAS_FCU_DCW

        sensible_heat_recovery: A number between 0 and 1 for the effectiveness
            of sensible heat recovery within the system. (Default: 0).
        latent_heat_recovery: A number between 0 and 1 for the effectiveness
            of latent heat recovery within the system. (Default: 0).
        demand_controlled_ventilation: Boolean to note whether demand controlled
            ventilation should be used on the system, which will vary the amount
            of ventilation air according to the occupancy schedule of the
            Rooms. (Default: False).
        doas_availability_schedule: An optional On/Off discrete schedule to set when
            the dedicated outdoor air system (DOAS) shuts off. This will not only
            prevent any outdoor air from flowing thorough the system but will also
            shut off the fans, which can result in more energy savings when spaces
            served by the DOAS are completely unoccupied. If None, the DOAS will be
            always on. (Default: None).

    Properties:
        * identifier
        * display_name
        * vintage
        * equipment_type
        * sensible_heat_recovery
        * latent_heat_recovery
        * demand_controlled_ventilation
        * doas_availability_schedule
        * schedules
        * has_district_heating
        * has_district_cooling
        * user_data
        * properties
    """
    __slots__ = ()

    EQUIPMENT_TYPES = (
        'DOAS_FCU_Chiller_Boiler',
        'DOAS_FCU_Chiller_ASHP',
        'DOAS_FCU_Chiller_DHW',
        'DOAS_FCU_Chiller_ElectricBaseboard',
        'DOAS_FCU_Chiller_GasHeaters',
        'DOAS_FCU_Chiller',
        'DOAS_FCU_ACChiller_Boiler',
        'DOAS_FCU_ACChiller_ASHP',
        'DOAS_FCU_ACChiller_DHW',
        'DOAS_FCU_ACChiller_ElectricBaseboard',
        'DOAS_FCU_ACChiller_GasHeaters',
        'DOAS_FCU_ACChiller',
        'DOAS_FCU_DCW_Boiler',
        'DOAS_FCU_DCW_ASHP',
        'DOAS_FCU_DCW_DHW',
        'DOAS_FCU_DCW_ElectricBaseboard',
        'DOAS_FCU_DCW_GasHeaters',
        'DOAS_FCU_DCW'
    )

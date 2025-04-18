"""Tests the features that honeybee_energy adds to honeybee_core Shade."""
from honeybee.shademesh import ShadeMesh

from honeybee_energy.properties.shademesh import ShadeMeshEnergyProperties
from honeybee_energy.construction.shade import ShadeConstruction
from honeybee_energy.schedule.ruleset import ScheduleRuleset

import honeybee_energy.lib.scheduletypelimits as schedule_types

from ladybug_geometry.geometry3d import Point3D, Mesh3D


def test_energy_properties():
    """Test the existence of the ShadeMesh energy properties."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh)

    assert hasattr(shade.properties, 'energy')
    assert isinstance(shade.properties.energy, ShadeMeshEnergyProperties)
    assert isinstance(shade.properties.energy.construction, ShadeConstruction)


def test_default_properties():
    """Test the auto-assigning of shade mesh properties."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh)
    in_shade = ShadeMesh('Awning_1', mesh, is_detached=False)

    assert shade.properties.energy.transmittance_schedule is None
    assert shade.properties.energy.construction.solar_reflectance == 0.2
    assert shade.properties.energy.construction.visible_reflectance == 0.2
    assert not shade.properties.energy.construction.is_specular
    assert shade.properties.energy.transmittance_schedule is None

    assert in_shade.properties.energy.construction.solar_reflectance == 0.35
    assert in_shade.properties.energy.construction.visible_reflectance == 0.35
    assert not in_shade.properties.energy.construction.is_specular


def test_set_construction():
    """Test the setting of construction on a ShadeMesh."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh)

    light_shelf_construction = ShadeConstruction('Light Shelf', 0.5, 0.5, True)

    shade.properties.energy.construction = light_shelf_construction
    assert shade.properties.energy.construction == light_shelf_construction

    assert shade.properties.energy.construction.solar_reflectance == 0.5
    assert shade.properties.energy.construction.visible_reflectance == 0.5
    assert shade.properties.energy.construction.is_specular


def test_set_transmittance_schedule():
    """Test the setting of transmittance_schedule on a ShadeMesh."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh)

    fritted_glass_trans = ScheduleRuleset.from_constant_value(
        'Fritted Glass', 0.5, schedule_types.fractional)

    shade.properties.energy.transmittance_schedule = fritted_glass_trans
    assert shade.properties.energy.transmittance_schedule == fritted_glass_trans


def test_duplicate():
    """Test what happens to energy properties when duplicating a ShadeMesh."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade_original = ShadeMesh('Awning_1', mesh)
    shade_dup_1 = shade_original.duplicate()
    light_shelf = ShadeConstruction('Light Shelf', 0.5, 0.5, True)
    bright_light_shelf = ShadeConstruction('Bright Light Shelf', 0.7, 0.7, True)
    fritted_glass_trans = ScheduleRuleset.from_constant_value(
        'Fritted Glass', 0.5, schedule_types.fractional)

    assert shade_original.properties.energy.host is shade_original
    assert shade_dup_1.properties.energy.host is shade_dup_1
    assert shade_original.properties.energy.host is not \
        shade_dup_1.properties.energy.host

    assert shade_original.properties.energy.construction == \
        shade_dup_1.properties.energy.construction
    shade_dup_1.properties.energy.construction = light_shelf
    assert shade_original.properties.energy.construction != \
        shade_dup_1.properties.energy.construction

    shade_dup_2 = shade_dup_1.duplicate()

    assert shade_dup_1.properties.energy.construction == \
        shade_dup_2.properties.energy.construction
    shade_dup_2.properties.energy.construction = bright_light_shelf
    assert shade_dup_1.properties.energy.construction != \
        shade_dup_2.properties.energy.construction

    assert shade_original.properties.energy.transmittance_schedule == \
        shade_dup_1.properties.energy.transmittance_schedule
    shade_dup_1.properties.energy.transmittance_schedule = fritted_glass_trans
    assert shade_original.properties.energy.transmittance_schedule != \
        shade_dup_1.properties.energy.transmittance_schedule

    shade_dup_3 = shade_dup_1.duplicate()

    assert shade_dup_1.properties.energy.transmittance_schedule == \
        shade_dup_3.properties.energy.transmittance_schedule
    shade_dup_3.properties.energy.transmittance_schedule = None
    assert shade_dup_1.properties.energy.transmittance_schedule != \
        shade_dup_3.properties.energy.transmittance_schedule


def test_to_dict():
    """Test the ShadeMesh to_dict method with energy properties."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh)

    shade_dict = shade.to_dict()
    assert 'properties' in shade_dict
    assert shade_dict['properties']['type'] == 'ShadeMeshProperties'
    assert 'energy' in shade_dict['properties']
    assert shade_dict['properties']['energy']['type'] == 'ShadeMeshEnergyProperties'

    light_shelf = ShadeConstruction('Light Shelf', 0.5, 0.5, True)
    shade.properties.energy.construction = light_shelf
    shade_dict = shade.to_dict()
    assert 'construction' in shade_dict['properties']['energy']
    assert shade_dict['properties']['energy']['construction']['solar_reflectance'] == 0.5
    assert shade_dict['properties']['energy']['construction']['visible_reflectance'] == 0.5
    assert shade_dict['properties']['energy']['construction']['is_specular']

    fritted_glass_trans = ScheduleRuleset.from_constant_value(
        'Fritted Glass', 0.5, schedule_types.fractional)
    shade.properties.energy.transmittance_schedule = fritted_glass_trans
    shade_dict = shade.to_dict()
    assert 'transmittance_schedule' in shade_dict['properties']['energy']
    assert shade_dict['properties']['energy']['transmittance_schedule'] is not None


def test_from_dict():
    """Test the ShadeMesh from_dict method with energy properties."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh)
    light_shelf = ShadeConstruction('Light Shelf', 0.5, 0.5, True)
    shade.properties.energy.construction = light_shelf
    fritted_glass_trans = ScheduleRuleset.from_constant_value(
        'Fritted Glass', 0.5, schedule_types.fractional)
    shade.properties.energy.transmittance_schedule = fritted_glass_trans

    shade_dict = shade.to_dict()
    new_shade = ShadeMesh.from_dict(shade_dict)
    assert new_shade.properties.energy.construction == light_shelf
    assert shade.properties.energy.construction.solar_reflectance == 0.5
    assert shade.properties.energy.construction.visible_reflectance == 0.5
    assert shade.properties.energy.construction.is_specular
    assert new_shade.properties.energy.transmittance_schedule == fritted_glass_trans
    assert new_shade.to_dict() == shade_dict


def test_writer_to_idf():
    """Test the ShadeMesh to_idf method."""
    pts = (Point3D(0, 0, 4), Point3D(0, 2, 4), Point3D(2, 2, 4),
           Point3D(2, 0, 4), Point3D(4, 0, 4))
    mesh = Mesh3D(pts, [(0, 1, 2, 3), (2, 3, 4)])
    shade = ShadeMesh('Awning_1', mesh)

    assert hasattr(shade.to, 'idf')
    idf_string = shade.to.idf(shade)
    assert 'Awning_1' in idf_string
    assert 'Shading:Building:Detailed,' in idf_string
    assert 'ShadingProperty:Reflectance' not in idf_string

    shade = ShadeMesh('Awning_2', mesh)
    light_shelf = ShadeConstruction('Light Shelf', 0.5, 0.5, True)
    shade.properties.energy.construction = light_shelf
    fritted_glass_trans = ScheduleRuleset.from_constant_value(
        'FrittedGlass', 0.5, schedule_types.fractional)
    shade.properties.energy.transmittance_schedule = fritted_glass_trans

    assert hasattr(shade, 'to_idf')
    idf_string = shade.to_idf()
    assert 'Awning_2' in idf_string
    assert 'Shading:Building:Detailed,' in idf_string
    assert 'ShadingProperty:Reflectance' in idf_string
    assert 'FrittedGlass' in idf_string

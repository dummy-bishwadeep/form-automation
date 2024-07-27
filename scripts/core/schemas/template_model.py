from enum import Enum


class HierarchyLevelEnum(str, Enum):
    site = 'Site'
    section = 'Section'
    department = 'Department'
    line = 'Line'
    equipment = 'Equipment'
    l1 = 'L1'
    l2 = 'L2'
    l3 = 'L3'
    l4 = 'L4'
    l5 = 'L5'

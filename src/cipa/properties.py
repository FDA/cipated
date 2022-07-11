from enum import Enum


class Property_Type(Enum):
    """Types of cell properties
    """
    CIPA_PROPERTY_INPUT_RESISTANCE = 1
    CIPA_PROPERTY_MEMBRANE_CAPACITANCE = 2
    CIPA_PROPERTY_MEMBRANE_RESISTANCE = 3
    CIPA_PROPERTY_MEMBRANE_RESTING_POTENTIAL = 4
    CIPA_PROPERTY_PASSAGE_NUMBER = 5
    CIPA_PROPERTY_SEAL_RESISTANCE = 6
    CIPA_PROPERTY_SERIES_RESISTANCE = 7
    CIPA_PROPERTY_SERIES_RESISTANCE_COMPENSATION = 8
    CIPA_PROPERTY_TEMPERATURE = 9
    CIPA_PROPERTY_UNKNOWN = 10

class Property:
    """Cell property

    Attributes:
        code (Property_Type): type of cell property to be used as PARAMCD in 
            TED files
        displayName (str): string to use when printing the cell property (i.e.,
            as PARAM in TED files)
        propertyType (Property_Type): this is used to handle missmatches (i.e.,
            unknown PARAMCD properties) when reading from TED files. Defatuls
            to Property_Type.CIPA_PROPERTY_UNKNOWN.
        value (str): value of the property
        unit (str): unit of the value of the property
        description (str): additional description or notes
    """
    def __init__(
        self, code: Property_Type,
        displayName: str = '',
        propertyType: Property_Type = Property_Type.CIPA_PROPERTY_UNKNOWN,
        value: str = '',
        unit: str ='',
        description: str = ''
    ):
        self.code = code  # PARAMCD in TED
        self.displayName = displayName  # PARAM in TED
        self.propertyType = propertyType
        self.value = value  # VALUE in TED
        self.unit = unit  # UNIT in TED
        self.description = description
        
# Dictionary mapping PARAMCDs in TED format to Property_Type
propertiesDict = {
    'Cm': Property_Type.CIPA_PROPERTY_MEMBRANE_CAPACITANCE,
    'P': Property_Type.CIPA_PROPERTY_PASSAGE_NUMBER,
    'Rm': Property_Type.CIPA_PROPERTY_MEMBRANE_RESISTANCE,
    'Rs': Property_Type.CIPA_PROPERTY_SERIES_RESISTANCE,
    'Rseal': Property_Type.CIPA_PROPERTY_SEAL_RESISTANCE,
    'Temperature': Property_Type.CIPA_PROPERTY_TEMPERATURE,
    'Vm': Property_Type.CIPA_PROPERTY_MEMBRANE_RESTING_POTENTIAL}

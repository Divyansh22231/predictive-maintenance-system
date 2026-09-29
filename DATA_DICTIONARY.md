Column Name: UID
Data Type: Integer
Meaning: Row identifier.
Example Value: 1
Role: Identifier

Column Name: Product ID
Data Type: Categorical (string)
Meaning: Product identifier consisting of a letter and a serial number.
Example Value: M14860
Role: Identifier

Column Name: Type
Data Type: Categorical
Meaning: Product quality variant (L / M / H).
Example Value: M
Role: Input feature

Column Name: Air temperature [K]
Data Type: Continuous
Meaning: Ambient air temperature measured in Kelvin.
Example Value: 298.1
Role: Input feature

Column Name: Process temperature [K]
Data Type: Continuous
Meaning: Operating temperature measured in Kelvin.
Example Value: 308.6
Role: Input feature

Column Name: Rotational speed [rpm]
Data Type: Integer
Meaning: Speed of the machine in rotations per minute.
Example Value: 1551
Role: Input feature

Column Name: Torque [Nm]
Data Type: Continuous
Meaning: Rotational force in Newton-metres (closest analogue to load).
Example Value: 42.8
Role: Input feature

Column Name: Tool wear [min]
Data Type: Integer
Meaning: Usage time of the tool in minutes (closest analogue to tool age).
Example Value: 0
Role: Input feature

Column Name: Machine failure
Data Type: Binary (0/1)
Meaning: Main classification target indicating whether a failure occurred.
Example Value: 0
Role: Target

Column Name: TWF
Data Type: Binary (0/1)
Meaning: Tool Wear Failure.
Example Value: 0
Role: Sub-label — excluded from input features due to data leakage (these columns are components used to derive Machine failure itself)

Column Name: HDF
Data Type: Binary (0/1)
Meaning: Heat Dissipation Failure.
Example Value: 0
Role: Sub-label — excluded from input features due to data leakage (these columns are components used to derive Machine failure itself)

Column Name: PWF
Data Type: Binary (0/1)
Meaning: Power Failure.
Example Value: 0
Role: Sub-label — excluded from input features due to data leakage (these columns are components used to derive Machine failure itself)

Column Name: OSF
Data Type: Binary (0/1)
Meaning: Overstrain Failure.
Example Value: 0
Role: Sub-label — excluded from input features due to data leakage (these columns are components used to derive Machine failure itself)

Column Name: RNF
Data Type: Binary (0/1)
Meaning: Random Failure.
Example Value: 0
Role: Sub-label — excluded from input features due to data leakage (these columns are components used to derive Machine failure itself)

# ParameterList
Lookup table for parameter names used in ModeledParameters. The *parameter* name is required to be unique.


Columns marked with an exclamation mark (❗️) may not be empty.
| Column Name | Description | Datatype | Length | Units  | UCD |
| --- | --- | --- | --- | --- | --- |
| ❗️ <ins>parameter</ins> | Short name for a parameter | string | 30 |  | meta.id;meta.main  |
| description | Description of the parameter | string | 100 |  | meta.note  |

## Indexes
| Name | Columns | Description |
| --- | --- | --- |
| PK_ParameterList | ['#ParameterList.parameter'] | Primary key for ParameterList table |


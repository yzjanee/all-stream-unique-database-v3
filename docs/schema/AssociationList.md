# AssociationList
Lookup table for stellar stream and association names. The *association* name is required to be unique.


Columns marked with an exclamation mark (❗️) may not be empty.
| Column Name | Description | Datatype | Length | Units  | UCD |
| --- | --- | --- | --- | --- | --- |
| ❗️ <ins>association</ins> | Name of the stellar stream or association | string | 100 |  | meta.id;meta.main  |
| association_type | Type of association (e.g., stellar stream, open cluster, moving group) | string | 30 |  |   |
| comments | Free-form comments for this entry | string | 100 |  | meta.note  |
| reference | Publication reference; links to Publications table | string | 30 |  | meta.ref  |

## Indexes
| Name | Columns | Description |
| --- | --- | --- |
| PK_AssociationList | ['#AssociationList.association'] | Primary key for AssociationList table |

## Foreign Keys
| Description | Columns | Referenced Columns |
| --- | --- | --- |
| Link AssociationList reference to Publications table | ['#AssociationList.reference'] | ['#Publications.reference'] |

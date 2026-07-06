# Associations
Stream membership for sources. The combination of *source* and *association* is expected to be unique.


Columns marked with an exclamation mark (❗️) may not be empty.
| Column Name | Description | Datatype | Length | Units  | UCD |
| --- | --- | --- | --- | --- | --- |
| ❗️ <ins>source</ins> | Main identifier for an object; links to Sources table | string | 100 |  | meta.id;meta.main  |
| ❗️ <ins>association</ins> | Association name; links to AssociationList table | string | 100 |  | meta.id  |
| membership_probability | Probability of membership in this association (nullable; not all streams provide this) | double |  |  | stat.probability  |
| adopted | Flag to indicate if this is the adopted entry | boolean |  |  | meta.code  |
| comments | Free-form comments; second reference stored here for multi-reference rows | string | 100 |  | meta.note  |
| ❗️ reference | Publication reference; links to Publications table | string | 30 |  | meta.ref  |

## Indexes
| Name | Columns | Description |
| --- | --- | --- |
| PK_Associations | ['#Associations.source', '#Associations.association'] | Primary key for Associations table |

## Foreign Keys
| Description | Columns | Referenced Columns |
| --- | --- | --- |
| Link Associations source to Sources table | ['#Associations.source'] | ['#Sources.source'] |
| Link Associations association to AssociationList table | ['#Associations.association'] | ['#AssociationList.association'] |
| Link Associations reference to Publications table | ['#Associations.reference'] | ['#Publications.reference'] |
## Checks
| Description | Expression |
| --- | --- |
| Validate membership probability range | membership_probability >= 0 AND membership_probability <= 1 |

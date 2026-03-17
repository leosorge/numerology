# Numerology API contract (text/date/both)

This is a reference contract for a Flask endpoint that supports three modes:

- `text`: only name/surname analysis
- `date`: only birth number analysis (numeric string, **no date validation**)
- `both`: run both analyses

## Endpoint

`POST /api/numerology`

## Request payload

```json
{
  "mode": "both",
  "name": "Mario",
  "surname": "Rossi",
  "birth_number": "10121990"
}



TARGET_SCHEMA = [
    "origin_port",
    "destination_port",
    "container_type_20gp_rate",
    "container_type_40hq_rate",
    "estimated_time_of_departure",
    "transit_time_days",
    "currency"
]

CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CNY", "AUD", "CAD", "CHF", "HKD", "SGD"}

FIELD_KNOWLEDGE_BASE = {
    "origin_port": [
        "origin port", "port of loading", "load port", "loading port", # "pol",
        "departure port", "source port", "from port", "shipper port",
        "port of origin", "place of receipt", "por"
    ],
    "destination_port": [
        "destination port", "discharge port", "pod", "port of discharge",
        "delivery port", "arrival port", "to port", "consignee port",
        "destination", "place of delivery", "final port", "disport"
    ],
    "container_type_20gp_rate": [
        "20gp", "20 gp", "20ft", "20 ft", "20 foot", "twenty foot",
        "20gp rate", "20 gp rate", "teu rate", "teu", "twenty equivalent unit",
        "20 general purpose", "20gp freight", "20 dry", "rate 20"
    ],
    "container_type_40hq_rate": [
        "40hq", "40 hq", "40ft hq", "40 high cube", "40hc", "40 hc",
        "40hq rate", "40 hq rate", "high cube rate", "40 high", "feu rate",
        "40hq freight", "40 cube", "rate 40hq", "forty high cube"
    ],
    "estimated_time_of_departure": [
        "etd", "estimated departure", "departure date", "sailing date",
        "vessel departure", "expected departure", "cutoff date", "sail date",
        "scheduled departure", "departure time", "vessel etd", "est departure"
    ],
    "transit_time_days": [
        "transit time", "transit days", "tt", "sailing time", "travel time",
        "voyage days", "journey time", "shipping days", "days in transit",
        "lead time", "delivery days", "transit period", "number of days"
    ],
    "currency": [
        "currency", "curr", "ccy", "currency code", "payment currency",
        "freight currency", "rate currency", "usd", "eur", "inr",
        "denomination", "monetary unit", "fx", "forex"
    ]
}
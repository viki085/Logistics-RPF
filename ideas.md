This is a project named Logistics RFP Column Normalization. 

The background for the project is in the logistics industry. Shippers provide RFP (request for proposal) files in highly non-standard formats. These files vary in:
- column naming conventions
- abbreviations
- terminology
- formatting
- structure

Each freight forwarder maintains a standardized internal schema used for pricing, routing, analytics, and operating systems.

The objective is to design and implement a system in Python that automatically maps arbitrary shipper RFP column headers to the following internal target schema. The target schema fields are:
- origin_port
- destination_port
- container_type_20gp_rate
- container_type_20hq_rate
- estimated_time_of_departure
- transit_time_days
- currency

Here are some examples of input to target mapping. 

Example 1

| Input Column     | Mapped Target Field              |
|------------------|----------------------------------|
| Orig Port        | origin_port                      |
| Destination      | destination_port                 |
| 20GP             | container_type_20gp_rate         |
| 40HQ Rate        | container_type_40hq_rate         |
| ETD              | estimated_time_of_departure      |
| Transit (days)   | transit_time_days                |
| Currency         | currency                         |

---

Example 2

| Input Column | Mapped Target Field              |
|--------------|----------------------------------|
| POL          | origin_port                      |
| POD          | destination_port                 |
| Rate_20      | container_type_20gp_rate         |
| Rate_40HC    | container_type_40hq_rate         |
| Departure    | estimated_time_of_departure      |
| T/T          | transit_time_days                |
| Curr         | currency                         |

---

Example 3

| Input Column     | Mapped Target Field              |
|------------------|----------------------------------|
| Load Port        | origin_port                      |
| Discharge Port   | destination_port                 |
| 20’              | container_type_20gp_rate         |
| 40’ HC           | container_type_40hq_rate         |
| Sailing Date     | estimated_time_of_departure      |
| Duration         | transit_time_days                |
| Rate Currency    | currency                         |

---
Example 4 - Complex Case

Input Columns: From, To, 20FT USD, 40FT, ETD (YYYYMMDD), Transit, CCY Potential Challenges include: combined container type and currency in one column, ambiguous container types, textual transit durations, and embedded metadata.


Requirements

- Implementation must be in Python
- You can use open source libraries
- You may use LLM APIs where necessary. 
- The system must generalize to unseen RFP formats.
- Provide confidence scores for mappings. 
- Design for minimal manual intervention.

Data Ingestion:

- Load data from files (csv/excel)
- Preprocess data column names for normalization
- Perform checks for schema compliance and merged columns 

Mapping Strategies:

- Use fuzzy matching to handle typos and variations
- Create a knowledge base of common abbreviations and synonyms
- Sentence Transformers for semantic similarity (HuggingFace API Call needed)
- Use LLM to map column headers to target schema (OpenAI API Call needed)

Scoring:
- Compute similarity scores between input columns and target schema.
- If similarity score is above a certain threshold after inital mappling stratergies,
  use LLM to map the column to the target schema.
- If similarity score is still below a certain threshold after LLM mapping, flag the column for manual review.

Output:
- Return a JSON log file with the mapped column headers and their confidence scores.
- Store unmapped columns in a seperate folder for review.
- Return processed files.

Additional Changes:
- Fix merged column data into separate columns
- Update Knowledge Base(schema) with new mappings obtained from LLM call.



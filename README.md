# Skylark Business Intelligence Agent

An AI-powered Business Intelligence Agent that connects to monday.com Work Orders and Deals boards and answers business questions using live board data.

## Overview

This project was developed as a technical assignment for Skylark Drones.

The system connects to two monday.com boards:

1. Work Order Tracker
2. Deal Funnel

The application dynamically retrieves data from monday.com through the monday.com MCP endpoint, processes and cleans the data using Python and Pandas, and provides business-oriented answers through a Streamlit web interface.

## Architecture

```text
                    ┌──────────────────────┐
                    │      User Query      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Streamlit App      │
                    │       app.py         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Query Engine      │
                    │   query_engine.py    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Data Processor     │
                    │  data_processor.py   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    monday.com MCP    │
                    │  Live Board Data     │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
        ┌───────────────┐             ┌───────────────┐
        │ Work Orders   │             │     Deals     │
        │     Board     │             │     Board     │
        └───────────────┘             └───────────────┘
```

## Key Features

- Live connection to monday.com
- Dynamic retrieval of board data
- Separate Work Orders and Deals datasets
- Pagination support for retrieving all board items
- Dynamic column mapping
- Data cleaning and normalization
- Date and numeric type conversion
- Business question answering
- Pipeline health summary
- Open pipeline value calculation
- Work order operational metrics
- Sector-level analysis
- Streamlit dashboard
- Hosted web application ready for deployment

## Current Business Questions Supported

The agent can answer questions such as:

### Work Orders

```text
How many work orders are there?
```

```text
How many completed work orders are there?
```

```text
How many ongoing work orders are there?
```

```text
How many work orders are billed?
```

```text
What sectors are we working in?
```

### Deals

```text
How many open deals are there?
```

```text
How many won deals are there?
```

```text
Show me deals by sector
```

```text
How many total deals are there?
```

### Pipeline

```text
Give me a pipeline summary
```

```text
What is the open pipeline value?
```

## Data Processing

The system performs several data preparation steps before answering questions.

### Text Cleaning

Text values are stripped of unnecessary whitespace and known accidental header-like values are treated as missing data.

For example, accidental values such as:

```text
Deal Status
Deal Stage
Sector/service
```

appearing as data values are converted to missing values where appropriate.

Known text inconsistencies such as:

```text
BIlled
```

are normalized to:

```text
Billed
```

### Date Processing

Relevant date columns are converted to Pandas datetime values.

Invalid or incomplete dates are converted to missing values rather than causing the application to fail.

### Numeric Processing

Financial and quantity fields are converted from string representations into numeric values.

This allows the application to perform calculations such as pipeline value and operational metrics.

## Data Quality Considerations

The source datasets contain real-world inconsistencies and incomplete records.

Important observations include:

- Some Work Order billing fields are missing.
- Some deal fields contain missing values.
- Some records contain inconsistent text values.
- Date fields may contain incomplete or invalid values.
- Financial values are masked/internal values.
- Billing status is incomplete for a significant portion of Work Orders.

The application therefore avoids assuming that missing values represent zero.

Data quality limitations should be considered when interpreting business metrics.

## Current Dataset Snapshot

The connected monday.com boards currently contain:

| Dataset | Records |
|---|---:|
| Work Orders | 176 |
| Deals | 346 |

Current operational snapshot from the connected data includes:

| Metric | Value |
|---|---:|
| Completed Work Orders | 117 |
| Ongoing Work Orders | 25 |
| Billed Work Orders | 3 |
| Open Deals | 49 |
| Won Deals | 165 |
| Dead Deals | 127 |
| On Hold Deals | 2 |
| Open Pipeline Value | ₹688,152,293.17 |

These values are based on the connected dataset at development/testing time and may change as monday.com data changes.

## Sector Analysis

### Work Orders

The current Work Order distribution includes:

```text
Mining: 100
Renewables: 51
Railways: 13
Powerline: 6
Others: 4
Construction: 2
```

### Deals

The current Deal distribution includes:

```text
Renewables: 111
Mining: 106
Railways: 40
Others: 28
Powerline: 26
Construction: 9
DSP: 7
Tender: 5
Manufacturing: 2
Security and Surveillance: 1
Aviation: 1
```

## Project Structure

```text
Skylark-BI-Agent/
│
├── app.py
├── app_test.py
├── data_processor.py
├── data_loader.py
├── query_engine.py
├── column_mapping.py
├── board_info.py
├── get_boards.py
├── test_mcp.py
├── test_monday.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

The `.env` file is intentionally excluded from GitHub because it contains the monday.com API credentials.

## File Descriptions

### `app.py`

Main Streamlit application.

It:

- Connects to monday.com
- Loads live data
- Displays KPI metrics
- Accepts user questions
- Sends questions to the query engine
- Displays answers

### `data_processor.py`

Responsible for:

- Connecting to monday.com MCP
- Retrieving all board items
- Handling pagination
- Dynamically retrieving board columns
- Converting board items into Pandas DataFrames
- Cleaning text values
- Converting dates and numeric fields

### `query_engine.py`

Contains the business question answering logic.

It processes user questions and calculates metrics from the live DataFrames.

### `data_loader.py`

Utility functions for loading board data.

### `column_mapping.py`

Utility for inspecting and mapping monday.com column IDs to human-readable column names.

### `app_test.py`

Local integration test for the complete data-loading and query pipeline.

### `test_mcp.py`

Tests the connection to monday.com MCP.

### `test_monday.py`

Tests the monday.com API connection.

### `get_boards.py`

Used to inspect available monday.com boards.

### `board_info.py`

Utility for inspecting board information.

## Technology Stack

- Python
- Streamlit
- Pandas
- monday.com
- monday.com MCP
- HTTPX
- Requests
- Python dotenv

## Environment Variables

Create a `.env` file locally containing:

```text
MONDAY_API_TOKEN=your_monday_api_token
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
DEALS_BOARD_ID=your_deals_board_id
```

Do not commit the `.env` file to GitHub.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/nkumarreddy/Skylark-BI-Agent.git
cd Skylark-BI-Agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows:

```powershell
.\venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file:

```text
MONDAY_API_TOKEN=your_monday_api_token
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
DEALS_BOARD_ID=your_deals_board_id
```

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in the browser.

## Testing

The complete local pipeline can be tested using:

```bash
python app_test.py
```

The test verifies:

- monday.com MCP connection
- Work Order retrieval
- Deal retrieval
- Data processing
- Query engine responses

## Deployment

The application can be deployed using a cloud platform such as Render.

Recommended configuration:

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

The following environment variables must be configured in the deployment platform:

```text
MONDAY_API_TOKEN
WORK_ORDERS_BOARD_ID
DEALS_BOARD_ID
```

The API token should be stored as a deployment secret/environment variable and should never be committed to the repository.

## Security

The monday.com API token is treated as a secret.

The project uses environment variables rather than hardcoding credentials.

The `.gitignore` file excludes:

```text
.env
venv/
__pycache__/
*.pyc
.streamlit/
```

## Design Decisions

### Dynamic Data Retrieval

The application does not hardcode the datasets into the application.

Data is retrieved dynamically from monday.com at runtime.

### Pagination

Board data is retrieved page-by-page so that the application can process boards containing more records than a single API response.

### Dynamic Column Mapping

Column IDs from monday.com are mapped dynamically to column names instead of relying entirely on fixed column IDs.

This makes the data processing layer more resilient to board configuration changes.

### Read-Only Architecture

The prototype reads information from monday.com and does not modify board records.

### Data Quality

The application performs basic cleaning and type conversion while retaining missing values where the source data is incomplete.

## Limitations

The current prototype uses a lightweight rule-based query engine for the supported business questions.

More advanced natural-language understanding could be added using an LLM-based agent.

Potential future improvements include:

- LLM-powered query interpretation
- Automatic clarification questions
- More advanced cross-board analysis
- Revenue and collection analysis
- Time-based trend analysis
- Interactive charts
- Automated anomaly detection
- More sophisticated data-quality reporting
- Role-based access control
- More robust natural-language query planning

## Future Improvements With More Development Time

With additional development time, the system could be extended to:

1. Introduce an LLM agent for natural-language business queries.
2. Generate SQL/Pandas-style analytical plans dynamically.
3. Add confidence and data-quality indicators to answers.
4. Add visual dashboards for pipeline and operations.
5. Support more complex cross-board questions.
6. Add automated insight generation.
7. Add caching and more efficient incremental data retrieval.
8. Add authentication for the hosted application.

## Assignment Submission

The main deliverables are:

- Hosted Streamlit prototype
- Source code repository
- README documentation
- Decision Log

Repository:

```text
https://github.com/nkumarreddy/Skylark-BI-Agent
```

---


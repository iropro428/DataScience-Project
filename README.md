# From Streams to Stages
## To what extent do digital streaming metrics predict the physical reality of global concert tours?

## Project overview
This project examines whether digital music success is reflected in real-world touring activity. It combines data from **Last.fm**, **Ticketmaster**, **Spotify Weekly Charts**, and a **capital city dataset** to analyze how artists' online popularity relates to the scale, geography, and timing of their live performances.

The final outcome of the project is an interactive **Streamlit web application** that presents the analysis through visualizations, filters, and short interpretations.

## Research questions
The project is structured into three thematic sections with three research questions each.

### 1. Streaming & Ticket Power
- **RQ1:** How does the number of Last.fm listeners correlate with the scale of an artist's tour, measured by the number of events scheduled?
- **RQ2:** How does the concentration of an artist's streaming activity on a few top tracks relate to the intensity of their touring, measured by events per year?
- **RQ3:** How do current Last.fm listener counts differ between artists who appeared in Spotify Weekly Charts *(Feb 2023 - Feb 2026)* and those who did not?

### 2. Geographic Analysis
- **RQ4:** What is the ratio of revisit cities to new cities on an artist's current tour?
- **RQ5:** What proportion of an artist's performances takes place in capital cities compared to non-capital cities?
- **RQ6:** How well do the countries where an artist has the highest listener reach on Last.fm align with the countries where they perform on their Ticketmaster tour?

### 3. Market Time & Scheduling
- **RQ7:** How do average days between concerts differ between artists with high and low Last.fm listener counts?
- **RQ8:** To what extent does an artist's Last.fm playcount influence the percentage of concerts scheduled on weekends?
- **RQ9:** How does lead time *(days between ticket sale start and the first concert date)* correlate with an artist's Last.fm listener count?

## Data sources
The project integrates four main data sources:

- **Last.fm API** for listener counts, playcounts, top tracks, and country-level listener reach
- **Ticketmaster API** for event dates, cities, countries, ticket sale information, and tour size
- **Spotify Weekly Charts** for identifying chart and non-chart artists over time
- **Capital city / country dataset** for distinguishing capital from non-capital tour locations

## Data pipeline
The project follows a multi-step data pipeline:

1. **Artist list creation**  
   A base list of artists is generated for the analysis.

2. **Data collection**  
   Scripts collect artist-level and event-level data from the external sources.

3. **Feature engineering**  
   Derived variables are calculated, for example:
   - total number of events
   - events per year
   - average days between concerts
   - weekend share
   - lead time
   - streaming concentration
   - revisit ratio
   - geographic alignment metrics

4. **Data integration**  
   The collected and derived data are merged into processed artist-level datasets.

5. **Web app usage**  
   The Streamlit application reads the processed CSV files and visualizes the results for each research question.

In short, the data flow is:

`raw source data -> processing scripts -> processed datasets -> Streamlit web app`

## Web application
The project website was built with **Streamlit** and is organized into the following pages:

- **Home**
- **Streaming & Ticket Power**
- **Geographic Analysis**
- **Market Time & Scheduling**
- **Data**
- **Glossary**
- **About Us**

### How the website is connected to the data
The application does not query the APIs live during normal usage. Instead, the Python scripts generate and update datasets in the `data/processed/` directory. The Streamlit pages then load these processed files and use them for the visual analysis.

This makes the app more stable, reproducible, and easier to present.

### Highlights of the web application
The web application allows users to:
- explore all nine research questions interactively
- compare artists across different popularity and touring measures
- inspect geographic and scheduling patterns visually
- use glossary explanations for important terms and metrics
- review the processed project data in a dedicated data page

## Project structure
Only the most relevant parts of the repository are listed here:

```text
DataScience-Project/
├── data/
│   ├── raw/                 # collected source data
│   ├── processed/           # cleaned and merged datasets used by the app
├── src/
│   ├── scripts/             # data collection and processing scripts
│   ├── research_question_analyses/
│   │                         # scripts for individual research questions
│   └── web/
│       ├── app.py           # Streamlit entry point
│       ├── components/      # shared UI components
│       └── pages/           # dashboard pages
├── requirements.txt
└── README.md
```

## Installation and running the project
### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create a `.env` file
Add the required API keys in the project root:

```env
LASTFM_API_KEY=your_lastfm_key
TICKETMASTER_API_KEY=your_ticketmaster_key
```

### 3. Run the web application
```bash
streamlit run src/web/app.py
```

## AI usage disclaimer
This project was developed with the support of **large language models (LLMs)** and other AI-based tools.

AI was used primarily for:
- coding assistance
- debugging
- restructuring and documenting code
- wording support for texts and descriptions
- general development guidance

All AI-supported outputs were reviewed, adapted, and integrated by the project team. Responsibility for the correctness of the code, the validity of the analysis, and the interpretation of the results remains entirely with the authors.

## Note on the final implementation
The original project idea focused more directly on Spotify popularity indicators such as followers and popularity score. During the project, access to the API functions required for our analysis was no longer available. As a result, this approach could not be used. Therefore, the final implementation relies primarily on **Last.fm listener counts and playcounts** as the main popularity proxies, while Spotify Weekly Charts are used as a complementary source.

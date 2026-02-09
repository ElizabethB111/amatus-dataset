AMATUS Study Insights: Understanding Math Learning Anxiety through Interactive Data Visualization

Overview

AMATUS Study Insights is an interactive Streamlit dashboard designed to explore patterns of math learning anxiety, self-concept, and arithmetic performance among university students. The dashboard translates psychological survey data into accessible visual insights that can inform educational practice, particularly around instructional design and student support.

The project focuses on how different math learning tasks relate to anxiety and how anxiety interacts with student performance and self-perception.

AMATUS stands for Arithmetic Performance, Mathematics Anxiety and Attitudes in Primary School Teachers and University Students.


Data Source & Study Context

The dashboard uses publicly available data collected in June 2017 from 848 German university students at the University of Tuebingen (Baden-Wuerttemberg, South-West Germany). See AMATUS project on OSF website for details and data dictionary https://osf.io/gszpb/files/osfstorage. 

While the full AMATUS dataset includes both teachers and university students from Germany and Belgium, all teacher data were intentionally excluded in the creation of this dashboard to focus specifically on student experiences.

Important notes: Dashboard creators are not affiliated with the AMATUS study. The dashboard is intended for educational and exploratory purposes, not clinical diagnosis. Original study details can be found via the AMATUS publication.

AMATUS Study Contributors: Krzysztof Cipora, Maristella Lunardon, Nicolas Masson, Carrie Georges, Hans-Christoph Nuerk, Christina Artemenko


What This Dashboard Explores
1. Overview of Psychological Test Scores: Users can explore how students scored across several self-reported measures, including: Math learning anxiety, Test-related self-concepts, Attitudes toward mathematics

2. Anxiety Triggers: This section visualizes correlations between specific math learning tasks and reported math anxiety.

Examples of tasks examined include: Watching math being demonstrated on the board, Starting a new math topic, Passive learning situations (lectures, peer explanations)

Key findings:

All examined tasks show relatively high correlations with math anxiety (on a 0–1 scale). Visual and passive learning tasks exhibit some of the strongest anxiety associations. These patterns suggest that anxiety may be context-dependent rather than constant.

Actionable insight for educators:
Reducing prolonged passive instruction and incorporating interactive strategies — such as narrated examples, manipulatives, mini whiteboards, and guided problem solving — may help mitigate anxiety during math instruction.

3. Student Profiles: Patterns of Anxiety and Performance: The dashboard groups students into interpretable profiles based on performance and anxiety patterns. These profiles highlight that anxiety and performance do not always align, reinforcing the importance of nuanced instructional responses.

Project Purpose: This project was created to: Translate psychological research into accessible visual insights, Support educators and education researchers in understanding math anxiety, Demonstrate best practices in data storytelling and interactive visualization, Serve as a portfolio example of responsible educational data analysis

Repository Structure
.
├── streamlit_app.py        # Main Streamlit application
├── data/                  # AMATUS dataset (processed for this dashboard)
├── decorations/                # Visual assets used in the app
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── LICENSE

Technologies Used

Python

Streamlit

Pandas

Altair

GitHub

Disclaimer: This dashboard is an interpretive visualization project based on publicly available data. It does not claim causal relationships and should not be used for diagnostic or evaluative purposes.

from dataclasses import dataclass
from typing import List

@dataclass
class PersonalContext:
    resume: str
    sample_cover_letter: str
    additional_info: str
    skills: List[str]
    achievements: List[str]
    personal_values: List[str]
    constraints: str

PERSONAL_CONTEXT = PersonalContext(
    resume="""
    Software Engineering Co-op Student at McGill University | GPA: 3.88/4.00 | Graduating Dec 2027

    Technical Skills:
    - Languages: Java (Spring Boot, JUnit), Python (Flask, PyTorch, Pandas), C, JavaScript, HTML/CSS, OCaml, Matlab, VHDL, ARM Assembly, Bash
    - Tools/Frameworks: Vue.js, React.js, Git, AWS, PostgreSQL

    Work Experience:
    - AI Trainer – Data Annotation, Remote (Freelance) March 2025 - Present: Authored structured prompts in mathematics to improve AI model accuracy, reviewed AI-generated responses to identify flaws and improve clarity
    - Mathematics & English Tutor (Private) 2021-2023: Helped student confidently pass calculus classes, addressed student concerns, provided suggestions for English writing improvement
    - Logistics & Inventory Support – Lactalis Canada, Lachine (Part-time) June 2022 – Present: Operated forklifts moving up to 62,000 kg of dairy per shift, coordinated with team during truck loading to streamline operations

    Key Projects:
    - Board Game Rental App (Winter 2025): Led a 7-person semi-agile team in designing a full-stack board game rental system using Java Spring Boot, PostgreSQL, and Vue.js. Led as project manager and full-stack developer, contributing ~40% of the codebase (+70 commits) across backend logic, controllers, database schema, UML diagrams, and Vue.js frontend. Built time-aware booking logic with conflict prevention and automated reminders; documented REST APIs and achieved 85%+ coverage through E2E testing. Final grade: 95%.
      Skills developed: Team leadership, agile project management, REST API design, database optimization, full-stack development

    - McHacks 12 - Triage Mate (January 2025): Prototyped a triage support platform for ER patients in 24h. Designed and implemented the frontend using JavaScript, Figma and React, integrating with a prebuilt Flask backend via REST APIs to display triage status and enable peer communication. Constructed a real-time virtual lobby using Python sockets and Pygame, overcoming data loss by adapting the transport protocol.
      Skills developed: Real-time communication protocols, healthcare software design, rapid prototyping under pressure, frontend-backend integration

    - Chess Application (Fall 2024): Developed a fully playable chess game in Python/Pygame. Used 2D arrays and OOP principles to simulate gameplay mechanics, enabling legal move validation, captures, and state tracking. Coded a simple AI opponent using minimax search with a lightweight evaluation function, evaluating up to ~5,000 positions per turn (shallow depth 2-3) to allow solo play against the engine.
      Skills developed: Algorithm design, game theory, performance optimization, recursive problem solving, AI/game development

    - Parkinson's Disease Model Predictor (Winter 2024): Collaborated in a 5-person team to build a ML pipeline that classifies PD's severity based on gait data from 93 PD patients and 73 control subjects. Utilized Python libraries including PyTorch, Keras, Pandas, scikit-learn, and Matplotlib to develop, train, and visualize results across models. Achieved 86% accuracy with a CNN-LSTM model and 75% with logistic regression by leveraging FFT and EMD signal analysis.
      Skills developed: Machine learning, neural networks, signal processing, data analysis, medical data classification

    - 2D Racing Game on FPGA: Built custom FPGA drivers in C, designed game logic, and crash logic.
      Skills developed: Low-level programming, hardware-software integration, 2D graphics concepts, embedded systems

    - EEG Data Analysis: Used MATLAB to analyze brain signals from 64-electrode EEG dataset (team of 4).
      Skills developed: Signal processing, data analysis, biomedical engineering applications, scientific computing

    - Metro Network Optimization: Simulated and optimized metro network for McGill campus using advanced data structures.
      Skills developed: Graph algorithms, optimization techniques, transportation modeling, data structures design

    - 100 Days of Code: Created daily projects including stock market alerts, Pong game, password manager, web scraping tools.
      Skills developed: API integration, GUI design, web scraping, automation, diverse programming paradigms
      
    GENERALLY it takes me two weeks to learn the fundamentals in a technology.

    Awards & Certifications:
    - 100 Days of Code – The Complete Python Bootcamp Summer 2025: Completed comprehensive Python bootcamp building diverse projects
    - Finalist, Cleantech Idea Pitch Competition Fall 2022: Designed bioreactor for biomass-to-hydrogen via dark fermentation, analyzed carbon lifecycle for emission reduction
    """,

    sample_cover_letter="""Dear Hiring Manager,

I am a customer focused and creative Technical Account Manager with over 2 years of experience interested in learning more about Adyen’s Implementation Team. 

Over the last two and a half years, l've helped my company generate over $10M in revenue by leading meetings with executive leaders and also
built a variety of web applications on the side. And now I'm excited to continue my journey by contributing and growing at Adyen. There are three things that make me the perfect fit for this position: 

First, l've always been intellectually curious about understanding how things work and the technology sector. As an Account Manager at a Machine Learning startup, I wanted to push myself and understand the technical elements of my day to day. I enrolled in an online Software Engineering program on the side and 2 years later, l've built multiple full stack web applications that interact with web APls like Twitter and Clearbit. These technical skills that I've built up have helped me become the go-to person on my team to help debug technical issues.

Second, I have plenty of experience leading meetings with high level executives. I've managed delicate situations pertaining to data privacy sharing, successfully upsold additional revenue streams on the back of data analysis, and run Quarterly Business Reviews where I've had to think quickly on my feet. As the company scaled from 50 to 250 employees, l've also taken on increased responsibility including the mentoring of junior team members. 

Finally,  As a global citizen (I've lived on 3 continents), I recognize the importance of diversity towards innovation and want to work at a company that embodies this. Having worked with multiple clients in the Fintech space over the past year, I've also become interested in payments and the opportunity to help
some of the fastest growing companies in the world continue to scale.

I think you'll find that my experience is a really good fit for Adyen and specifically this position. I'm ready to take my skills to the next level withyour team and look forward to hearing back.

Best regards,
Andres Gonzalez""",

    additional_info="""
    Additional Context:
    - Currently pursuing Software Engineering Co-op program at McGill University
    - Strong academic performance with 3.88/4.00 GPA
    - Experience leading technical teams and mentoring other students
    - Passionate about sustainable technology and ethical software development
    - Fluent in English, French, and Spanish
    - Available for 4-8 month co-op terms
    - Interested in full-stack development, AI/ML, and systems programming
    """,

    skills=[
        "Full-stack web development (Java Spring Boot, Vue.js, React.js)",
        "Database design and optimization (PostgreSQL, SQL)",
        "Machine learning and data analysis (Python, PyTorch, Pandas)",
        "Algorithm design and optimization",
        "Test-driven development and automated testing",
        "Agile development methodologies",
        "Version control and collaborative development (Git)",
        "Cloud platforms and deployment (AWS)",
        "Low-level programming (C, VHDL, ARM Assembly)",
        "Technical leadership and team management"
    ],

    achievements=[
        "Led successful migration of legacy systems, improving test coverage by 20%",
        "Achieved 85% test coverage in team-led Board Game Rental App project",
        "Mentored 50+ students as Teaching Assistant for computer science courses",
        "Developed real-time ER triage system in hackathon environment",
        "Maintained 3.88/4.00 GPA while balancing work and leadership responsibilities",
        "Built hardware-accelerated racing game using custom VHDL drivers",
        "Completed 100 Days of Code challenge with diverse project portfolio"
    ],

    personal_values=[
        "Integrity – doing the right thing without cutting corners or pretending",
        "Honesty & self-awareness – being direct about strengths and weaknesses, always questioning and improving",
        "Intellectual depth – striving to understand things from first principles and avoid surface-level thinking",
        "Grit & follow-through – showing discipline even through burnout or setbacks, finishing what's started",
        "Thoughtful autonomy – preferring independent, well-reasoned decisions over blindly following trends",
        "Responsibility toward the world – caring about sustainability, fairness, and ethical impact",
        "Craftsmanship & technical curiosity – taking pride in building elegant, grounded, low-level systems"
    ],

    constraints="""
    Constraints and Preferences:
    - Keep cover letters to 1 page maximum
    - Maintain professional but warm tone
    - Avoid overly corporate language
    - Focus on concrete examples and achievements
    - Always mention specific company details when possible
    - Include quantifiable results when available
    - Ensure each cover letter is tailored to the specific role
    """
)
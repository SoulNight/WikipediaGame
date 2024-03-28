Author: Tony Bautista & Aidan Lewis Grenz

WGIP: Enhanced with "Milestones" Section

Background
The Wikipedia Game is a web-based game where players navigate from a given starting Wikipedia article to a target article using the fewest hyperlinks. The current algorithm employs a breadth-first search (BFS) approach, which does not prioritize the relevance of links based on content.

Rationale
The BFS algorithm's non-discriminatory nature towards link relevance often leads to longer, inefficient search paths. Introducing a content-aware heuristic could streamline the search process by prioritizing more relevant links.

Improvement Overview
This proposal suggests integrating a keyword relevance-based heuristic into the BFS algorithm. This approach aims to prioritize hyperlinks leading closer to the target article by evaluating their content's relevance.

Methodology
1. Keyword Extraction: Extract significant keywords from the target article to guide the search.
2. Content Analysis: Evaluate the relevance of links on each visited page by analyzing their content for keyword presence.
3. Priority Queue: Adapt the BFS to use a priority queue for links with keywords matching the target article.
4. Fallback Mechanism: Retain a standard queue for links without target keywords to ensure algorithm completeness.

Potential Challenges
- Keyword Extraction: Identifying optimal keywords for guiding the search.
- Performance: Content analysis may slow down the search process.
- Accuracy: Risk of prioritizing misleadingly relevant links.
- Completeness: Ensuring the modified algorithm guarantees finding a path, if available.

Testing and Validation
1. Benchmarking: Compare the heuristic BFS with the original BFS regarding search efficiency and time.
2. Edge Cases: Validate performance under challenging scenarios, such as obscure target articles.
3. User Trials: Assess the improved algorithm in a controlled user study.


Future Work
Considerations for future improvements include leveraging machine learning for link relevance prediction and exploring graph databases for optimized link navigation.

Milestones

1. Milestone 1: Research and Design Phase
   - Deadline: 2 weeks from start.
   - Tasks: Finalize the algorithm design. Select NLP libraries (e.g., NLTK, spaCy) and word embedding models (Word2Vec, GloVe).
   - Deliverables: Algorithm design document

2. Milestone 2: Prototype Development
   - Deadline: 4 weeks from start.
   - Tasks: Implement the heuristic BFS algorithm. Develop keyword extraction and content analysis functionalities.
   - Programming Languages & Libraries: Python, NLTK/spaCy for NLP, NumPy for data manipulation.
   - Deliverables: Functional prototype.

3. Milestone 3: Initial Testing and Benchmarking
   - Deadline: 6 weeks from start.
   - Tasks: Conduct initial tests comparing heuristic BFS with standard BFS. Identify performance bottlenecks.
   - Deliverables: Testing report, performance benchmarks.

4. Milestone 4: User Trials and Iteration**
   - Deadline: 7 weeks from start.
   - Tasks: Deploy prototype in a test environment. Collect and analyze user feedback.
   - Deliverables**: User feedback report, revised prototype.

5. Milestone 5: Final Review and Launch Preparation**
   - Deadline: 8 weeks from start.
   - Tasks: Based on user trials and testing, finalize the algorithm and prepare it for integration into the live game environment.
   - Deliverables: Finalized algorithm and integration plan.

Conclusion
This proposal outlines a comprehensive plan to enhance the Wikipedia Game's search algorithm by incorporating a content-aware heuristic. The detailed milestones provide a clear path toward achieving a more efficient and user-friendly search mechanism.


---Thursday's Lectures notes (3-14-24)---


The insights we gained from Thursday's lecture introduce a variety of advanced techniques and strategies that can significantly optimize the Wikipedia Game Improvement Proposal (WGIP). These enhancements focus on leveraging artificial intelligence, efficient data handling, and algorithm optimization to streamline the search process and improve the overall user experience. Here’s an elaboration on these enhancements:

AI and Machine Learning Integration
- Use of AI in Search: Employing artificial intelligence, such as chat GPT and word embeddings, can revolutionize the search process. AI can review search paths for relevance and efficiency, utilizing the power of language models to understand and prioritize content.
- Word Embeddings and Transformer Models: Incorporating word embeddings and transformer models enables the algorithm to grasp the context and significance of words in relation to each other. By analyzing entire Wikipedia pages, the algorithm achieves a more nuanced understanding of content relevance, allowing for a more targeted search path.

Caching for Efficiency
- Benefits of Caching: Caching frequently accessed data in a local repository can drastically reduce search times and resource consumption. This approach is particularly beneficial for data that is reused often throughout the search process.
- Optimizing Data Handling: The strategic use of data structures can lead to more efficient runtimes. For example, opting for lists instead of sets when duplicate entries are not a concern can speed up the search process, especially when the goal is to find a path quickly rather than the most efficient path.

Search Algorithm Improvements
- Adapting Search Strategies: Modifying the search strategy to prioritize finding a path quickly, such as adapting aspects of the A* algorithm for speed over the shortest path, can significantly enhance performance.
- Parallel Processing: Utilizing parallelism and threading can expedite the search by allowing multiple potential paths to be explored simultaneously, leveraging modern processors' capabilities to their fullest.

Leveraging APIs and External Tools
- Wikipedia API Efficiency: Using the Wikipedia API effectively can enhance the search process's speed and efficiency, providing a direct and optimized way to access and traverse Wikipedia content.
- Local Model Execution: The use of local models, inspired by tools like LLM Studio or Visual Studio Code, offers the flexibility to run medium-sized models locally. This approach reduces dependence on external services and can speed up the search by processing data directly on the user's device.

Algorithmic Refinements
- Heuristic Enhancements: Refining the heuristic search focusing on link similarity and relevance can improve search efficiency. By using NLP techniques to compare the contextual relevance of links to the target page, the algorithm can more effectively prioritize promising paths.
-  Efficient Data Analysis: The extraction and analysis of keywords, through frequency analysis or advanced NLP techniques, can offer insights into the relevance of links, guiding the search in a more informed manner.

Implementation and Validation
-  Benchmarking and Validation: Establishing standard benchmarks and conducting extensive testing, including edge cases and user trials, will be crucial for validating the enhanced algorithm's effectiveness.
- Logging and Analysis: Implementing logging mechanisms, such as a CSV matrix, can help track the algorithm's performance, identify bottlenecks, and further refine the search process.



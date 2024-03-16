Author: Tony Bautista & Aidan Lewis Grenz

Wikipedia Game Improvement Proposal (WGIP)

Background
The Wikipedia Game is a web-based game that challenges players to reach a specific Wikipedia article from a given starting article, using the fewest hyperlink clicks. The current algorithm guiding this process is a simple breadth-first search (BFS), which treats all links equally and does not consider the content within the pages.

Rationale
While guaranteeing a solution, the BFS algorithm does not account for the relevance of content when selecting links. This often results in an inefficient path and a longer search time. Incorporating a content-aware heuristic can make the search more targeted and efficient.

Improvement Overview
The proposed improvement is to enhance the BFS algorithm with a heuristic approach based on keyword relevance. This would allow the game to prioritize links that are more likely to lead to the target article, based on the content similarity.

Methodology
The methodology for the improvement includes:
1. Keyword Extraction: Analyze the target page to extract critical terms that signify its content.
2. Content Analysis: Upon visiting a new page, examine the content of its links.
3. Priority Queue: Modify the BFS to prioritize links that include the target page's keywords.
4. Fallback: Maintain a regular queue for links without keywords to ensure the algorithm remains complete.

Pseudo-code:
function heuristicBFS(startPage, targetPageKeywords) {
    queue = new PriorityQueue()
    visited = new Set()

    queue.add(startPage)

    while not queue.isEmpty() {
        currentPage = queue.pop()

        if currentPage == targetPage {
            return reconstructPath(currentPage)
        }

        visited.add(currentPage)

        for link in extractLinks(currentPage) {
            if link not in visited {
                relevance = calculateRelevance(link, targetPageKeywords)
                queue.addWithPriority(link, relevance)
            }
        }
    }
}

Potential Challenges
-Keyword Extraction: Determining the most relevant keywords from the target page can be challenging and may require fine-tuning.
- Performance: Analyzing the content of each link for keywords can introduce performance overhead.
- Accuracy: The heuristic may prioritize contextually relevant links that lead away from the target, potentially introducing inefficiencies.
Completeness: It is critical to ensure that the heuristic-enhanced BFS algorithm remains complete and can find a path if one exists.

Testing and Validation
To ensure the proposed algorithm performs as intended, rigorous testing must be conducted. This would include:

1. Benchmarking: Compare the new algorithm against the current BFS regarding the number of steps to reach the target page and the time taken for several test cases.
2. Edge Cases: Test scenarios where the target page is obscure or has few incoming links to ensure the heuristic does not compromise the search.
3. User Trials: Implement the improved algorithm in a test environment and measure user success rates and search times.

Future Work
Future enhancements could include machine learning models to predict link relevance or graph database technologies to optimize link traversal.

Conclusion
The proposal aims to enhance search efficiency and user experience in the Wikipedia Game without extensive modifications by integrating a content-aware heuristic. Special libraries for NLP, like NLTK or spaCy, and word embedding models, such as Word2Vec or GloVe, may be considered for advanced analysis and optimization.


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



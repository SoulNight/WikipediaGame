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


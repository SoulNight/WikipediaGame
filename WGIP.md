

# Wikipedia Game Improvement Proposal (WGIP)

## Authors

Tony Bautista 
email: jubautista@chapman.edu

Aidan Lewis Grenz
email: aidanlewisgrenz@icloud.com


## Background

The Wikipedia Game is a web-based game where players navigate from a given starting Wikipedia article to a target article using the fewest hyperlinks. The current algorithm employs a breadth-first search (BFS) approach, which does not prioritize the relevance of links based on content.

## Rationale

The BFS algorithm's non-discriminatory nature towards link relevance often leads to longer, inefficient search paths. Introducing a content-aware heuristic could streamline the search process by prioritizing more relevant links.

## Improvement Overview

This proposal suggests integrating a keyword relevance-based heuristic into the BFS algorithm. This approach aims to prioritize hyperlinks leading closer to the target article by evaluating their content's relevance.

## Methodology

1. Keyword Extraction: Extract significant keywords from the target article to guide the search.
2. Content Analysis: Evaluate the relevance of links on each visited page by analyzing their content for keyword presence.
3. Priority Queue: Adapt the BFS to use a priority queue for links with keywords matching the target article.
4. Fallback Mechanism: Retain a standard queue for links without target keywords to ensure algorithm completeness.

## Potential Challenges

- Keyword Extraction: Identifying optimal keywords for guiding the search.
- Performance: Content analysis may slow down the search process.
- Accuracy: Risk of prioritizing misleadingly relevant links.
- Completeness: Ensuring the modified algorithm guarantees finding a path, if available.

## Testing and Validation

1. Benchmarking: Compare the heuristic BFS with the original BFS regarding search efficiency and time.
2. Edge Cases: Validate performance under challenging scenarios, such as obscure target articles.
3. User Trials: Assess the improved algorithm in a controlled user study.

## Future Work

Considerations for future improvements include leveraging machine learning for link relevance prediction and exploring graph databases for optimized link navigation.

## Project Milestones

### Milestone 1: Project Setup and Environment Preparation

- Notes: Assemble the development workspace, procure all necessary software utilities, and catalog the dependencies and libraries necessary for the initiative.
  
#### Pseudo code:

```python
# Import necessary libraries
import nltk
import gensim
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq
import requests
from bs4 import BeautifulSoup

# Download NLTK data (e.g., stopwords)
nltk.download('stopwords')
nltk.download('punkt')

# Define function to install required Python libraries
def install_libraries():
    # Example: pip install gensim nltk numpy scikit-learn BeautifulSoup4
    pass

# Initialize environment setup
install_libraries()
```

### Milestone 2: Understand A* Search Algorithm and the Original BFS Implementation

- **Notes**: Examine the current BFS strategy and strategize for the enhancement with A* methodologies, taking into account areas for heuristic integration.

#### Psuedo code:

```python
# Pseudo-code to understand BFS and prepare for A* integration
def bfs_algorithm(start_page, target_page):
    """
    Basic BFS search from start_page to target_page.
    This will be enhanced with A* search integration.
    """
    queue = [(start_page, [start_page])]
    visited = set()

    while queue:
        current_page, path = queue.pop(0)
        if current_page == target_page:
            return path
        for link in get_links_from_page(current_page):
            if link not in visited:
                visited.add(link)
                queue.append((link, path + [link]))

def get_links_from_page(page_url):
    """
    Fetch and parse all hyperlinks from a given Wikipedia page.
    """
    # Simulate fetching links from a Wikipedia page
    return ["Link1", "Link2", "Link3"]

# Note: Actual implementation will fetch real links
```

### Milestone 3: Keyword Extraction

- **Notes**: Conduct an exploration to determine the most effective techniques for keyword extraction, considering NLTK for tokenization and Gensim for logic extraction.

#### Psuedo Code

```python
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.summarization import keywords

def extract_keywords(text):
    """
    Extract keywords using NLTK for tokenization and Gensim for keyword extraction.
    """
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stopwords.words

('english')]
    text_for_extraction = " ".join(filtered_tokens)
    extracted_keywords = keywords(text_for_extraction, words=5, lemmatize=True).split('\n')
    return extracted_keywords

# Example usage
sample_text = "This is a sample text for keyword extraction."
print(extract_keywords(sample_text))
```

### Milestone 4: Semantic Similarity Calculation

- **Notes**: Survey a range of methodologies to evaluate the semantic linkages between articles, considering options like TF-IDF or embedding techniques.

#### Psuedo Code:

```python
def calculate_semantic_similarity(text1, text2):
    """
    Calculate semantic similarity between two texts using TF-IDF and cosine similarity.
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

# Example usage
text1 = "This is a sample text."
text2 = "This is another sample text with semantic similarity."
print(calculate_semantic_similarity(text1, text2))
```

### Milestone 5: Heuristic Function Design

- **Notes**: Develop a heuristic approach informed by semantic analysis and keyword significance to approximate the target article's accessibility.

#### Pseudo Code:

```python
def heuristic_function(current_page_content, target_keywords):
    """
    Design heuristic based on semantic similarity and keyword presence.
    """
    current_page_keywords = extract_keywords(current_page_content)
    similarity_score = calculate_semantic_similarity(" ".join(current_page_keywords), " ".join(target_keywords))
    return similarity_score

# Example usage
current_page_content = "Content of the current page with some keywords."
target_keywords = ["target", "keywords"]
print(heuristic_function(current_page_content, target_keywords))
```

### Milestone 6: Integration and Testing

- **Notes**: Synthesize all elements to finalize the A* Algorithm augmented with the heuristic approach and execute thorough testing protocols.

#### Pseudo code:

```python
# Pseudo code for integration and testing of the A* Search Algorithm with the heuristic function
def integration_testing():
    # Assuming other functions such as a_star_search, heuristic_func, and reconstruct_path are defined
    start_page = "Start Wikipedia Page URL"
    target_page = "Target Wikipedia Page URL"
    path = a_star_search(start_page, target_page, heuristic_func)
    if path:
        print(f"Path found: {' -> '.join(path)}")
    else:
        print("No path found.")

# Run integration tests
integration_testing()
```

### Milestone 7: Optimization and Refinement

- **Notes**: Locate and rectify any efficiency impediments within the codebase, implementing techniques such as result caching, concurrent computing, and search logic enhancement.

#### Pseudo code:

```
# Pseudo code for optimization and refinement
def optimize_algorithm():
    # Profile the algorithm to find bottlenecks
    profile_results = profile(a_star_search, args=(start_page, target_page, heuristic_func))
    
    # Analyze profile results to find optimization opportunities
    analyze_profile(profile_results)

    # Implement optimizations based on the analysis
    # This could involve caching results, using more efficient data structures,
    # or parallelizing certain operations
    implement_optimizations()

# Run optimization process
optimize_algorithm()
```

## Project Milestones

| Milestone                                        | Description                                                                                                                                              | Duration      | Progress        | Completed | Expected Completion  |
|--------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|-----------------|-----------|----------------------|
| Initial Project Configuration                    | Assemble the development workspace, procure all necessary software utilities, and catalog the dependencies and libraries necessary for the initiative.    | 3 days        | Pending         | No        | April 7, 2024       |
| Comprehend A* and BFS Mechanisms                 | Examine the current BFS strategy and strategize for the enhancement with A* methodologies, taking into account areas for heuristic integration.           | 3 days        | Pending         | No        | April 14, 2024        |
| Extraction of Keywords                           | Conduct an exploration to determine the most effective techniques for keyword extraction, considering NLTK for tokenization and Gensim for logic extraction. | 1 week        | Pending         | No        | April 21, 2024       |
| Evaluation of Semantic Linkages                  | Survey a range of methodologies to evaluate the semantic linkages between articles, considering options like TF-IDF or embedding techniques.             | 1 week        | Pending         | No        | April 28, 2024       |
| Development of Heuristic Approach                | Develop a heuristic approach informed by semantic analysis and keyword significance to approximate the target article's accessibility.                     | 1 week        | Pending         | No        | April 28, 2024       |
| Integration and Comprehensive Testing            | Synthesize all elements to finalize the A* Algorithm augmented with the heuristic approach and execute thorough testing protocols.                        | 2 weeks       | Pending         | No        | May 12, 2024          |
| Streamlining and Enhancement                     | Locate and rectify any efficiency impediments within the codebase, implementing techniques such as result caching, concurrent computing, and search logic enhancement. | 1 week        | Pending         | No        | May 19, 2024         |



## Conclusion

This proposal outlines a comprehensive plan to enhance the Wikipedia Game's search algorithm by incorporating a content-aware heuristic. The detailed milestones provide a clear path toward achieving a more efficient and user-friendly search mechanism.
```

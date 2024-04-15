
Wikipedia Game Improvement Proposal (WGIP)

Author: Tony Bautista & Aidan Lewis Grenz

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

Project Milestones
Milestone 1: Project Setup and Environment Preparation
Notes: Import necessary libraries and initialize environment setup. 
Time Required: 2 weeks 
Current Status: Started
Finished: 
Delivery Date: April 8

Psuedo code:
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

Milestone 2: Understand A* Search Algorithm and the Original BFS Implementation
Notes: Analyze BFS and prepare for A* integration. 
Time Required: 2 weeks 
Current Status: Not Started 
Finished: 
Delivery Date: April 22, 2024

Psuedo code:
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


Milestone 3: Keyword Extraction
Notes: Extract keywords using NLTK for tokenization and Gensim for keyword extraction. 
Time Required: 1 week 
Current Status: Not Started 
Finished: 
Delivery Date: April 29, 2024

Psuedo Code
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.summarization import keywords

def extract_keywords(text):
    """
    Extract keywords using NLTK for tokenization and Gensim for keyword extraction.
    """
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stopwords.words('english')]
    text_for_extraction = " ".join(filtered_tokens)
    extracted_keywords = keywords(text_for_extraction, words=5, lemmatize=True).split('\n')
    return extracted_keywords

# Example usage
sample_text = "This is a sample text for keyword extraction."
print(extract_keywords(sample_text))


Milestone 4: Semantic Similarity Calculation
Notes: Calculate semantic similarity between two texts using TF-IDF and cosine similarity. 
Time Required: 1 week 
Current Status: Not Started 
Finished: 
Delivery Date: May 6, 2024

Psuedo Code:
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


Milestone 5: Heuristic Function Design
Notes: Design heuristic based on semantic similarity and keyword presence. 
Time Required: 1 week 
Current Status: Not Started 
Finished: 
Delivery Date: May 13, 2024

Pseudo Code:
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


Conclusion
This proposal outlines a comprehensive plan to enhance the Wikipedia Game's search algorithm by incorporating a content-aware heuristic. The detailed milestones provide a clear path toward achieving a more efficient and user-friendly search mechanism.




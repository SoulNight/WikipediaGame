console.log("Starting fetch request setup...");

document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('wiki-form');
    const logsElement = document.getElementById('logs-content');
    const abortButton = document.getElementById('abort-btn');
    const searchingElement = document.getElementById('searching');
    const searchIdElement = document.getElementById('search-id');
    const heuristicSelect = document.getElementById('heuristic-select');
    const searchMethodInputs = document.querySelectorAll('input[name="search-method"]');
    let searchId;

    function updateHeuristicVisibility() {
        const isAStarSelected = Array.from(searchMethodInputs).some(input => input.value === 'a_star' && input.checked);
        heuristicSelect.classList.toggle('visible', isAStarSelected);
    }

    searchMethodInputs.forEach(input => 
        input.addEventListener('change', updateHeuristicVisibility)
    );

    updateHeuristicVisibility(); // Initial check on page load

    // EventSource to listen for logs from the server
    const eventSource = new EventSource('/logs');
    eventSource.onmessage = function(event) {
        const logItem = document.createElement('div');
        logItem.textContent = event.data;
        logsElement.appendChild(logItem);
    };

    // Function to clear statistics
    function clearStatistics() {
        const statsElement = document.getElementById('stats-content');
        if (statsElement) {
            statsElement.innerHTML = '';
        }
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        clearStatistics(); // Call this function to clear the statistics before starting a new search
        searchingElement.textContent = 'Searching...';
        logsElement.innerHTML = ''; // Reset logs
        document.getElementById('results-list').innerHTML = ''; // Clear search results

        const startPage = document.getElementById('start-page').value;
        const finishPage = document.getElementById('finish-page').value;
        const searchMethod = document.querySelector('input[name="search-method"]:checked').value;
        const heuristicChoice = document.getElementById('heuristic-choice') ? document.getElementById('heuristic-choice').value : 'links'; // Default to 'links' if not present

        fetch('/find_path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                start: startPage,
                finish: finishPage,
                method: searchMethod,
                heuristic: heuristicChoice, // Send the heuristic choice to the server
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status code: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            searchId = data.search_id;
            searchingElement.textContent = 'Search started.';
            searchIdElement.textContent = `Search ID: ${searchId}`;
            console.log('Search ID:', searchId);

            // Start polling for search results
            pollForResults(searchId);
        })
        .catch(error => {
            console.error('Error:', error);
            searchingElement.textContent = `Error: ${error.message}`;
        });
    });

    abortButton.addEventListener('click', function() {
        if (searchId) {
            fetch('/abort_search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ search_id: searchId }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to abort the search. Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Search aborted successfully.');
                searchingElement.textContent = 'Search has been aborted.';
                searchIdElement.textContent = '';
                clearStatistics(); // Clear statistics when search is aborted
            })
            .catch(error => {
                console.error('Error:', error);
                searchingElement.textContent = `Error: ${error.message}`;
            });
        } else {
            console.log('No search has been started to abort.');
        }
    });

    console.log("Finished fetch request setup.");
});


function pollForResults(searchId) {
    setTimeout(() => {
        fetch(`/get_results/${searchId}`)
            .then(response => {
                if (response.status === 404) {
                    console.log('Search results not ready, continuing to poll.');
                    setTimeout(() => pollForResults(searchId), 2000);
                    return null;
                } else if (!response.ok) {
                    throw new Error(`Results retrieval failed with status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data); // Log the data received from the server
                if (data) {
                    console.log('Received path length:', data.path_length);
                    if (data.completed && data.path) {
                        displayResults(data.path);
                        displayStatistics({
                          totalLinksFound: data.discovered,
                          pathFound: data.completed,
                          pathLength: data.path_length,
                          searchTime: data.time,
                          searchMethod: data.search_method
                        });
                    } else if (data.message === 'Search is in progress') {
                        setTimeout(() => pollForResults(searchId), 150000);
                    }
                }
            })
            .catch(error => {
                console.error('Error during result polling:', error);
            });
    }, 2000);
}




function displayResults(searchResults) {
    console.log('Displaying search results:', searchResults);
    const resultsListElement = document.getElementById('results-list');
    resultsListElement.innerHTML = '';

    searchResults.forEach(url => {
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.href = url;
        link.textContent = url;
        listItem.appendChild(link);
        resultsListElement.appendChild(listItem);
    });
}

function displayStatistics(data) {
    console.log('Displaying statistics:', data);
    console.log('Displaying path length:', data.pathLength);
    const statsElement = document.getElementById('stats-content');
    if (!statsElement) return;

    statsElement.innerHTML = '';

    const statsList = document.createElement('ul');

    // Format the time to two decimal places before adding it to the statsList
    const searchTimeFormatted = parseFloat(data.searchTime).toFixed(2);

    // Dynamically create list items for each statistic
    const statistics = {
        'Total Pages Discovered': data.totalLinksFound,
        'Path Found': data.pathFound ? 'Yes' : 'No',
        'Path Length': data.pathLength,
        'Search Time': `${searchTimeFormatted} seconds`, // Updated to use formatted time
        'Search Method': data.searchMethod
    };

    for (const [label, value] of Object.entries(statistics)) {
        const statItem = document.createElement('li');
        statItem.textContent = `${label}: ${value}`;
        statsList.appendChild(statItem);
    }

    statsElement.appendChild(statsList);
}

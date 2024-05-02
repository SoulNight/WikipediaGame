console.log("Starting fetch request setup..."); // Logging message indicating the start of fetch request setup

document.addEventListener('DOMContentLoaded', (event) => { // Event listener for DOMContentLoaded event
    const form = document.getElementById('wiki-form'); // Getting reference to the form element
    const logsElement = document.getElementById('logs-content'); // Getting reference to the logs content element
    const abortButton = document.getElementById('abort-btn'); // Getting reference to the abort button element
    const searchingElement = document.getElementById('searching'); // Getting reference to the searching element
    const searchIdElement = document.getElementById('search-id'); // Getting reference to the search ID element
    const heuristicSelect = document.getElementById('heuristic-select'); // Getting reference to the heuristic select element
    const searchMethodInputs = document.querySelectorAll('input[name="search-method"]'); // Getting references to all search method input elements
    let searchId; // Declaring a variable to store search ID

    function updateHeuristicVisibility() { // Function to update heuristic visibility
        const isAStarSelected = Array.from(searchMethodInputs).some(input => input.value === 'a_star' && input.checked); // Checking if A* search method is selected
        heuristicSelect.classList.toggle('visible', isAStarSelected); // Toggling visibility of heuristic select based on A* selection
    }

    searchMethodInputs.forEach(input => // Adding event listener to each search method input
        input.addEventListener('change', updateHeuristicVisibility)
    );

    updateHeuristicVisibility(); // Initial check on page load

    // EventSource to listen for logs from the server
    const eventSource = new EventSource('/logs'); // Creating EventSource object to listen for server logs
    eventSource.onmessage = function(event) { // Event handler for message event
        const logItem = document.createElement('div'); // Creating a new div element for log item
        logItem.textContent = event.data; // Setting text content of log item
        logsElement.appendChild(logItem); // Appending log item to logs content
    };

    // Function to clear statistics
    function clearStatistics() { // Function to clear statistics
        const statsElement = document.getElementById('stats-content'); // Getting reference to statistics content element
        if (statsElement) { // Checking if statistics element exists
            statsElement.innerHTML = ''; // Clearing inner HTML of statistics element
        }
    }

    form.addEventListener('submit', function(event) { // Event listener for form submission
        event.preventDefault(); // Preventing default form submission behavior
        clearStatistics(); // Call this function to clear the statistics before starting a new search
        searchingElement.textContent = 'Searching...'; // Setting searching text content
        logsElement.innerHTML = ''; // Resetting logs
        document.getElementById('results-list').innerHTML = ''; // Clearing search results

        const startPage = document.getElementById('start-page').value; // Getting value of start page input
        const finishPage = document.getElementById('finish-page').value; // Getting value of finish page input
        const searchMethod = document.querySelector('input[name="search-method"]:checked').value; // Getting value of selected search method
        const heuristicChoice = document.getElementById('heuristic-choice') ? document.getElementById('heuristic-choice').value : 'links'; // Default to 'links' if not present

        fetch('/find_path', { // Fetching data from server
            method: 'POST', // Setting request method
            headers: { // Setting request headers
                'Content-Type': 'application/json', // Setting content type to JSON
            },
            body: JSON.stringify({ // Converting data to JSON string
                start: startPage, // Setting start page
                finish: finishPage, // Setting finish page
                method: searchMethod, // Setting search method
                heuristic: heuristicChoice, // Sending the heuristic choice to the server
            }),
        })
        .then(response => { // Handling response
            if (!response.ok) { // Checking if response is not okay
                throw new Error(`Server responded with status code: ${response.status}`); // Throwing error with status code
            }
            return response.json(); // Returning JSON parsed response
        })
        .then(data => { // Handling data
            searchId = data.search_id; // Setting search ID from response data
            searchingElement.textContent = 'Search started.'; // Updating searching text content
            searchIdElement.textContent = `Search ID: ${searchId}`; // Setting search ID text content
            console.log('Search ID:', searchId); // Logging search ID

            // Start polling for search results
            pollForResults(searchId); // Calling function to poll for search results
        })
        .catch(error => { // Handling error
            console.error('Error:', error); // Logging error
            searchingElement.textContent = `Error: ${error.message}`; // Updating searching text content with error message
        });
    });

    abortButton.addEventListener('click', function() { // Event listener for abort button click
        if (searchId) { // Checking if search ID exists
            fetch('/abort_search', { // Fetching data to abort search
                method: 'POST', // Setting request method
                headers: { // Setting request headers
                    'Content-Type': 'application/json', // Setting content type to JSON
                },
                body: JSON.stringify({ search_id: searchId }), // Converting data to JSON string
            })
            .then(response => { // Handling response
                if (!response.ok) { // Checking if response is not okay
                    throw new Error(`Failed to abort the search. Status: ${response.status}`); // Throwing error with status
                }
                return response.json(); // Returning JSON parsed response
            })
            .then(data => { // Handling data
                console.log('Search aborted successfully.'); // Logging successful search abortion
                searchingElement.textContent = 'Search has been aborted.'; // Updating searching text content
                searchIdElement.textContent = ''; // Clearing search ID text content
                clearStatistics(); // Clearing statistics when search is aborted
            })
            .catch(error => { // Handling error
                console.error('Error:', error); // Logging error
                searchingElement.textContent = `Error: ${error.message}`; // Updating searching text content with error message
            });
        } else { // If no search has been started
            console.log('No search has been started to abort.'); // Logging message
        }
    });

    console.log("Finished fetch request setup.");
});


function pollForResults(searchId) { // Function to poll for search results
    setTimeout(() => { // Setting a timeout for polling
        fetch(`/get_results/${searchId}`) // Fetching search results from server
            .then(response => { // Handling response
                if (response.status === 404) { // Checking if search results are not ready
                    console.log('Search results not ready, continuing to poll.'); // Logging message
                    setTimeout(() => pollForResults(searchId), 2000); // Polling again after 2 seconds
                    return null; // Returning null
                } else if (!response.ok) { // Checking if response is not okay
                    throw new Error(`Results retrieval failed with status: ${response.status}`); // Throwing error with status
                }
                return response.json(); // Returning JSON parsed response
            })
            .then(data => { // Handling data
                console.log('Received data:', data); // Logging data received from server
                if (data) { // Checking if data exists
                    console.log('Received path length:', data.path_length); // Logging received path length
                    if (data.completed && data.path) { // Checking if search is completed and path found
                        displayResults(data.path); // Displaying search results
                        displayStatistics({ // Displaying statistics
                            totalLinksFound: data.discovered,
                            pathFound: data.completed,
                            pathLength: data.path_length,
                            searchTime: data.time,
                            searchMethod: data.search_method
                        });
                    } else if (data.message === 'Search is in progress') { // If search is in progress
                        setTimeout(() => pollForResults(searchId), 150000); // Polling again after 150 seconds
                    }
                }
            })
            .catch(error => { // Handling error
                console.error('Error during result polling:', error); // Logging error
            });
    }, 2000); // Polling interval
}

function displayResults(searchResults) { // Function to display search results
    console.log('Displaying search results:', searchResults); // Logging message
    const resultsListElement = document.getElementById('results-list'); // Getting reference to results list element
    resultsListElement.innerHTML = ''; // Clearing inner HTML of results list

    searchResults.forEach(url => { // Iterating through search results
        const listItem = document.createElement('li'); // Creating list item element
        const link = document.createElement('a'); // Creating anchor element
        link.href = url; // Setting href attribute of anchor
        link.textContent = url; // Setting text content of anchor
        listItem.appendChild(link); // Appending anchor to list item
        resultsListElement.appendChild(listItem); // Appending list item to results list
    });
}

function displayStatistics(data) { // Function to display statistics
    console.log('Displaying statistics:', data); // Logging statistics data
    console.log('Displaying path length:', data.pathLength); // Logging path length
    const statsElement = document.getElementById('stats-content'); // Getting reference to statistics content element
    if (!statsElement) return; // Returning if statistics element does not exist

    statsElement.innerHTML = ''; // Clearing inner HTML of statistics element

    const statsList = document.createElement('ul'); // Creating unordered list element

    // Format the time to two decimal places before adding it to the statsList
    const searchTimeFormatted = parseFloat(data.searchTime).toFixed(2); // Formatting search time

    // Dynamically create list items for each statistic
    const statistics = { // Object containing statistics data
        'Total Pages Discovered': data.totalLinksFound,
        'Path Found': data.pathFound ? 'Yes' : 'No',
        'Path Length': data.pathLength,
        'Search Time': `${searchTimeFormatted} seconds`, // Updated to use formatted time
        'Search Method': data.searchMethod
    };

    for (const [label, value] of Object.entries(statistics)) { // Iterating over statistics data
        const statItem = document.createElement('li'); // Creating list item element
        statItem.textContent = `${label}: ${value}`; // Setting text content of list item
        statsList.appendChild(statItem); // Appending list item to statistics list
    }

    statsElement.appendChild(statsList); // Appending statistics list to statistics element
}

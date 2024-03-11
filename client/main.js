console.log("Starting fetch request...");

// Flag to indicate if an abort has been requested.
let abortRequested = false;
let searchIntervalId; // ID of the interval that updates the elapsed time

document.addEventListener('DOMContentLoaded', (event) => {
    console.log("Starting fetch request...");

    // Flag to indicate if an abort has been requested.
    let abortRequested = false;
    let searchIntervalId; // ID of the interval that updates the elapsed time

    document.getElementById('wiki-form').addEventListener('submit', function(event) {
        event.preventDefault();
        abortRequested = false;  // Reset the abort flag on new search

        document.getElementById('path').innerHTML = '';
        document.getElementById('logs').innerHTML = '';
        document.getElementById('stats').innerHTML = '';
        document.getElementById('searching').innerHTML = 'Searching...';

        // Start the timer and update the elapsed time every second
        const startTime = Date.now();
        searchIntervalId = setInterval(() => {
            const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
            document.getElementById('searching').innerHTML = `Searching... ${elapsedTime} seconds`;
        }, 1000);

        var startPage = document.getElementById('start-page').value;
        var finishPage = document.getElementById('finish-page').value;

        console.log("Sending fetch request...");
        fetch('/find_path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start: startPage,
                finish: finishPage
            })
        })
        .then(response => {
            if (response.status === 429) {
                throw new Error('You have made too many requests. Please try again later.');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error:', error);
            var pathElement = document.getElementById('path');
            pathElement.innerHTML = '<p>Error: ' + error.message + '</p>';
        })
        .then(data => {
            clearInterval(searchIntervalId);  // Stop the search timer
            document.getElementById('searching').innerHTML = '';  // Clear the searching message

            // If an abort was requested or if there's no data/error, do not process further.
            if (abortRequested || !data || data.error) {
                console.log('Search aborted or error occurred, not processing data.');
                return;
            }

            console.log('about to output data');
            console.log(data);

            // output path
            var pathElement = document.getElementById('path');
            pathElement.innerHTML = '<ul>';
            data.path.forEach(function(page) {
                pathElement.innerHTML += '<li><a href="' + page + '">' + decodeURIComponent(page) + '</a></li>';
            });
            pathElement.innerHTML += '</ul>';

            // output logs
            var logsElement = document.getElementById('logs');
            logsElement.innerHTML = '<pre>' + data.logs.join('\n') + '</pre>';

            // output stats
            var statsElement = document.getElementById('stats');
            statsElement.innerHTML = '<ul>' +
                                    '<li>Elapsed time: ' + data.time + '</li>' +
                                    '<li>Number of discovered pages: ' + data.discovered + '</li>' +
                                    '</ul>';
        });
    });

    function abortSearch() {
        if (!abortRequested) { // Only run if abort hasn't already been requested
            console.log("Aborting search...");
            abortRequested = true; // Signal that an abort has been requested
            
            fetch('/abort_search', { method: 'POST' })
            .then(response => {
                if(response.ok) {
                    console.log('Search aborted successfully.');
                    document.getElementById('searching').innerHTML = 'Search has been aborted.';
                } else {
                    return response.text().then(text => {
                        throw new Error('Failed to abort the search. Status: ' + response.status + ' Response: ' + text);
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('searching').innerHTML = 'Error: ' + error.message;
            });
    
            clearInterval(searchIntervalId);  // Clear the interval when the search is aborted
        }
    }
    // Bind the abort function to the abort button
    document.getElementById('abort-btn').addEventListener('click', abortSearch);

    console.log("Finished fetch request setup.");
});

window.onload = function() {
    console.log("Starting fetch request...");

    document.getElementById('wiki-form').addEventListener('submit', function(event) {
        event.preventDefault();

        var startPage = document.getElementById('start-page').value;
        var finishPage = document.getElementById('finish-page').value;

        var logsElement = document.getElementById('logs-content');
        var statsElement = document.getElementById('stats-content');
        var resultsList = document.getElementById('results-list');

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
            logsElement.innerHTML = error.message + (data && data.time ? '<p>Elapsed time: ' + data.time + '</p>' : '');
        })
        .then(data => {
            if (!data) return; // if there was an error, data will be undefined

            console.log(data);

            // Clear previous results
            resultsList.innerHTML = '';
            logsElement.innerHTML = '';
            statsElement.innerHTML = '';

            // Output path
            let pathHtml = '<ul>';
            data.path.forEach(function(page) {
                pathHtml += '<li><a href="' + page + '">' + decodeURIComponent(page) + '</a></li>';
            });
            pathHtml += '</ul>';
            resultsList.innerHTML = pathHtml;

            // Output discovered pages (logs)
            let logsHtml = '<pre>';
            data.logs.forEach(function(log) {
                logsHtml += log + '\n';
            });
            logsHtml += '</pre>';
            logsElement.innerHTML = logsHtml;

            // Output stats
            let statsHtml = '<ul>';
            statsHtml += '<li>Elapsed time: ' + data.time + '</li>';
            statsHtml += '<li>Number of discovered pages: ' + data.logs.length + '</li>';
            statsHtml += '</ul>';
            statsElement.innerHTML = statsHtml;

            console.log("Finished fetch request...");
        });
    });
};
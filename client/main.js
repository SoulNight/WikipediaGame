console.log("Starting fetch request...");
document.getElementById('wiki-form').addEventListener('submit', function(event) {
    event.preventDefault();

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
        var logsElement = document.getElementById('logs');
        logsElement.innerHTML = error.message + (data && data.time ? '<p>Elapsed time: ' + data.time + '</p>' : '');
    })
    .then(data => {
        if (!data) return; // if there was an error, data will be undefined
        console.log(data);
        var pathElement = document.getElementById('path');
        var logsElement = document.getElementById('logs');
        pathElement.innerHTML = ''; // clear previous path
        logsElement.innerHTML = ''; // clear previous logs
        var pathHtml = '<ul>';
        data.path.forEach(function(page) {
            pathHtml += '<li><a href="' + page + '">' + decodeURIComponent(page) + '</a></li>';
        });
        pathHtml += '</ul>';
        pathElement.innerHTML = pathHtml;
        var logsHtml = '<pre>';
        data.logs.forEach(function(log) {
            logsHtml += log + '\n';
        });
        logsHtml += '\n<p>Elapsed time: ' + data.time + '</p>';
        logsHtml += '</pre>';
        logsElement.innerHTML = logsHtml;
    });
});
console.log("Finished fetch request...");

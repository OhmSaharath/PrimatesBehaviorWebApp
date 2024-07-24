document.addEventListener("DOMContentLoaded", function() {
    
    // Parameter Initialization

    const gameContainer = document.getElementById('game-container');
    const signalUrlTemplate = gameContainer.getAttribute('data-signal-url');
    const configUrlTemplate = gameContainer.getAttribute('data-config-url');
    
    const button = document.createElement('button');
    const gameInstanceId = getGameInstanceIdFromURL();

    let config = {
        interval_correct: 2,  // Default wait time for correct click
        interval_incorrect: 5,  // Default wait time for incorrect click
        interval_absent: 60  // Default wait time for absent click
    };

    // Fetch game configuration
    const configUrl = configUrlTemplate.replace('0', gameInstanceId);
    fetch(configUrl)
        .then(response => response.json())
        .then(data => {
            if (data) {
                config = data;
            }
        })
        .catch(error => console.error('Error fetching config:', error));



    
    button.onclick = function(event) {
        console.log('correct')
        event.stopPropagation();  // Prevent the background click event from firing
        button.style.backgroundColor = 'green';

        // Activate the pump
        sendSignal(gameInstanceId); // Call the function to send signal

        // wait for "interval_correct" second then convert back to yellow
        console.log('waitfor'+config.interval_correct+'second')
        setTimeout(() => {
            button.style.backgroundColor = 'yellow';
        }, config.interval_correct * 1000);  // Convert seconds to milliseconds
    };

    document.body.onclick = function() {
        button.style.backgroundColor = 'red';
        console.log('incorrect')
        console.log('waitfor'+config.interval_incorrect+'second')

        // wait for "interval_incorrect" second then convert back to yellow
        setTimeout(() => {
            button.style.backgroundColor = 'yellow';
        }, config.interval_incorrect * 1000);  // Convert seconds to milliseconds
    };

    function getGameInstanceIdFromURL() {
        // Extract gameInstanceId from current URL
        const pathParts = window.location.pathname.split('/');
        return parseInt(pathParts[pathParts.length - 1]); // Assuming the gameInstanceId is the last part of the URL path
    }

    function sendSignal(gameInstanceId) {
        // Replace the placeholder with the actual gameInstanceId
        const signalUrl = signalUrlTemplate.replace('0', gameInstanceId);
        
        // Use AJAX to send signal to Django backend
        const xhr = new XMLHttpRequest();
        xhr.open('GET', signalUrl, true); 
        xhr.onload = function () {
            if (xhr.status === 200) {
                console.log('Signal sent successfully');
            } else {
                console.error('Error sending signal');
            }
        };
        xhr.send();
    }

    gameContainer.appendChild(button);
    
});
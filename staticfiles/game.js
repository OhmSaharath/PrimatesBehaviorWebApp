document.addEventListener("DOMContentLoaded", function() {
    
    const gameContainer = document.getElementById('game-container');
    const signalUrlTemplate = gameContainer.getAttribute('data-signal-url');
    
    const button = document.createElement('green');
    const gameInstanceId = getGameInstanceIdFromURL();
    
    button.onclick = function() {
        console.log('hello')
        //utton.style.backgroundColor = 'blue';
        sendSignal(gameInstanceId); // Call the function to send signal
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
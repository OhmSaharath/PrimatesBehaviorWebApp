document.addEventListener("DOMContentLoaded", function() {
    
    // Parameter Initialization

    const gameContainer = document.getElementById('game-container');
    const signalUrlTemplate = gameContainer.getAttribute('data-signal-url');
    const configUrlTemplate = gameContainer.getAttribute('data-config-url');
    const gameInstanceId = getGameInstanceIdFromURL();
    
    const button = document.createElement('button');
    let buttonSize = 95;  // Initial size percentage of the button
    const minButtonSizePx = 50;  // Minimum button size in pixels (0.5 cm = 50 pixels)
    const minClickAreaPx = 200;  // Minimum click area size in pixels (2 cm = 200 pixels), special case when button is less than 2cmx2cm
    
    button.style.position = 'absolute';  // Allow positioning the button absolutely

    // Create an overlay for handling the special click area
    const overlay = document.createElement('div');
    overlay.style.position = 'absolute';
    overlay.style.backgroundColor = 'transparent';  // Make the overlay invisible
    overlay.style.pointerEvents = 'auto';  // Ignore pointer events initially

    updateButtonSize(buttonSize); // initialize button


    let config = {
        interval_correct: 2,  // Default wait time for correct click
        interval_incorrect: 5,  // Default wait time for incorrect click
        interval_absent: 60  // Default wait time for absent click
    };

    
    let inactivityTimer = null; // Variable to convert state of inactivity back to original
    let actionBlocked = false;   // Flag to track if actions are blocked
    let Trials = 0;  // Global variable to count trials
    let trialResults = [];  // Array to store results of last 10 trials


    // Fetch game configuration
    const configUrl = configUrlTemplate.replace('0', gameInstanceId);
    fetch(configUrl)
        .then(response => response.json())
        .then(data => {
            if (data) {
                config = data;
            }
            resetInactivityTimer();  // Start the inactivity timer after config is fetched
        })
        .catch(error => console.error('Error fetching config:', error));


    
    // buttonclick
    button.onclick = function(event) {
        if (actionBlocked) return;  // Prevent action if blocked
        console.log('correct')
        event.stopPropagation();  // Prevent the background click event from firing

        updateButtonColorAndTrials('green'); 



        // Activate the pump
        sendSignal(gameInstanceId); // Call the function to send signal

        // wait for "interval_correct" second then convert back to yellow
        console.log('waitfor'+config.interval_correct+'second')
        setTimeout(() => {
            button.style.backgroundColor = 'yellow';
            actionBlocked = false;  // Allow actions again after button reverts to yellow
            resetInactivityTimer();  // Start the inactivity timer after config is fetched
        }, config.interval_correct * 1000);  // Convert seconds to milliseconds
    };

    // Special case, tolerance window
    overlay.onclick = function(event) {
        if (actionBlocked) return;  // Prevent action if blocked
        event.stopPropagation();  // Prevent the background click event from firing
        updateButtonColorAndTrials('green');
        sendSignal(gameInstanceId); // Call the function to send signal

        setTimeout(() => {
            button.style.backgroundColor = 'yellow';
            actionBlocked = false;  // Allow actions again after button reverts to yellow
            resetInactivityTimer();  // Reset inactivity timer after button reverts to yellow
        }, config.interval_correct * 1000);  // Convert seconds to milliseconds
    };

    // Incorrect case, background click
    document.body.onclick = function() {
        if (actionBlocked) return;  // Prevent action if blocked
        console.log('incorrect')
        updateButtonColorAndTrials('red');
        console.log('waitfor'+config.interval_incorrect+'second')


        // wait for "interval_incorrect" second then convert back to yellow
        setTimeout(() => {
            button.style.backgroundColor = 'yellow';
            actionBlocked = false;  // Allow actions again after button reverts to yellow
            resetInactivityTimer();  // Start the inactivity timer after config is fetched
        }, config.interval_incorrect * 1000);  // Convert seconds to milliseconds
    };

    function updateButtonColorAndTrials(color) {
        button.style.backgroundColor = color;
        if (color !== 'yellow') {
            Trials++;  // Increment Trials only if color is not yellow
            if (color === 'green') {
                trialResults.push(true);
            } else if (color === 'red') {
                trialResults.push(false);
            }
            if (trialResults.length > 10) {
                trialResults.shift();  // Keep only the last 10 results
            }
            console.log('Trials:', Trials, 'Recent 10 Trials:', trialResults);
            updateButtonBasedOnPerformance();
        }
        actionBlocked = true;  // Block actions when color is green or red
    }

    function updateButtonBasedOnPerformance() {
        if (trialResults.length === 10) {
            const correctResponses = trialResults.filter(result => result).length;
            const correctRate = correctResponses / trialResults.length;
            if (correctRate > 0.8) {
                console.log('Correct rate more than 80%, reducing the size of rectangle by 90%');

                // Randomize the button's position within the game container
                const containerWidth = gameContainer.clientWidth;
                const containerHeight = gameContainer.clientHeight;
                const buttonWidth = button.offsetWidth;
                const buttonHeight = button.offsetHeight;
                const randomX = Math.random() * (containerWidth - buttonWidth);
                const randomY = Math.random() * (containerHeight - buttonHeight);
                button.style.left = `${randomX}px`;
                button.style.top = `${randomY}px`;

                // Update the button size after repositioning
                buttonSize *= 0.1;  // Reduce the size by 90% of the previous size
                updateButtonSize(buttonSize);

            } 
            // Reset the trialResults array for the next 10 trials
            trialResults = [];
        }
    }

    function updateButtonSize(sizePercentage) {
        const containerWidth = gameContainer.clientWidth;
        const containerHeight = gameContainer.clientHeight;
        const newWidth = (containerWidth * sizePercentage) / 100;
        const newHeight = (containerHeight * sizePercentage) / 100;

        // Ensure the button does not shrink below the minimum size
        const finalWidth = newWidth < minButtonSizePx ? minButtonSizePx : newWidth;
        const finalHeight = newHeight < minButtonSizePx ? minButtonSizePx : newHeight;

        button.style.width = `${finalWidth}px`;
        button.style.height = `${finalHeight}px`;

        // Update the overlay size and position
        const overlaySize = Math.max(minClickAreaPx, Math.max(finalWidth, finalHeight));
        overlay.style.width = `${overlaySize}px`;
        overlay.style.height = `${overlaySize}px`;
        overlay.style.left = `${parseFloat(button.style.left) + (finalWidth - overlaySize) / 2}px`;
        overlay.style.top = `${parseFloat(button.style.top) + (finalHeight - overlaySize) / 2}px`;
    }


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

    // Absent case
    function resetInactivityTimer() {
        if (inactivityTimer) {
            clearTimeout(inactivityTimer);
        }
        inactivityTimer = setTimeout(() => {
            console.log('no activity detected')

            updateButtonColorAndTrials('red');

            setTimeout(() => {
                button.style.backgroundColor = 'yellow';
                actionBlocked = false;  // Allow actions again after button reverts to yellow
                resetInactivityTimer();  // Restart the inactivity timer after button reverts to yellow
            }, config.interval_incorrect * 1000);
        }, config.interval_absent * 1000);
    }

    gameContainer.appendChild(button);
    gameContainer.appendChild(overlay);
    
});
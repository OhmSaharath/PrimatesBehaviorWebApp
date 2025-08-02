document.addEventListener("DOMContentLoaded", function() {
    
    // Parameter Initialization

    const gameContainer = document.getElementById('game-container');
    const signalUrlTemplate = gameContainer.getAttribute('data-signal-url');
    const configUrlTemplate = gameContainer.getAttribute('data-config-url');
    const reportUrlTemplate = gameContainer.getAttribute('report-update-url');
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


    //let config = {
    //    interval_correct: 2,  // Default wait time for correct click
    //    interval_incorrect: 5,  // Default wait time for incorrect click
    //    interval_absent: 60  // Default wait time for absent click
    //};

    
    let inactivityTimer = null; // Variable to convert state of inactivity back to original
    let actionBlocked = false;   // Flag to track if actions are blocked
    let Trials = 0;  // Global variable to count trials
    let Last10trialResults = [];  // Array to store results of last 10 trials
    let config = null;

    // Fetch game configuration
    const configUrl = configUrlTemplate.replace('0', gameInstanceId);
    fetch(configUrl)
        .then(response => response.json())
        .then(data => {
            if (data) {
                console.log(data);
                config = data;
            }
            resetInactivityTimer();  // Start the inactivity timer after config is fetched
        })
        .catch(error => console.error('Error fetching config:', error));
    
    console.log(config);

    // Get the audio elements
    const correctSound = document.getElementById('correct-sound');
    const incorrectSound = document.getElementById('incorrect-sound');

    // Initialize a variable to track touch duration
    let touchStartTime = null;
    let accumulatedDuration = 0;
    let durationCheckInterval = null; // Interval for checking accumulated duration
    
    // Correct case. Shared event handlers for touch and mouse
    const correct_startHandler = (event) => {
        event.preventDefault(); // Prevent default behavior
        event.stopPropagation(); // Prevent event from propagating to other elements
        touchStartTime = Date.now();

        // Change the button color to orange while pressing
        button.style.backgroundColor = 'orange';
    
        // Start checking the duration periodically
        durationCheckInterval = setInterval(() => {
            if (!touchStartTime) return; // Skip if there's no active touch
            const currentTime = Date.now();
            const touchDuration = currentTime - touchStartTime + accumulatedDuration;
    
            console.log(`Checking Duration: ${touchDuration}ms`);
    
            // If duration meets the requirement, trigger correct state
            if (touchDuration >= config.button_holdDuration) {
                console.log('Hold duration met, triggering correct state');
                updateButtonColorAndTrials('green');
                updateReport(gameInstanceId, 'correct', Trials);
                sendSignal(gameInstanceId);
    
                accumulatedDuration = 0;
                touchStartTime = null; // Reset touch start time
                clearInterval(durationCheckInterval); // Stop checking
    
                // Reset after correct state
                setTimeout(() => {
                    button.style.backgroundColor = 'yellow';
                    actionBlocked = false;
                    resetInactivityTimer();
                }, config.interval_correct * 1000);
            }
        }, 100); // Check every 100ms (adjust as needed)
    };
    
    const correct_endHandler = (event) => {
    event.preventDefault(); // Prevent default behavior
    event.stopPropagation(); // Prevent event from propagating to other elements
    if (touchStartTime) {
        const touchEndTime = Date.now();
        accumulatedDuration += touchEndTime - touchStartTime;
        console.log(`Touch ended. Accumulated Duration: ${accumulatedDuration}ms`);
        touchStartTime = null;
        // Change the button color back to yellow after releasing
        button.style.backgroundColor = 'yellow';
    }

    // Clear the duration checking interval
    clearInterval(durationCheckInterval);
    };

    // Add event listeners for both touch and mouse events
    button.addEventListener('mousedown', correct_startHandler);
    button.addEventListener('mouseup', correct_endHandler);
    button.addEventListener('touchstart', correct_startHandler);
    button.addEventListener('touchend', correct_endHandler);

    // Special case, tolerance window -> Green
    overlay.addEventListener('mousedown', correct_startHandler);
    overlay.addEventListener('mouseup', correct_endHandler);
    overlay.addEventListener('touchstart', correct_startHandler);
    overlay.addEventListener('touchend', correct_endHandler);

    // Incorrect case, background click -> Red
    const incorrect_Handler = (event) => {
        event.preventDefault(); // Prevent default behavior
        if (actionBlocked) return;  // Prevent action if blocked
        console.log('incorrect')

        // update button
        updateButtonColorAndTrials('red');

        // populate reports
        updateReport(gameInstanceId, 'incorrect', Trials)

        console.log('waitfor'+config.interval_incorrect+'second')

        // reset previos accumulated duration
        accumulatedDuration = 0;


        // wait for "interval_incorrect" second then convert back to yellow
        setTimeout(() => {
            button.style.backgroundColor = 'yellow';
            actionBlocked = false;  // Allow actions again after button reverts to yellow
            resetInactivityTimer();  // Start the inactivity timer after config is fetched
        }, config.interval_incorrect * 1000);  // Convert seconds to milliseconds
    }

    // Add event listeners for both touch and mouse events for incorrect state
    document.body.addEventListener('mousedown', incorrect_Handler);
    document.body.addEventListener('touchstart', incorrect_Handler);



    function updateButtonColorAndTrials(color) {
        button.style.backgroundColor = color;
        if (color !== 'yellow') {
            Trials++;  // Increment Trials only if color is not yellow
            if (color === 'green') {
                Last10trialResults.push(true);

                correctSound.currentTime = 0;  // Reset sound to start
                correctSound.play();  // Play correct sound

            } else if (color === 'red') {
                Last10trialResults.push(false);
                
                incorrectSound.currentTime = 0;  // Reset sound to start
                incorrectSound.play();  // Play incorrect sound

            }
            if (Last10trialResults.length > 10) {
                Last10trialResults.shift();  // Keep only the last 10 results
            }
            console.log('Trials:', Trials, 'Recent 10 Trials:', Last10trialResults);
            updateButtonBasedOnPerformance();
        }
        actionBlocked = true;  // Block actions when color is green or red
    }

    function randomizeButtonPositionandUpdateSize(buttonScale) {
        // Randomize the button's position within the game container
        const containerWidth = gameContainer.clientWidth;
        const containerHeight = gameContainer.clientHeight;
        const buttonWidth = button.offsetWidth;
        const buttonHeight = button.offsetHeight;

        // Ensure the button stays within container boundaries
        const maxX = containerWidth - buttonWidth;
        console.log(maxX)
        const maxY = containerHeight - buttonHeight;
        const randomX = Math.max(0, Math.random() * maxX);
        console.log(randomX)
        const randomY = Math.max(0, Math.random() * maxY);
        button.style.left = `${randomX}px`;
        button.style.top = `${randomY}px`;

        // Update the button size after repositioning
        buttonSize *= buttonScale;  // Reduce the size by 90% of the previous size
        updateButtonSize(buttonSize);
    }

    function updateButtonBasedOnPerformance() {
        if (Last10trialResults.length === 10) {
            const bscale = 0.5; 
            const correctResponses = Last10trialResults.filter(result => result).length;
            const correctRate = correctResponses / Last10trialResults.length;
            console.log("correct rate "+ correctRate)
            if (correctRate >= 0.8) {
                console.log('Correct rate more than 80%, reducing the size of rectangle by 90%');

                
                randomizeButtonPositionandUpdateSize(bscale);
                // Reset the Last10trialResults array for the next 10 trials
                Last10trialResults = [];

            } 
            
        }
        else {
            const bscale = 1;
            randomizeButtonPositionandUpdateSize(bscale);
        }
    }

    function updateButtonSize(sizePercentage) {
        const containerWidth = gameContainer.clientWidth;
        const containerHeight = gameContainer.clientHeight;
    
        // Calculate the smaller dimension of the container for a square button
        const containerMinDimension = Math.min(containerWidth, containerHeight);
    
        const newSize = (containerMinDimension * sizePercentage) / 100;
    
        // Ensure the button does not shrink below the minimum size
        const finalSize = newSize < minButtonSizePx ? minButtonSizePx : newSize;

        button.style.width = `${finalSize}px`;
        button.style.height = `${finalSize}px`;

        // Update the overlay size and position for the click area
        if (finalSize < minClickAreaPx) {
            const overlaySize = Math.max(minClickAreaPx, finalSize);
            overlay.style.width = `${overlaySize}px`;
            overlay.style.height = `${overlaySize}px`;
            overlay.style.left = `${parseFloat(button.style.left) + (finalSize - overlaySize) / 2}px`;
            overlay.style.top = `${parseFloat(button.style.top) + (finalSize - overlaySize) / 2}px`;
            overlay.style.pointerEvents = 'auto';  // Enable pointer events
        } else {
            overlay.style.pointerEvents = 'none';  // Disable pointer events
            overlay.style.width = '0px';
            overlay.style.height = '0px';
        }
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

    function updateReport(gameInstanceId, status, trials_num){

        // Replace the placeholder with the actual gameInstanceId
        const reportUrl = reportUrlTemplate.replace('0', gameInstanceId);

        // Current timestamp in ISO format
        const timestamp = new Date().toISOString();  


        // Get the current button's dimensions
        const buttonWidth = button.offsetWidth;
        const buttonHeight = button.offsetHeight;

        // Calculate the area of the button, resulting in px
        const area = buttonWidth * buttonHeight;

        // Set the isCorrect variable based on the status
        const isCorrect = (status === 'correct') ? true : false;


        // Use AJAX to send signal to Django backend
        const xhr = new XMLHttpRequest();
        xhr.open('POST', reportUrl, true); 
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));  // CSRF token for security
        // Send the data with timestamp, area, status, and isCorrect boolean
        xhr.send(JSON.stringify({ 
            timestamp: timestamp, 
            area: area, 
            status: status,
            isCorrect: isCorrect,  // Store true if "correct", false otherwise
            trialsNum : trials_num
        }));

        // For debugging: log the button area, timestamp, status, and isCorrect
        console.log(`Button area: ${area} px², Timestamp: ${timestamp}, Status: ${status}, IsCorrect: ${isCorrect}, trialsNum: ${trials_num}`);

    }

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Absent case, call after every case 
    function resetInactivityTimer() {
        if (inactivityTimer) {
            clearTimeout(inactivityTimer);
        }
        inactivityTimer = setTimeout(() => {
            console.log('no activity detected')
            
            // update button
            updateButtonColorAndTrials('red');

            // populate reports
            updateReport(gameInstanceId, 'absent', Trials)

            

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
// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// Function to handle game logout
function gameLogout(instance) {
    const csrftoken = getCookie('csrftoken');
    fetch(gameLogoutUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            //'X-CSRFToken': '{{ csrf_token }}'
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ game_instance: instance })
    })
    .then(response => {
        if (response.ok) {
            alert("Data sent successfully!");
        } else {
            alert("Failed to send data.");
        }
    })
    .catch(error => console.error('Error:', error));
}

// Backup function for game logout
function gameLogout_back(instance){

    // Use AJAX to send signal to Django backend
    const xhr = new XMLHttpRequest();
    xhr.open('POST', gameLogoutUrl, true); 
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));  // CSRF token for security
    // Send the data with timestamp, area, status, and isCorrect boolean
    xhr.send(JSON.stringify({ 
        game_instance: instance, 
    }));
}


// Function to dynamically load game configuration form based on selected game type
document.addEventListener("DOMContentLoaded", function () {
    const gameChoiceField = document.getElementById("id_game_name");
    const configFormContainer = document.getElementById("gameConfigFormContainer");
    const configForm = document.getElementById("gameConfigForm");


    if (gameChoiceField) {  
        console.log('waiting for change');

        const gameType = gameChoiceField.value;

        console.log(gameType);

        if (gameType) {
            fetch(`/get-game-config-form/?game_type=${gameType}`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.form_html) {
                        configForm.innerHTML = data.form_html; // Update the form
                        configFormContainer.style.display = "block"; // Show the container
                    } else {
                        configFormContainer.style.display = "none"; // Hide the container
                    }
                })
                .catch((error) => {
                    console.error("Error fetching the configuration form:", error);
                    alert("An error occurred while fetching the configuration form.");
                });
        } else {
            configFormContainer.style.display = "none"; // Hide the container if no game is selected
        }

        gameChoiceField.addEventListener("change", function () {

            const gameType = this.value;

            console.log(gameType);

            //const gameType = this.value; // Get the selected game type

            if (gameType) {
                fetch(`/get-game-config-form/?game_type=${gameType}`)
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.form_html) {
                            configForm.innerHTML = data.form_html; // Update the form
                            configFormContainer.style.display = "block"; // Show the container
                        } else {
                            configFormContainer.style.display = "none"; // Hide the container
                        }
                    })
                    .catch((error) => {
                        console.error("Error fetching the configuration form:", error);
                        alert("An error occurred while fetching the configuration form.");
                    });
            } else {
                configFormContainer.style.display = "none"; // Hide the container if no game is selected
            }
        });
    }
});
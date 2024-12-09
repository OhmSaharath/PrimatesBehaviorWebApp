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

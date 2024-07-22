document.addEventListener("DOMContentLoaded", function() {
    const gameContainer = document.getElementById('game-container');
    
    const button = document.createElement('button');
    
    button.onclick = function() {
        // This is where you can add the logic for what happens after the button is pushed
        alert('Button Pushed!');
    };
    
    gameContainer.appendChild(button);
});
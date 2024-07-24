document.addEventListener("DOMContentLoaded", function() {
    const gameContainer = document.getElementById('game-container');
    
    const button = document.createElement('button');

    
    button.onclick = function() {
        button.style.backgroundColor = 'green';
    };
    
    gameContainer.appendChild(button);
    
});
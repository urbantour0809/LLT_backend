window.onload = function() {
    const flaskUrl = window.location.origin;

    console.log("Initializing script...");

    const date = new Date();
    const day = date.getDay();
    const diff = 6 - day;
    const nextSaturday = new Date(date.setDate(date.getDate() + diff));
    const formattedDate = nextSaturday.toISOString().split('T')[0];

    document.getElementById('game-info').innerText = `1137회차 (${formattedDate})`;

    console.log("Fetching lotto numbers from backend...");

    fetch(`${flaskUrl}/generate-lotto`)
        .then(response => {
            console.log("Received response from backend");
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Lotto numbers:", data.numbers);
            const gameNumbers = data.numbers;
            appendNumbers('game1', gameNumbers[0]);
            appendNumbers('game2', gameNumbers[1]);
            appendNumbers('game3', gameNumbers[2]);
            appendNumbers('game4', gameNumbers[3]);
            appendNumbers('game5', gameNumbers[4]);
        })
        .catch(error => {
            console.error('Error fetching lotto numbers:', error);
        });

    function appendNumbers(gameId, numbers) {
        console.log(`Appending numbers for ${gameId}:`, numbers);
        const gameDiv = document.getElementById(gameId);
        gameDiv.innerHTML = '';
        numbers.forEach(num => {
            const img = document.createElement('img');
            img.src = `src/image/numbers/${num}.png`;
            img.alt = `${num}번`;
            img.classList.add('lotto-ball');
            gameDiv.appendChild(img);
        });
    }
}

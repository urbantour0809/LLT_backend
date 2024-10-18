window.onload = function() {
    // Flask 서버의 경로는 현재 Cloudtype 서버에서 동일하므로 상대 경로로 호출
    const flaskUrl = window.location.origin;  // Flask 서버의 Cloudtype URL

    const date = new Date();
    const day = date.getDay();
    const diff = 6 - day;
    const nextSaturday = new Date(date.setDate(date.getDate() + diff));
    const formattedDate = nextSaturday.toISOString().split('T')[0];

    document.getElementById('game-info').innerText = `1137회차 (${formattedDate})`;

    fetch(`${flaskUrl}/generate-lotto`)
        .then(response => response.json())
        .then(data => {
            const gameNumbers = data.numbers;
            appendNumbers('game1', gameNumbers[0]);
            appendNumbers('game2', gameNumbers[1]);
            appendNumbers('game3', gameNumbers[2]);
            appendNumbers('game4', gameNumbers[3]);
            appendNumbers('game5', gameNumbers[4]);
        })
        .catch(error => console.error('Error fetching lotto numbers:', error));

    function appendNumbers(gameId, numbers) {
        const gameDiv = document.getElementById(gameId);
        gameDiv.innerHTML = '';
        numbers.forEach(num => {
            const img = document.createElement('img');
            img.src = `static/image/numbers/${num}.png`;
            img.alt = `${num}번`;
            img.classList.add('lotto-ball');
            gameDiv.appendChild(img);
        });
    }
}

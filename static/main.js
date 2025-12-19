// Загружаем список игроков
async function openPlayersModal() {
    const resp = await fetch("/kick_list");
    const players = await resp.json();

    const container = document.getElementById("playersList");
    container.innerHTML = "";

    if (players.length === 0) {
        container.innerHTML = "<p>Нет игроков онлайн</p>";
    } else {
        players.forEach(p => {
            container.innerHTML += `
                <div class="player-item">
                    ${p}
                    <button onclick="selectPlayer('${p}')">Кик</button>
                </div>
            `;
        });
    }

    document.getElementById("playersModal").style.display = "flex";
}

function closePlayersModal() {
    document.getElementById("playersModal").style.display = "none";
}

function selectPlayer(name) {
    document.getElementById("kickPlayerName").value = name;
    closePlayersModal();
    document.getElementById("reasonModal").style.display = "flex";
}

function closeReasonModal() {
    document.getElementById("reasonModal").style.display = "none";
}

// ===== БАН =====

async function openBanPlayersModal() {
    const resp = await fetch("/kick_list"); // список тот же
    const players = await resp.json();

    const container = document.getElementById("banPlayersList");
    container.innerHTML = "";

    if (players.length === 0) {
        container.innerHTML = "<p>Нет игроков онлайн</p>";
    } else {
        players.forEach(p => {
            container.innerHTML += `
                <div class="player-item">
                    ${p}
                    <button onclick="selectBanPlayer('${p}')">Бан</button>
                </div>
            `;
        });
    }

    document.getElementById("banPlayersModal").style.display = "flex";
}

function closeBanPlayersModal() {
    document.getElementById("banPlayersModal").style.display = "none";
}

function selectBanPlayer(name) {
    document.getElementById("banPlayerName").value = name;
    closeBanPlayersModal();
    document.getElementById("banReasonModal").style.display = "flex";
}

function closeBanReasonModal() {
    document.getElementById("banReasonModal").style.display = "none";
}

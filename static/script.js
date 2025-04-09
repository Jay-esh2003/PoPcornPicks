let allMovies = [];
let selected = new Map();

document.addEventListener("DOMContentLoaded", () => {
    fetch("/movies")
        .then(res => res.json())
        .then(data => {
            allMovies = data;
            const input = document.getElementById("movieInput");

            input.addEventListener("input", () => {
                // Remove any existing suggestion box
                const oldBox = document.querySelector(".suggestions");
                if (oldBox) oldBox.remove();
            
                const val = input.value.toLowerCase();
                if (!val) return;
            
                const suggestions = allMovies
                    .filter(m => m.title.toLowerCase().includes(val))
                    .slice(0, 5);
            
                const suggestionBox = document.createElement("ul");
                suggestionBox.classList.add("suggestions");
                suggestionBox.style.position = "absolute";
                suggestionBox.style.width = input.offsetWidth + "px";
            
                suggestions.forEach(m => {
                    const li = document.createElement("li");
                    li.textContent = m.title;
                    li.setAttribute("data-id", m.id);
            
                    li.addEventListener("click", () => {
                        selected.set(m.id, m.title);
                        updateSelected();
                        input.value = "";
                        suggestionBox.remove();
                    });
            
                    suggestionBox.appendChild(li);
                });
            
                // Make input container position: relative
                input.parentNode.style.position = "relative";
                input.parentNode.appendChild(suggestionBox);
            });
            
        });
});

function updateSelected() {
    const selectedDiv = document.getElementById("selectedMovies");
    selectedDiv.innerHTML = Array.from(selected.entries())
        .map(([id, title]) => `<span>${title}</span>`)
        .join("");
}

function getRecommendations() {
    const movieIds = Array.from(selected.keys());

    fetch("/recommend_by_movies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ movie_ids: movieIds })
    })
    .then(res => res.json())
    .then(data => {
        const resultDiv = document.getElementById("recommendations");
        resultDiv.innerHTML = "<h3>Recommended Movies:</h3>";
    
        const list = document.createElement("ul");
        list.classList.add("recommendation-list");
    
        data.recommendations.forEach(rec => {
            const li = document.createElement("li");
            li.innerHTML = `
                <div class="poster-card">
                    <img src="${rec.poster || ''}" alt="${rec.title}" />
                    <p>${rec.title}</p>
                </div>
            `;
            list.appendChild(li);
        });
    
        resultDiv.appendChild(list);
    });
    
}

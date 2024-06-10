document.addEventListener("DOMContentLoaded", function () {
  // Elementi del DOM
  var searchForm = document.getElementById("searchForm");
  var searchInput = document.getElementById("searchInput");
  var movieContainer = document.querySelector(".movie-container");
  var filters = document.getElementById("filters");
  var filterForm = document.getElementById("filterForm");
  var filterToggle = document.querySelector(".filter-toggle");

  // Inizializzazione
  initializeEvents();

  function initializeEvents() {

    searchForm.addEventListener("submit", searchMovies);
    filterForm.addEventListener("submit", applyFilters);
    filterToggle.addEventListener("click", toggleFilterPanel);

  }

  function searchMovies(event) {
    event.preventDefault();
    var searchText = searchInput.value.trim();
    fetch(`/search?query=${searchText}`)
      .then(handleResponse)
      .then(renderMovies)
      .catch(handleError);
  }

  function applyFilters(event) {
    event.preventDefault();
    var params = new URLSearchParams(new FormData(filterForm)).toString();
    console.log(params)
    fetch(`/api/filter?${params}`)
      .then(handleResponse)
      .then(renderMovies)
      .catch(handleError);
  }

  function toggleFilterPanel() {
    filters.style.display = filters.style.display === "none" ? "flex" : "none";
  }

  function renderMovies(movies) {
    var movieHTML = "";
    if (movies.length === 0) {
      movieHTML = "<p>Film non trovato</p>";
    } else {
      movies.forEach(function (movie) {
        movieHTML +=
          '<div class="movie-card" data-movie-id="' +
          movie._id +
          '" onclick="location.href=\'/movie/' +
          movie._id +
          "'\">";
        movieHTML +=
          '<img src="' +
          movie.poster +
          '" alt="Poster of ' +
          movie.title +
          '">';
        movieHTML += '<div class="movie-info">';
        movieHTML +=
          "<h2>" +
          movie.title +
          ' (<span class="movie-year">' +
          movie.year +
          "</span>)</h2>";
        movieHTML += "<p><strong>Genre:</strong> " + movie.genre + "</p>";
        movieHTML +=
          "<p><strong>Certificate:</strong> " + movie.certificate + "</p>";
        movieHTML +=
          "<p><strong>Duration:</strong> " + movie.duration + " min</p>";
        movieHTML +=
          '<p><strong>Rating:</strong> <span class="rating" data-rating="' +
          movie.rating +
          '">' +
          movie.rating +
          "</span></p>";
        movieHTML += "</div></div>";
      });
    }
    movieContainer.innerHTML = movieHTML;
    // Applica i colori delle valutazioni dopo il rendering dei film
    applyRatingColors();
  }


  function applyRatingColors() {
    var ratings = document.querySelectorAll(".rating");
    ratings.forEach(function (rating) {
      var value = parseFloat(rating.getAttribute("data-rating"));
      if (value < 6) {
        rating.style.color = "red";
      } else if (value >= 6 && value < 7.5) {
        rating.style.color = "yellow";
      } else if (value >= 7.5 && value < 9) {
        rating.style.color = "green";
      } else if (value >= 9) {
        rating.style.color = "purple";
      }
    });
  }

  function handleResponse(response) {
    if (!response.ok) {
      throw new Error("Errore nella richiesta al server: " + response.status);
    }
    return response.json();
  }

  function handleError(error) {
    console.error("Si è verificato un errore:", error);
    // Puoi gestire l'errore qui, ad esempio mostrando un messaggio all'utente
  }

 
});

document.addEventListener("DOMContentLoaded", function () {
  var movieCards = document.querySelectorAll(".movie-card");
  movieCards.forEach(function (card) {
    card.addEventListener("click", function () {
      var movieId = card.getAttribute("data-movie-id");
      window.location.href = "/movie/" + movieId;
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  var movieYears = document.querySelectorAll(".movie-year");
  movieYears.forEach(function (yearElem) {
    var year = yearElem.textContent;
    var yearInt = parseInt(year, 10);
    if (!isNaN(yearInt)) {
      yearElem.textContent = yearInt;
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const scoreButton = document.getElementById("score-button");
  const scoreInput = document.getElementById("user-score");
  const dateInput = document.getElementById("seen-date");
   const date = dateInput.value;
  const favoritesButton = document.getElementById("favorite-button");
  const watchlistButton = document.getElementById("seen-button");
  const movieId = window.location.pathname.split("/").pop(); // Assumendo che l'ID del film sia l'ultima parte dell'URL

  // Evento per gestire l'aggiunta/rimozione dai preferiti
  favoritesButton.addEventListener("click", function () {
    toggleFavorites(movieId);
  });

  // Evento per gestire l'aggiunta/rimozione dalla watchlist
  watchlistButton.addEventListener("click", function () {
    toggleWatchlist(movieId);
  });

  scoreButton.addEventListener("click", function () {
    const score = scoreInput.value;

    fetch(`/user_score/${movieId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ score: score }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          window.location.href = data.redirect_url; // Reindirizza alla homepage o a un'altra pagina
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });

  // Funzione per gestire l'aggiunta/rimozione dai preferiti
  function toggleFavorites(movieId) {
    fetch(`/add_to_favorites/${movieId}`, {
      method: "POST",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Errore durante l'aggiornamento dei preferiti");
        }
        return response.json();
      })
      .then((data) => {
        console.log(data.message); // Logga il messaggio di successo
        // Aggiorna l'interfaccia utente o fai altre azioni necessarie
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  // Funzione per gestire l'aggiunta/rimozione dalla watchlist
  function toggleWatchlist(movieId) {
    fetch(`/add_to_watchlist/${movieId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ date: date }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Errore durante l'aggiornamento della watchlist");
        }
        return response.json();
      })
      .then((data) => {
        console.log(data.message); // Logga il messaggio di successo
        // Aggiorna l'interfaccia utente o fai altre azioni necessarie
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
});

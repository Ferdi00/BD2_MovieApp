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
  }

  function parseYear(year) {
    var yearInt = parseInt(year, 10);
    return isNaN(yearInt) ? year : yearInt;
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

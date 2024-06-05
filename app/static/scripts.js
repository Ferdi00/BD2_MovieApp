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
  var movieCards = document.querySelectorAll(".movie-card");
  movieCards.forEach(function (card) {
    card.addEventListener("click", function () {
      var movieId = card.getAttribute("data-movie-id");
      window.location.href = "/movie/" + movieId;
    });
  });

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
  var searchForm = document.getElementById("searchForm");
  var searchInput = document.getElementById("searchInput");
  var movieContainer = document.querySelector(".movie-container");

  searchForm.addEventListener("submit", function (event) {
    event.preventDefault(); // Evita il comportamento predefinito di invio del modulo
    var searchText = searchInput.value.trim();

    fetch("/search?query=" + searchText)
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Errore nella richiesta al server: " + response.status
          );
        }
        return response.json();
      })
      .then((data) => {
        renderMovies(data);
      })
      .catch((error) => {
        console.error("Si è verificato un errore:", error);
        // Puoi gestire l'errore qui, ad esempio mostrando un messaggio all'utente
      });
  });

  function renderMovies(movies) {
    var movieHTML = "";
    movies.forEach(function (movie) {
      movieHTML += '<div class="movie-card" data-movie-id="' + movie._id + '">';
      movieHTML +=
        '<img src="' + movie.poster + '" alt="Poster of ' + movie.title + '">';
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
        '<p><strong>Rating:</strong> <span class="rating">' +
        movie.rating +
        "</span></p>";
      movieHTML += "</div></div>";
    });
    movieContainer.innerHTML = movieHTML;
  }

  var movieYears = document.querySelectorAll(".movie-year");
  movieYears.forEach(function (yearElem) {
    var year = yearElem.textContent;
    var yearInt = parseInt(year, 10);
    if (!isNaN(yearInt)) {
      yearElem.textContent = yearInt;
    }
  });
});
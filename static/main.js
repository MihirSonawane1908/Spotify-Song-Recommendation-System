document.addEventListener('DOMContentLoaded', () => {
    const songInput = document.getElementById('songInput');
    const songSuggestions = document.getElementById('songSuggestions');
    const searchButton = document.getElementById('searchButton');
    const songDetailsDiv = document.getElementById('songDetails');
    const recommendationButton = document.getElementById('recommendationButton');
    const popButton = document.getElementById('popButton');
    const genrerecommendationsDiv = document.getElementById('genrerecommendationsDiv');

    let songs = []; // Array to store song data fetched from CSV
    let selectedGenre = ''; // Variable to store the selected genre from song details

    // Event listener for input focus
    songInput.addEventListener('focus', () => {
        songSuggestions.style.display = 'block';
    });

    // Event listener for document click
    document.addEventListener('click', (event) => {
        if (!songInput.contains(event.target) && !songSuggestions.contains(event.target)) {
            songSuggestions.style.display = 'none';
        }
    });

    // Event listener for song input
    songInput.addEventListener('input', fetchSongs);

    // Event listener for search button
    searchButton.addEventListener('click', () => {
        const songName = songInput.value.trim();
        if (songName.length === 0) {
            alert('Please enter a song name.');
            return;
        }

        fetchSongDetails(songName);
    });

    // Function to fetch song suggestions based on user input
    function fetchSongs() {
        const input = songInput.value.trim().toLowerCase();
        if (input.length === 0) {
            songSuggestions.innerHTML = '';
            songSuggestions.style.display = 'none';
            return;
        }

        // Filter songs based on input text
        const filteredSongs = songs.filter(song => song.toLowerCase().includes(input));
        displaySongs(filteredSongs);
    }

    // Function to display filtered songs in autocomplete dropdown
    function displaySongs(songs) {
        songSuggestions.innerHTML = '';
        songs.forEach(song => {
            const option = document.createElement('div');
            option.textContent = song;
            option.addEventListener('click', () => {
                songInput.value = song;
                songSuggestions.style.display = 'none';
            });
            songSuggestions.appendChild(option);
        });
        songSuggestions.style.display = songs.length > 0 ? 'block' : 'none';
    }

    // Function to fetch song details based on song name
    function fetchSongDetails(songName) {
        fetch(`/get_song_details`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ song_name: songName })
        })
        .then(response => response.json())
        .then(data => {
            // Store the selected genre from song details
            selectedGenre = data.genre;
            songDetailsDiv.innerHTML = `
                <h2>Song Details:</h2>
                <p><strong>Song Name:</strong> ${data.name}</p>
                <p><strong>Artist:</strong> ${data.artist}</p>
                <p><strong>Album:</strong> ${data.album}</p>
                <p><strong>Genre:</strong> ${data.genre}</p>
            `;
            recommendationButton.style.display = 'inline-block'; // Show the recommendation button
        })
        .catch(error => console.error('Error fetching song details:', error));
    }

    // Event listener for genre recommendation button
    recommendationButton.addEventListener('click', () => {
        fetchGenreRecommendations(selectedGenre);
    });

    // Function to fetch genre recommendations based on selected genre
    function fetchGenreRecommendations(selectedGenre) {
        fetch('/get_genre_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ selected_genre: selectedGenre })
        })
        .then(response => response.json())
        .then(data => {
            displayGenreRecommendations(data);
        })
        .catch(error => {
            console.error('Error fetching genre recommendations:', error);
            alert('Error fetching genre recommendations. Please try again.');
        });
    }

    // Function to display genre recommendations in the HTML
    function displayGenreRecommendations(recommendations) {
        genrerecommendationsDiv.innerHTML = ''; // Clear previous recommendations if any

        if (!recommendations || recommendations.length === 0) {
            genrerecommendationsDiv.innerHTML = '<p>No recommendations found.</p>';
            return;
        }

        const ul = document.createElement('ul');
        recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.textContent = recommendation.track_name + ' - ' + recommendation.artists + ' - ' + recommendation.track_genre ;
            ul.appendChild(li);
        });
        genrerecommendationsDiv.appendChild(ul);
    }

    // Fetch song data from CSV
    fetch('/get_song_data')
        .then(response => response.json())
        .then(data => {
            songs = data.map(song => song.song_name); // Extract song names from data
        })
        .catch(error => console.error('Error fetching song data:', error));
});

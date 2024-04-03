import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import csv
import pandas as pd
import mysql.connector
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)
app.secret_key = '1234'

# Establish a MySQL connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='KpssM@190820',
    database='student_database'  # Change to your actual database name
)

# Route for showing the sign-up page
@app.route('/signup', methods=['GET'])
def show_signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user already exists in the database
        cursor = db.cursor()
        query = "SELECT * FROM student_register WHERE email = %s"
        cursor.execute(query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return 'User already exists'  # Display error message if user already exists
        else:
            # Insert new user into the database
            insert_query = "INSERT INTO student_register (email, password) VALUES (%s, %s)"
            cursor.execute(insert_query, (email, password))
            db.commit()
            session.clear()

            # Set session variable to indicate user is logged in after sign-up
        session['logged_in'] = True
        flash('Account created successfully! You can now log in.')  # Flash message for successful sign-up

            # Debugging: Print messages to console
        print('Redirecting to login page...')  # Check if this message is printed
        return redirect(url_for('show_login'))  # Redirect to login page after successful sign-up

    return render_template('signup.html')  # Render sign-up page if method is not POST

@app.route('/')
def show_login():
    return render_template('login.html')

# Route for handling login
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Perform authentication by querying the MySQL database
        cursor = db.cursor()
        query = "SELECT * FROM student_register WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()  # Fetch the first row (user) from the result

        if user:
            session['logged_in'] = True  # Set session variable to indicate user is logged in
            return redirect(url_for('index'))  # Redirect to home page after successful login
        else:
            return 'Invalid login credentials'

    return render_template('login.html')

# Route for the home page (protected route)
@app.route('/login')
def index():
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html')
    else:
        return redirect(url_for('show_login'))  # Redirect to login page if not logged in

# Logout route to clear session and redirect to login page
@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.clear()  # Clear session data
        return redirect(url_for('show_login'))  # Redirect to login page





# Route to fetch song data from CSV
@app.route('/get_song_data')
def get_song_data():
    songs = []

    # Get the directory path where the CSV file is located
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'static', 'info.csv')  # Assuming CSV file is in the static folder

    # Open and read the CSV file
    with open(csv_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Extract relevant information from the CSV row
            song_info = {
                'song_name': row['track_name'],
                'artist': row['artists'],
                'album': row['album_name'],
                'genre': row['track_genre'],
               
            }
            songs.append(song_info)

    return jsonify(songs)

# Route to handle song details request
@app.route('/get_song_details', methods=['POST'])
def get_song_details():
    data = request.get_json()
    song_name = data['song_name']

    # Get the directory path where the CSV file is located
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'static', 'info.csv')  # Assuming CSV file is in the static folder

    # Open and read the CSV file to find the song details
    with open(csv_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['track_name'] == song_name:
                song_details = {
                    'name': row['track_name'],
                    'artist': row['artists'],
                    'album': row['album_name'],
                    'genre': row['track_genre'],
                    
                }
                return jsonify(song_details)

    # Return an error message if song details are not found
    return jsonify({'error': 'Song details not found'})


# Load the data from the CSV file
def load_data():
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'static', 'sampled_dataset.csv')
    df = pd.read_csv(csv_path)
    return df

# Calculate cosine similarity for genre recommendations
def get_genre_recommendations(genre):
    df = load_data()

    # Filter data by genre
    genre_data = df[df['track_genre'] == genre]

    if genre_data.empty:
        return []

   # Calculate cosine similarity
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(genre_data[['danceability', 'popularity', 'energy', 'acousticness', 'instrumentalness']])
    genre_data[['danceability', 'popularity', 'energy', 'acousticness', 'instrumentalness']] = scaled_features

# Calculate cosine similarity
    similarities = cosine_similarity(genre_data[['danceability', 'popularity', 'energy', 'acousticness', 'instrumentalness']])

# Get top 10 similar songs
    similar_indices = similarities.argsort()[0][-11:-1][::-1]  # Exclude the selected song itself
    recommendations = genre_data.iloc[similar_indices].to_dict(orient='records')
    return recommendations


# Route to fetch genre recommendations based on selected genre
@app.route('/get_genre_recommendations', methods=['POST'])
def fetch_genre_recommendations():
    data = request.get_json()
    selected_genre = data['selected_genre']
    recommendations = get_genre_recommendations(selected_genre)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)

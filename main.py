import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# spotipy documentation: https://spotipy.readthedocs.io/en/2.24.0/
# spotify documentation: https://developer.spotify.com/documentation/web-api
# streamlit documentation: https://docs.streamlit.io/
# ( sp for spotipy and st for streamlit )


# Spotify API credentials loaded from environment variables
CLIENT_ID = os.getenv('CLIENT_ID') # instead of export SPOTIPY_CLIENT_ID='your-spotify-client-id'
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000' # Redirect URI for OAuth flow

# Initialize Spotify client with user authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope='user-top-read playlist-modify-private' # Scopes to access user top tracks and modify playlists
))


# Initialize Streamlit app and UI setup (title and icon)
st.set_page_config(page_title='Spotify Song Analysis', page_icon=':star:') #emoji
st.title('Spotify Top Songs Analysis')

#----------------------------------------------------------------------------------------------

# Dropdown to select the time range for top tracks
time_range = st.selectbox('Select time range', ['short_term', 'medium_term', 'long_term'])
top_tracks = sp.current_user_top_tracks(limit=16, time_range=time_range)

#----------------------------------------------------------------------------------------------

# Fetch track IDs and audio features
track_ids = [track['id'] for track in top_tracks['items']]  # Extracting track IDs
audio_features = sp.audio_features(track_ids)  # Get audio features for the selected tracks

# Create DataFrame with more audio features
df = pd.DataFrame(audio_features) # Convert audio features to DataFrame
df['track_name'] = [track['name'] for track in top_tracks['items']] #  Add track names
df['artist'] = [track['artists'][0]['name'] for track in top_tracks['items']]  # Add artist names
df = df[['track_name', 'artist', 'acousticness', 'energy', 'danceability', 'valence']]   # Select relevant columns
df.set_index('track_name', inplace=True) # Set track names as index for easier visualization


# Display bar chart of audio features
st.subheader('Audio Features for Top Tracks')
st.bar_chart(df[['acousticness', 'energy', 'danceability', 'valence']], height=500)

#---------------------------------------------------------------------------------------------

# Display album covers for top tracks in a 3-column grid
st.subheader("")

# Define the number of columns
num_columns = 4
columns = st.columns(num_columns)  # Create a list of columns

# Loop through each track and display the image in a grid
for idx, track in enumerate(top_tracks['items']):
    album_cover_url = track['album']['images'][0]['url']  # Get the album cover image URL
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    
    # Place each image in one of the columns
    with columns[idx % num_columns]:
        st.image(album_cover_url, caption=f"{track_name} - {artist_name}", width=150)

#----------------------------------------------------------------------------------------------

# Genre analysis for each artist
st.subheader('Top Genres')
artist_ids = [track['artists'][0]['id'] for track in top_tracks['items']]
genres = [sp.artist(artist_id)['genres'] for artist_id in artist_ids]
unique_genres = set([genre for sublist in genres for genre in sublist])
st.write("Your top genres:", ', '.join(unique_genres))


#----------------------------------------------------------------------------------------------
# Button to generate a playlist from the top tracks

#create the button in steamlit
if st.button('Generate Playlist from Top Tracks'):
    # Get current user ID
    user_id = sp.current_user()['id']
    
    # Create a new playlist
    playlist_name = f"{time_range.capitalize()} Top Tracks"
    playlist_description = "Generated with Streamlit and Spotipy based on your top tracks."
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description=playlist_description)
    
    # Add tracks to the playlist
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=track_ids)
    
    # Confirm playlist creation
    st.success(f"Playlist '{playlist_name}' created successfully!")

#----------------------------------------------------------------------------------------------

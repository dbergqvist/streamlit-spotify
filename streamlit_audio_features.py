# Streamlit

import requests
import streamlit as st

from spotipy_client.spotipy_client import SpotifyAPI


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style.css")

Types_of_Features = (
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "loudness",
    "speechiness",
    "tempo",
    "valence",
)

st.title("Hammer time!")
Name_of_Artist = st.text_input("Artist Name")
Name_of_Feat = st.selectbox("Feature", Types_of_Features)
button_clicked = st.button("OK")

# import spotipy_client as spc
import spotipy
import pandas as pd

client_id = "<your_client_id>"
client_secret = "<your_client_secret>"

spotify = SpotifyAPI(client_id, client_secret)

Data = spotify.search({"artist": f"{Name_of_Artist}"}, search_type="track")

need = []
for i, item in enumerate(Data["tracks"]["items"]):
    track = item["album"]
    track_id = item["id"]
    song_name = item["name"]
    popularity = item["popularity"]
    need.append(
        (
            i,
            track["artists"][0]["name"],
            track["name"],
            track_id,
            song_name,
            track["release_date"],
            popularity,
        )
    )

Track_df = pd.DataFrame(
    need,
    index=None,
    columns=(
        "Item",
        "Artist",
        "Album Name",
        "Id",
        "Song Name",
        "Release Date",
        "Popularity",
    ),
)

access_token = spotify.access_token

headers = {"Authorization": f"Bearer {access_token}"}
endpoint = "https://api.spotify.com/v1/audio-features/"

Feat_df = pd.DataFrame()
for id in Track_df["Id"].iteritems():
    track_id = id[1]
    lookup_url = f"{endpoint}{track_id}"
    # print(lookup_url)
    ra = requests.get(lookup_url, headers=headers)
    audio_feat = ra.json()
    # print(audio_feat)
    Features_df = pd.DataFrame(audio_feat, index=[0])
    Feat_df = Feat_df.append(Features_df)
    # print(Feat_df)

Full_Data = Track_df.merge(Feat_df, left_on="Id", right_on="id")

Sort_DF = Full_Data.sort_values(by=["Popularity"], ascending=False)

chart_df = Sort_DF[
    [
        "Artist",
        "Album Name",
        "Song Name",
        "Release Date",
        "Popularity",
        f"{Name_of_Feat}",
    ]
]

# Streamlit Chart

import altair as alt

feat_header = Name_of_Feat.capitalize()

st.header(f"{feat_header}" " vs. Popularity")
c = (
    alt.Chart(chart_df)
    .mark_circle()
    .encode(
        alt.X("Popularity", scale=alt.Scale(zero=False)),
        y=f"{Name_of_Feat}",
        color=alt.Color("Popularity", scale=alt.Scale(zero=False)),
        size=alt.value(200),
        tooltip=["Popularity", f"{Name_of_Feat}", "Song Name", "Album Name"],
    )
)

st.altair_chart(c, use_container_width=True)

st.header("Table of Attributes")
st.table(chart_df)


st.write("acousticness: Confidence measure from 0.0 to 1.0 on if a track is acoustic.")
st.write(
    "danceability: Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable."
)
st.write(
    "energy: Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy."
)
st.write(
    "instrumentalness: Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0."
)
st.write(
    "liveness: Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live."
)
st.write(
    "loudness: The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typical range between -60 and 0 db."
)
st.write(
    "speechiness: Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks."
)
st.write(
    "tempo: The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration."
)
st.write(
    "valence: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry)."
)


st.write(
    "Information about features is from:  https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/"
)

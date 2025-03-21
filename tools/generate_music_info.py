from dotenv import load_dotenv
from tinytag import TinyTag
import json
import os

class MusicInfoGenerator:
    def __init__(self):
        load_dotenv()
        self.music_path = os.path.join(os.getenv("MUSIC_DIR"), "Music")
        self.music_info = {}

    def get_mp3_info(self, file_path):
        try:
            tag = TinyTag.get(file_path)
            if tag:
                return {
                    "album": tag.album,         # album as string
                    "albumartist": tag.albumartist,   # album artist as string
                    "artist": tag.artist,        # artist name as string
                    "comment": tag.comment,       # file comment as string
                    "composer": tag.composer,      # composer as string
                    "disc": tag.disc,          # disc number as integer
                    "disc_total": tag.disc_total,    # total number of discs as integer
                    "genre": tag.genre,         # genre as string
                    "title": tag.title,         # title of the song as string
                    "track": tag.track,         # track number as integer
                    "track_total": tag.track_total,   # total number of tracks as integer
                    "year": tag.year,          # year or date as string
                    "duration": tag.duration      # audio duration in seconds as float
                }
            else:
                return None  # or raise an exception if tags are mandatory
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
        
    def generate(self):
        for artist in os.listdir(self.music_path):
            self.music_info[artist] = {}
            artist_path = os.path.join(self.music_path, artist)
            for album in os.listdir(artist_path):
                self.music_info[artist][album] = []
                album_path = os.path.join(artist_path, album)
                for song in os.listdir(album_path):
                    song_path = os.path.join(album_path, song)
                    song_info = self.get_mp3_info(song_path)
                    song_info["PATH"] = os.path.join("Music", artist, album, song)
                    self.music_info[artist][album].append(song_info)
                    self.music_info[artist][album].sort(key=(lambda x: x["track"]+(100*x["disc"])))

        with open("music_info.json", 'w') as mi_json:
            json.dump(self.music_info, mi_json, indent=4)

if __name__ == "__main__":
    mi_gen = MusicInfoGenerator()
    mi_gen.generate()
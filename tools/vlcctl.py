from dotenv import load_dotenv
import subprocess as sp
import socket
import select
import json
import time
import sys
import os

"""
Class to control vlc on the raspberry pi to play music
"""
class VLC_CTL:
    ADD = "add %s"
    ADDRESS = "localhost"
    PORT = 24680

    def __init__(self):
        load_dotenv()
        print("creating socket")
        self.socket = socket.socket()
        self.music = {}
        self.playlist = []

        self.socket.connect((VLC_CTL.ADDRESS, VLC_CTL.PORT))
        self.socket.settimeout(3.0)
        self.receive()

        with open("tools/music_info.json", 'r') as mi_json:
            self.music = json.load(mi_json)

    def execute(self, cmd:str):
        self.socket.send(f"{cmd}\n".encode())
        return self.receive()

    def receive(self, stop_point:bytes=b'>'):
        buffer = b''
        while True:
            r, _, _ = select.select([self.socket], [], [])
            if r:
                data = self.socket.recv(1024)
                if not data:
                    return None
                buffer += data
            if stop_point in buffer:
                break
        line, _, buffer = buffer.partition(stop_point)
        return line.decode()

    def play_all_songs(self):
        for artist in self.music:
            for song in self.music[artist]:
                print(song)
                self.execute(f"add {song}")
                self.playlist.append(song)
                break

    def play(self, song:str):
        self.execute(f"add {song}")
        self.playlist.append(song)

    def queue(self, song:str):
        self.execute(f"enqueue {song}")
        self.playlist.append(song)

    def remove(self, song:str):
        self.execute(f"delete {self.playlist.index(song)+3}")

    def get_length(self):
        return self.execute(f"get_length")
    
    def toggle_pause(self):
        self.execute(f"pause")

    def next(self):
        self.execute(f"next")
    
    def previous(self):
        self.execute(f"prev")

    def set_volume(self, volume:int):
        if (volume < 0 or volume > 256):
            return -1
        self.execute(f"volume {volume}")

    def get_playlist(self):
        # playlist = []
        # playlist_out = self.execute(f"playlist").split("\n")
        # start_reading = False
        # for line in playlist_out:
        #     if start_reading:
        #         name =  line.split(" ", maxsplit=)
        #     if "1 - Playlist" in line:
        return self.execute(f"playlist")
        

    def get_stats(self):
        return self.execute(f"stats")
    
    def get_info(self, playlist_id:int=-1):
        return self.execute(cmd = f"info" if playlist_id == -1 else f"info {playlist_id}")
    
    def clear_playlist(self):
        self.execute(f"clear")

    def goto_song(self, playlist_id:int):
        self.execute(f"goto {playlist_id}")

    def choose_song(self):
        i = 0
        for artist in self.music:
            print(f"{artist}")
        artist_choice = input("Choose an artist: ")
        for album in self.music[artist_choice]:
            print(f"{album}")
        album_choice = input("Choose an album: ")
        for song in self.music[artist_choice][album_choice]:
            title = song["title"]
            print(f"{i}: {title}")
            i += 1
        song_choice = self.music[artist_choice][album_choice][int(input("Choose a song: "))]["PATH"]
        music_dir = os.getenv("MUSIC_DIR")
        print(music_dir + song_choice)
        return music_dir + song_choice

        
    def display_options_menu(self):
        print("---Options---")
        print("1: queue song")
        print("2: play/pause")
        print("3: get length of song")
        print("4: next song")
        print("5: previous song")
        print("6: set volume")
        print("7: play song")
        print("8: get current song stats")
        print("9: remove song from playlist")
        print("10: get playlist")
        print("q: quit")

        opt = input("choose an option: ")
        match opt:
            case "1":
                self.queue(self.choose_song())
            case "2":
                self.toggle_pause()
            case "3":
                print(self.get_length())
            case "4":
                self.next()
            case "5":
                self.previous()
            case "6":
                vol = input("set volume to [0-256]: ")
                if self.set_volume(int(vol)) == -1:
                    print("volume must be a number between 0-256")
            case "7":
                self.play(self.choose_song())
            case "8":
                print(self.get_stats())
            case "9":
                self.remove(self.choose_song())
            case "10":
                print(self.get_playlist())
            case "q":
                # TODO: cleanup subprocesses
                exit()
    

if __name__ == "__main__":
    vlc = VLC_CTL()

    while (True):
        vlc.display_options_menu()
from dotenv import load_dotenv
import subprocess as sp
import socket
import select
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
        self.socket.connect((VLC_CTL.ADDRESS, VLC_CTL.PORT))
        self.songs = {}
        self.get_songs()

    def execute(self, cmd:str):
        self.socket.send(cmd.encode())

    def get_songs(self):
        song_dir = os.getenv("SONG_DIR")
        for artist in os.listdir(song_dir):
            self.songs[artist] = []
            for song in os.listdir(f"{song_dir}/{artist}"):
                if song.endswith(".mp3"):
                    self.songs[artist].append(f"{song_dir}/{artist}/{song}")

    def play_all_songs(self):
        for artist in self.songs:
            for song in self.songs[artist]:
                print(song)
                self.execute(f"add {song}\n")
                break

    def play_song(self, song:str):
        self.execute(f"add {song}\n")

    def queue_song(self, song:str):
        self.execute(f"enqueue {song}\n")

    def get_length(self):
        self.execute("get_length\n")
        return self.socket.recv(1024).decode()
    
    def display_options_menu(self):
        print("---Options---")
        print("1: queue song")
        print("2: play/pause")
        print("3: get length of song")
        print("4: next song")
        print("5: previous song")
        print("6: set volume")
        print("7: play song")
        print("q: quit")

        opt = input("choose an option: ")
        match opt:
            case "1":
                i = 0
                for artist in self.songs:
                    for song in self.songs[artist]:
                        print(f"{i}: {song}")
                        i += 1
                self.queue_song(self.songs["Agust D"][int(input("Choose song to queue: "))])
            case "2":
                self.execute("pause\n")
            case "3":
                print(self.get_length())
            case "4":
                self.execute("next\n")
            case "5":
                self.execute("prev\n")
            case "6":
                vol = input("set volume to [0-256]: ")
                self.execute(f"volume {vol}\n")
            case "7":
                i = 0
                for artist in self.songs:
                    for song in self.songs[artist]:
                        print(f"{i}: {song}")
                        i += 1
                self.play_song(self.songs["Agust D"][int(input("Choose song to queue: "))])
            case "q":
                # TODO: cleanup subprocesses
                exit()
    

if __name__ == "__main__":
    vlc = VLC_CTL()

    while (True):
        vlc.display_options_menu()
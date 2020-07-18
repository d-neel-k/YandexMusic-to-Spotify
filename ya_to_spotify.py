import logging
import json

import requests
from yandex_music.client import Client

from config import spotify_user_token
from config import spotify_user_id
from config import yandex_login
from config import yandex_password


class YaMusicToSpotify:
	def __init__(self):
		self.userID = spotify_user_id
		self.userToken = spotify_user_token
		self.userYaLogin = yandex_login
		self.userYaPassword = yandex_password

	def getNameTrack(self):
		'''Grab liked tracks from Yandex Music and create list of tracks and artists'''
		client = Client()
		client = Client.from_credentials(self.userYaLogin, self.userYaPassword)

		listLikesTacks = []
	
		listIDLikesTacks = client.users_likes_tracks().tracksIds #List of tracks ID 
	
		for ids in listIDLikesTacks:
			try:
				songName = client.tracks([ids])[0]['title']
				singerName = client.tracks([ids])[0]['artists'][0]['name']
				track_info = []
				track_info.append(songName)
				track_info.append(singerName)
				listLikesTacks.append(track_info)
				print('ID: 'ids)
			except:
				print('Founed error with ID:', ids)
				pass

		return listLikesTacks

	def createPlaylist(self):
		'''Creating playlist in Spotify'''
		body_parametrs = json.dumps({
			'name': 'Yandex Music',
			'description': 'Моя музыка',
			'public': False
			})

		query = 'https://api.spotify.com/v1/users/{}/playlists'.format(self.userID)

		res = requests.post(
			query,
			data=body_parametrs,
			headers={
				'Content-Type':'application/json',
				'Authorization':'Bearer {}'.format(self.userToken)
			})

		res_json = res.json()
		return res_json["id"]

	def searchingSong(self, name_list):
		'''Getting URI track from Spotify'''
		uris = []
		not_founded = []
		nt_founded_count = 0

		for nam in name_list:
			songName = nam[0]
			singerName = ' ' + nam[1]
			
			query = 'https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20'.format(
				songName, 
				singerName
				)
			
			res = requests.get(
				query, 
				headers={
					'Content-Type':'application/json',
					'Authorization':'Bearer {}'.format(self.userToken)
				})

			res_json = res.json()
			try:
				songs = res_json['tracks']['items']
				uri = songs[0]['uri']
				uris.append(uri)
			except:
				not_founded.append(nam)
				nt_founded_count += 1 
				pass

		'''Writing not founded tracks in file'''
		with open('not_founded.txt', 'w', encoding='utf8') as f:
			try:
				f.write(str(nt_founded_count) + '\n')
				for nfel in not_founded:
					f.write(str(nfel) + '\n')
			except:
				print('Запись не удачна')
				pass
	
		return uris

	def sortURI(self, uris):
		'''Split list of URI'''
		processed_uris = []
		limited_list = []
		for uri in uris:
			if len(limited_list) < 75: limited_list.append(uri)# maximum is 100
			else:
				processed_uris.append(limited_list)
				limited_list = []
		processed_uris.append(limited_list)
		return processed_uris 

	def addSongToPlaylist(self):
		'''Add all liked songs from Yandex Music into a new Spotify playlist'''

		#Create a new playlist
		playlistID = self.createPlaylist()

		uri = self.sortURI(self.searchingSong(self.getNameTrack()))

		for uris in uri:
		#Create responses (maximum 100 URIs in one response)
			uri_json = {}
			uri_json['uris'] = uris	

			body_parametrs = json.dumps(uri_json)

			query = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlistID) 
			
			res = requests.post(
				query,
				data=body_parametrs,
				headers={
					'Content-Type':'application/json',
					'Authorization':'Bearer {}'.format(self.userToken)
			})

        res_json = response.json()
        return res_json

if __name__ == '__main__':
	yasp = YaMusicToSpotify()
	yasp.addSongToPlaylist()
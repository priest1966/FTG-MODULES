from .. import loader
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from asyncio import sleep
import threading
@loader.tds
class VoiceToTextMod(loader.Module):
	strings = {"name": "Voice To Text"}
	@loader.owner
	async def vttcmd(self, message):
		reply=await message.get_reply_message()
		media=''
		if reply:
			if reply.media:
				media=reply.media
			else:
				await message.edit('<strong>This is not a voice!</strong>')
				return				
		else:
			await message.edit('<strong>Where is the voice?</strong>')
			return
		await message.edit('<code>I am waiting.</code>')
		try:
			await message.client.send_message('@voicybot', '/l en')
		except YouBlockedUserError:
			await message.edit('<code>Unblock </code> @voicybot')
			return
		await message.edit('<code>I'm waiting.</code>')
		async with message.client.conversation('@voicybot') as silent:
			try:
				await message.edit('<code>I am waiting..</code>')
				response = silent.wait_event(events.NewMessage(incoming=True,
				                                             from_users=330029937))
				if media:
					await message.client.send_file('@voicybot', media)
				else:
					await message.edit('<strong>Error!</strong>')
				response = await response
				await message.edit('<code>I am waiting...</code>')
				await message.delete()
				if '🦄' in f'{response.message}':
					await message.client.send_message('@voicybot', '/silent')
					await sleep(0.8)
					await message.client.send_message(message.to_id,response.message,reply_to=reply.id)
				else:
					await message.client.send_message(message.to_id,response.message,reply_to=reply.id)

			except YouBlockedUserError:
				await message.edit('<code>Unblock </code> @voicybot')
				return

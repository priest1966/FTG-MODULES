# -*- coding: utf-8 -*-

 # Module author: @Fl1yd

 import requests
 from telethon.tl.functions.channels import EditBannedRequest as eb
 from telethon.tl.types import ChatBannedRights as cb

 from .. import utils, loader


 @loader.tds
 class BanWordsMod(loader.Module):
 """Bad words."""
 strings = {'name': 'Ban Words'}

 async def client_ready(self, client, db):
 self.db = db

 async def addbwcmd(self, message):
 """Add a word to the "Bad Words" list. use: .addbw <word>."""
 if not message.is_private:
 chat = await message.get_chat()
 if not chat.admin_rights and not chat.creator:
 return await message.edit("<b>I am not an admin here.</b>")
 else:
 if not chat.admin_rights.delete_messages:
 return await message.edit("<b>I don't have the required rights.</b>")

 words = self.db.get("BanWords", "bws", {})
 args = utils.get_args_raw(message).lower()
 if not arguments:
 return await message.edit("<b>[BanWords]</b> No arguments.")

 chat_id = str(message.chat_id)
 if chat_id not in words:
 words.setdefault(chat_id, [])

 if "stats" not in words:
 words.update({"stats": {chat_id: {"action": "none", "antimat": False, "limit": 5}}})

 if args not in words[chat_id]:
 if ", " in args:
 args = args.split(', ')
 words[chat_id].extend(args)
 self.db.set("BanWords", "bws", words)
 await message.edit(
 f"<b>[BanWords]</b> Words added to chat list - \"<code>{';  '.join(args)}</code>\".")
 else:
 words[chat_id].append(args)
 self.db.set("BanWords", "bws", words)
 await message.edit(f"<b>[BanWords]</b> Added a word to the chat list - \"<code>{args}</code>\".")
 else:
 return await message.edit("<b>[BanWords]</b> This word is already in the list of chat words.")

 async def rmbwcmd(self, message):
 """Remove a word from the "Bad Words" list. Use: .rmbw <word or all/clearall (optional)>.\nall - removes all words from the list.\nclearall - removes all saved module data.""  "
 words = self.db.get("BanWords", "bws", {})
 args = utils.get_args_raw(message)
 if not arguments:
 return await message.edit("<b>[BanWords]</b> No arguments.")
 chat_id = str(message.chat_id)

 try:
 if args == "all":
 words.pop(chat_id)
 words["stats"].pop(chat_id)
 self.db.set("BanWords", "bws", words)
 return await message.edit("<b>[BanWords]</b> All words have been removed from the chat list.")

 if args == "clearall":
 self.db.set("BanWords", "bws", {})
 return await message.edit("<b>[BanWords]</b> All lists from all chats have been removed.")

 words[chat_id].remove(args)
 if len(words[chat_id]) == 0:
 words.pop(chat_id)
 self.db.set("BanWords", "bws", words)
 await message.edit(f"<b>[BanWords]</b> Word removed from chat list - \"<code>{args}</code>\".")
 except(KeyError, ValueError):
 return await message.edit("<b>[BanWords]</b> This word is not in the dictionary of this chat.")

 async def bwscmd(self, message):
 """View the list of "bad words". Use: .bws."""
 words = self.db.get("BanWords", "bws", {})
 chat_id = str(message.chat_id)

 try:
 ls = words[chat_id]
 if len(ls) == 0: raise KeyError
 except KeyError:
 return await message.edit("<b>[BanWords]</b> There is no word list in this chat.")

 word = "".join(f"• <code>{_}</code>\n" for _ in ls)
 await message.edit(f"<b>[BanWords]</b> List of words in this chat:\n\n{word}")

 async def bwstatscmd(self, message):
 """Bad words statistics. Use: .bwstats <clear* (optional)>.\n* - reset chat settings."""
 words = self.db.get("BanWords", "bws", {})
 chat_id = str(message.chat_id)
 args = utils.get_args_raw(message)

 if args == "clear":
 try:
 words["stats"].pop(chat_id)
 words["stats"].update({chat_id: {"antimat": False, "action": "none", "limit": 5}})
 self.db.set("BanWords", "bws", words)
 return await message.edit("<b>[BanWords]</b> Chat settings reset.")
 except KeyError:
 return await message.edit("<b>[BanWords]</b> No user statistics.")

 try:
 w=""
 for _ in words["stats"][chat_id]:
 if _ not in ["action", "antimat", "limit"] and words["stats"][chat_id][_] != 0:
 user = await message.client.get_entity(int(_))
 w += f'• <a href="tg://user?id={int(_)}">{user.first_name}</a>: <code>{words["stats"][chat_id]  [_]}</code>\n'
 return await message.edit(f"<b>[BanWords]</b> Who used special words:\n\n{w}")
 except KeyError:
 return await message.edit("<b>[BanWords]</b> There are no people in this chat who used special words.")

 async def swbwcmd(self, message):
 """Toggle bad words mode. Use: .swbw <mode(antimat/kick/ban/mute/none)>, or .swbw limit <number:int>."""
 if not message.is_private:
 chat = await message.get_chat()
 if chat.admin_rights or chat.creator:
 if chat.admin_rights.delete_messages == False:
 return await message.edit("<b>I don't have the required permissions.</b>")

 else:
 return await message.edit("<b>I'm not the admin here.</b>")
 words = self.db.get("BanWords", "bws", {})
 args = utils.get_args_raw(message)
 chat_id = str(message.chat_id)

 if chat_id not in words:
 words.setdefault(chat_id, [])
 if "stats" not in words:
 words.update({"stats": {chat_id: {"action": "none", "antimat": False, "limit": 5}}})

 if not arguments:
 return await message.edit(f"<b>[BanWords]</b> Chat Settings:\n\n"
 f"<b>Special word limit:</b> {words['stats'][chat_id]['limit']}\n"
 f"<b>Action will be performed when the limit of special words is reached:</b> {words['stats'][chat_id]['action']}\n"
 f"<b>Status \"antimat\" mode:</b> {words['stats'][chat_id]['antimat']}")
 if "limit" in args:
 try:
 limit = int(utils.get_args_raw(message).split(' ', 1)[1])
 words["stats"][chat_id].update({"limit": limit})
 self.db.set("BanWords", "bws", words)
 return await message.edit(
 f"<b>[BanWords]</b> Special word limit has been set to {words['stats'][chat_id]['limit']}.")
 except(IndexError, ValueError):
 return await message.edit(
 f"<b>[BanWords]</b> The limit of special words in this chat is {words['stats'][chat_id]['limit']}\n"
 f"You can set a new one with the command .bwsw limit <number:int>.")

 if args == "antimat":
 if words["stats"][chat_id]["antimat"]:
 words["stats"][chat_id]["antimat"] = False
 self.db.set("BanWords", "bws", words)
 return await message.edit("<b>[BanWords]</b> \"anti-mat\" mode is off.")
 else:
 words["stats"][chat_id]["antimat"] = True
 self.db.set("BanWords", "bws", words)
 return await message.edit("<b>[BanWords]</b> \"anti-mat\" mode is on.")
 else:
 if args == "kick":
 words["stats"][chat_id].update({"action": "kick"})
 elif args == "ban":
 words["stats"][chat_id].update({"action": "ban"})
 elif args == "mute":
 words["stats"][chat_id].update({"action": "mute"})
 elif args == "none":
 words["stats"][chat_id].update({"action": "none"})
 else:
 return await message.edit(
 f"<b>[BanWords]</b> This mode is not in the list. Yes: kick/ban/mute/none.")
 self.db.set("BanWords", "bws", words)
 return await message.edit(
 f"<b>[BanWords]</b> Now, when the limit of special words is reached, the action will be performed: {words['stats'][chat_id]['action']}.")

 async def watcher(self, message):
 """Update 19.03: Fix shitcode."""
 try:
 if message.sender_id == (await message.client.get_me()).id: return
 words = self.db.get("BanWords", "bws", {})
 chat_id = str(message.chat_id)
 user_id = str(message.sender_id)
 user = await message.client.get_entity(int(user_id))

 if chat_id not in str(words): return
 action = words["stats"][chat_id]["action"]
 if words["stats"][chat_id]["antimat"] == True:
 r = requests.get("https://api.fl1yd.ml/badwords")
 ls = r.text.split(', ')
 else:
 ls = words[chat_id]

 for_in ls:
 if _.lower() in message.raw_text.lower().split():
 if user_id not in words["stats"][chat_id]:
 words["stats"][chat_id].setdefault(user_id, 0)

 count = words["stats"][chat_id][user_id]
 words["stats"][chat_id].update({user_id: count + 1})
 self.db.set("BanWords", "bws", words)

 if count == words["stats"][chat_id]["limit"]:
 try:
 if action == "kick":
 await message.client.kick_participant(int(chat_id), int(user_id))
 elif action == "ban":
 await message.client(eb(int(chat_id), user_id, cb(until_date=None, view_messages=True)))
 elif action == "mute":
 await message.client(eb(int(chat_id), user.id, cb(until_date=True, send_messages=True)))
 words["stats"][chat_id].pop(user_id)
 self.db.set("BanWords", "bws", words)
 await message.respond(
 f"<b>[BanWords]</b> {user.first_name} reached the limit ({words['stats'][chat_id]['limit']}) of a special word, and was restricted from chatting.")
 except:
 pass
 await message.client.delete_messages(message.chat_id, message.id)
 except:
 pass
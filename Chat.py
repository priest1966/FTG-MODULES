# -*- coding: utf-8 -*-

# Module author: @ftgmodulesbyfl1yd, @dekftgmodules, @memeframe

import asyncio
import io
from asyncio import sleep
from os import remove

from telethon import errors, functions
from telethon.errors import (BotGroupsBlockedError, ChannelPrivateError,
                             ChatAdminRequiredError, ChatWriteForbiddenError,
                             InputUserDeactivatedError, MessageTooLongError,
                             UserAlreadyParticipantError, UserBlockedError,
                             UserIdInvalidError, UserKickedError,
                             UserNotMutualContactError,
                             UserPrivacyRestrictedError, YouBlockedUserError)
from telethon.tl.functions.channels import (InviteToChannelRequest,
                                            LeaveChannelRequest)
from telethon.tl.functions.messages import (AddChatUserRequest,
                                            GetCommonChatsRequest)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (ChannelParticipantCreator,
                               ChannelParticipantsAdmins,
                               ChannelParticipantsBots)

from .. import loader, utils


@loader.tds
class ChatMod(loader.Module):
    """Chat module"""
    strings = {'name': 'Chat Tools'}

    async def client_ready(self, client, db):
        self.db = db

    async def useridcmd(self, message):
        """The .userid <@ or replay> command shows the ID of the selected user."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        try:
            if args:
                user = await message.client.get_entity(
                    args if not args.isdigit() else int(args))
            else:
                user = await message.client.get_entity(reply.sender_id)
        except ValueError:
            user = await message.client.get_entity(message.sender_id)

        await message.edit(f"<b>Name:</b> <code>{user.first_name}</code>\n"
                           f"<b>ID:</b> <code>{user.id}</code>")

    async def chatidcmd(self, message):
        """The .chatid command shows the chat ID."""
        if message.is_private:
            return await message.edit("<b>This is not a chat!</b>")
        args = utils.get_args_raw(message)
        to_chat = None

        try:
            if args:
                to_chat = args if not args.isdigit() else int(args)
            else:
                to_chat = message.chat_id

        except ValueError:
            to_chat = message.chat_id

        chat = await message.client.get_entity(to_chat)

        await message.edit(f"<b>Name:</b> <code>{chat.title}</code>\n"
                           f"<b>ID</b>: <code>{chat.id}</code>")

    async def invitecmd(self, message):
        """Use .invite <@ or replay> to add the user to the chat."""
        if message.is_private:
            return await message.edit("<b>This is not a chat!</b>")

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if not args and not reply:
            return await message.edit("<b>No arguments or reply.</b>")

        try:
            if args:
                user = args if not args.isdigit() else int(args)
            else:
                user = reply.sender_id

            user = await message.client.get_entity(user)

            if not message.is_channel and message.is_group:
                await message.client(AddChatUserRequest(chat_id=message.chat_id,
                                                        user_id=user.id,
                                                        fwd_limit=1000000))
            else:
                await message.client(
                    InviteToChannelRequest(channel=message.chat_id,
                                           users=[user.id]))
            return await message.edit("<b>User invited successfully!</b>")

        except ValueError:
            m = "<b>Invalid @ or ID.</b>"
        except UserIdInvalidError:
            m = "<b>Invalid @ or ID.</b>"
        except UserPrivacyRestrictedError:
            m = "<b>The user's privacy settings not allow you to invite him.</b>"
        except UserNotMutualContactError:
            m = "<b>The user's privacy settings not allow you to invite him.</b>"
        except ChatAdminRequiredError:
            m = "<b>I do not have rights.</b>"
        except ChatWriteForbiddenError:
            m = "<b>I do not have rights.</b>"
        except ChannelPrivateError:
            m = "<b>I do not have rights.</b>"
        except UserKickedError:
            m = "<b>The user was kicked from the chat, contact the administrators.</b>"
        except BotGroupsBlockedError:
            m = "<b>Bot blocked in chat, contact administrators.</b>"
        except UserBlockedError:
            m = "<b>User blocked from chat, contact administrators.</b>"
        except InputUserDeactivatedError:
            m = "<b>User account deleted.</b>"
        except UserAlreadyParticipantError:
            m = "<b>The user is already in the group.</b>"
        except YouBlockedUserError:
            m = "<b>You have blocked this user.</b>"
        return await message.reply(m)

    async def leavecmd(self, message):
        """Use the .leave command to kick yourself out of the chat."""
        args = utils.get_args_raw(message)
        if message.is_private:
            return await message.edit("<b>This is not a chat!</b>")
        if args:
            await message.edit(f"<b>Before communication.\nCause: {args}</b>")
        else:
            await message.edit("<b>Before communication.</b>")
        await message.client(LeaveChannelRequest(message.chat_id))

    async def userscmd(self, message):
        """Command .users <name>;  nothing displays a list of all users in the chat."""
        if message.is_private:
            return await message.edit("<b>This is not a chat!</b>")
        await message.edit("<b>We believe...</b>")
        args = utils.get_args_raw(message)
        info = await message.client.get_entity(message.chat_id)
        title = info.title or "this chat"

        if args:
            users = await message.client.get_participants(message.chat_id,
                                                          search=f"{args}")
            mentions = f'<b>In the chat "{title}" found {len(users)} users with the name {args}:</b> \n'

        else:
            users = await message.client.get_participants(message.chat_id)
            mentions = f"<b>Users in \"{title}\": {len(users)}</b> \n"
        for user in users:
            if user.deleted:
                mentions += f"\n• Remote account <b>|</b> <code>{user.id}</code>"

            else:
                mentions += f"\n• <a href =\"tg://user?id={user.id}\">{user.first_name}</a> | <code>{user.id}</code>"
        try:
            await message.edit(mentions)
        except MessageTooLongError:
            await message.edit(
                "<b>Damn, too big chat.  Loading list of Users in file...</b>")
            with open("userslist.md", "w+") as file:
                file.write(mentions)
            await message.client.send_file(message.chat_id,
                                           "userslist.md",
                                           caption="<b>Users in {}:</b>".format(
                                                   title),
                                           reply_to=message.id)
            remove("userslist.md")
            await message.delete()

    async def adminscmd(self, message):
        """The .admins command shows a list of all admins in the chat."""
        if message.is_private:
            return await message.edit("<b>This is not a chat!</b>")
        await message.edit("<b>We believe...</b>")
        info = await message.client.get_entity(message.chat_id)
        title = info.title or "this chat"

        admins = await message.client.get_participants(message.chat_id,
                                                       filter=ChannelParticipantsAdmins)
        mentions = f"<b>Admins in \"{title}\": {len(admins)}</b>\n"

        for user in admins:
            admin = admins[admins.index(
                (await message.client.get_entity(user.id)))].participant
            if admin:
                rank = admin.rank or "admin"

            else:
                rank = "creator" if type(
                    admin) == ChannelParticipantCreator else "admin"
            if user.deleted:
                mentions += f"\n• Remote account <b>|</b> <code>{user.id}</code>"

            else:
                mentions += f"\n• <a href=\"tg://user?id={user.id}\">{user.first_name}</a> | {rank} | <code>{user.id}</code>"
        try:
            await message.edit(mentions)
        except MessageTooLongError:
            await message.edit(
                "Damn, too many admins here.  Loading a list of admins into a file...")
            with open("adminlist.md", "w+") as file:
                file.write(mentions)
            await message.client.send_file(message.chat_id,
                                           "adminlist.md",
                                           caption="<b>Admins in \"{}\":<b>".format(
                                                   title),
                                           reply_to=message.id)
            remove("adminlist.md")
            await message.delete()

    async def botscmd(self, message):
        """The .bots command shows a list of all bots in the chat."""
        if message.is_private:
            return await message.edit("<b>This is not a chat!</b>")
        await message.edit("<b>We believe...</b>")

        info = await message.client.get_entity(message.chat_id)
        title = info.title or "this chat"

        bots = await message.client.get_participants(message.to_id,
                                                     filter=ChannelParticipantsBots)
        mentions = f"<b>Bots in \"{title}\": {len(bots)}</b>\n"

        for user in bots:
            if not user.deleted:
                mentions += f"\n• <a href=\"tg://user?id={user.id}\">{user.first_name}</a> | <code>{user.id}</code>"
            else:
                mentions += f"\n• Remote bot <b>|</b> <code>{user.id}</code> "

        try:
            await message.edit(mentions, parse_mode="html")
        except MessageTooLongError:
            await message.edit("Damn, too many bots here.  Loading"
                                "list of bots to file...")
            with open("botlist.md", "w+") as file:
                file.write(mentions)
            await message.client.send_file(message.chat_id,
                                           "botlist.md",
                                           caption="<b>Bots in \"{}\":</b>".format(
                                                   title),
                                           reply_to=message.id)
            remove("botlist.md")
            await message.delete()

    async def commoncmd(self, message):
        """Use .common <@ or replay> to find out common chats with user. """
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            return await message.edit('<b>No arguments or reply.</b>')
        await message.edit('<b>We believe...</b>')
        try:
            if args:
                if args.isnumeric():
                    user = int(args)
                    user = await message.client.get_entity(user)
                else:
                    user = await message.client.get_entity(args)
            else:
                user = await utils.get_user(reply)
        except ValueError:
            return await message.edit('<b>Failed to find user.</b>')
        msg = f'<b>General chats with {user.first_name}:</b>\n'
        user = await message.client(GetFullUserRequest(user.id))
        comm = await message.client(
            GetCommonChatsRequest(user_id=user.user.id, max_id=0, limit=100))
        count = 0
        m = ''
        for chat in comm.chats:
            m += f'\n• <a href="tg://resolve?domain={chat.username}">{chat.title}</a> <b>|</b> <code>{chat.id}</code> '
            count += 1
        msg = f'<b>General chats with {user.user.first_name}: {count}</b>\n'
        await message.edit(f'{msg} {m}')

    async def chatdumpcmd(self, message):
        """.chatdump <n> <m> <s>
                Chat user dump
                 <n> - Get only users with open numbers
                 <m> - Send dump to favorites
                 <s> - Silent dump
        """
        if not message.chat:
            await message.edit("<b>This is not a chat</b>")
            return
        chat = message.chat
        num = False
        silent = False
        tome = False
        if utils.get_args_raw(message):
            a = utils.get_args_raw(message)
            if "n" in a:
                num = True
            if "s" in a:
                silent = True
            if "m" in a:
                tome = True
        if not silent:
            await message.edit("🖤Dumping chat...🖤")
        else:
            await message.delete()
        f = io.BytesIO()
        f.name = f'Dump by {chat.id}.csv'
        f.write("FNAME;LNAME;USER;ID;NUMBER\n".encode())
        me = await message.client.get_me()
        for i in await message.client.get_participants(message.to_id):
            if i.id == me.id:
                continue
            if num and i.phone or not num:
                f.write(
                    f"{str(i.first_name)};{str(i.last_name)};{str(i.username)};{str(i.id)};{str(i.phone)}\n".encode())
        f.seek(0)
        if tome:
            await message.client.send_file('me', f,
                                           caption="Chat dump " + str(chat.id))
        else:
            await message.client.send_file(message.to_id, f, caption="Dump"
                                                                      "chat"
                                                                     + str(
                                                                         chat.id))
        if not silent:
            if tome:
                if num:
                    await message.edit("🖤Chat users dump saved in "
                                        "chosen ones!🖤")
                else:
                    await message.edit("🖤Dump chat users with open "
                                        "numbers saved in favorites!🖤")
            else:
                await message.delete()
        f.close()

    async def adduserscmd(self, event):
        """Add members"""
        if len(event.text.split()) == 2:
            idschannelgroup = event.text.split(" ", maxsplit=1)[1]
            user = [i async for i in
                    event.client.iter_participants(event.to_id.channel_id)]
            await event.edit(
                f"<b>{len(user)} users will be invited from chat {event.to_id.channel_id} to chat/channel {idschannelgroup}</b>")
            for u in user:
                try:
                    try:
                        if not u.bot:
                            await event.client(
                                functions.channels.InviteToChannelRequest(
                                    idschannelgroup, [u.id]))
                            await asyncio.sleep(1)
                    except:
                        pass
                except errors.FloodWaitError as e:
                    print('Flood for', e.seconds)
        else:
            await event.edit(f"<b>Where will we invite?</b>")

    async def reportcmd(self, message):
        """Репорт пользователя за спам."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args:
            user = await message.client.get_entity(
                args if not args.isnumeric() else int(args))
        if reply:
            user = await message.client.get_entity(reply.sender_id)
        else:
            return await message.edit("<b>Who should I report?</b>")

        await message.client(functions.messages.ReportSpamRequest(peer=user.id))
        await message.edit("<b>You received a spam report!</b>")
        await sleep(1)
        await message.delete()

    async def echocmd(self, message):
        """Activate/Deactivate Echo."""
        echos = self.db.get("Echo", "chats", [])
        chatid = str(message.chat_id)

        if chatid not in echos:
            echos.append(chatid)
            self.db.set("Echo", "chats", echos)
            return await message.edit(
                "<b>[Echo Mode]</b> Activated in this chat!")

        echos.remove(chatid)
        self.db.set("Echo", "chats", echos)
        return await message.edit(
            "<b>[Echo Mode]</b> Deactivated in this chat!")

    async def watcher(self, message):
        echos = self.db.get("Echo", "chats", [])
        chatid = str(message.chat_id)

        if chatid not in str(echos):
            return
        if message.sender_id == (await message.client.get_me()).id:
            return

        await message.client.send_message(int(chatid), message,
                                          reply_to=await message.get_reply_message() or message)

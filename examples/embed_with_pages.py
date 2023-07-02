# ©️ The NextGuild Project 2023-present
# If support is needed, you can join the support server (guilded.gg/nextguild) or raise an issue.
# NOTICE: This example requires a external library, that is not endorsed or supported by The NextGuild Project.
# CODE LEVEL // ADVANCED - This is not recommended for beginners, as it requires a lot of knowledge about the NextGuild API and Python in general.
# You can install the appropriate dependencies with the following commands in the terminal:
# pip install nextguild
# pip install sqlite3
# pip install websockets
# pip install requests

from nextguild import *
import sqlite3

bot = Client('INSERT YOUR TOKEN HERE')
events = Events(bot)

#these are all of the emotes we'll be using as reactions. We'll be using a dict, since it's faster and easier to use than an array.
emotes = {'arrow_left': 90002097, 'arrow_right': 90002093}

#Setting up the database
connection = sqlite3.connect('database.sqlite3') # This is the connection, which we will use to commit changes to the database, ensuring that no data gets lost even if the bot goes offline.
cursor = connection.cursor() # This is the cursor, which we will use to execute SQL commands.
cursor.execute('CREATE TABLE IF NOT EXISTS helpembeds (id INTEGER, page INTEGER DEFAULT 1, owner STRING)') #we create a table containing information about each help message, if it doesn't exist already. We will update this information later.

#We will now create a function that will return the help embed for a given page, so we don't need to repeat the same code over and over again.
totalpages = 3 #This is the total amount of pages in the help embed. You can change this to whatever you want, but make sure to update the help_embed function accordingly. You don't necessarily need to do this, but it will clear any confusion.
def help_embed(page):
    embed = Embed(title='Help', description='This is a help embed used in an example by NextGuild!', footer=f'You are on page {page}/{totalpages}')
    if page == 1:
        embed.add_field(name='!help', value='Shows this help embed.') # You can obviously add more fields, but for the sake of simplicity, we will only add one field per page.
    if page == 2:
        embed.add_field(name='!command', value='This is another command')
    if page == 3:
        embed.add_field(name='!command2', value='This is a third command')
    return embed #returning the embed to the function caller.

@events.on_ready
async def ready(bot):
    print('Bot is ready!')
    global bot_id
    bot_id = bot.user_id
    
    
    
#the next step is to create a function that will send the help embed to the channel, and add the reactions to it.
@events.on_message
async def help(message):
    if message.created_by == bot_id: #we check if the message was sent by the bot, so we don't get an infinite loop.
        return

    if message.content == '!help':
        help_embed_id = Data(bot.send_message(channel_id=message.channel_id, embed=help_embed(1), reply_message_ids=[message.id])).id #sending the help embed, and storing the message id to later insert it in the database. We use Data since it simplifies the process of getting the message id.
        cursor.execute('INSERT INTO helpembeds (id, owner) VALUES (?, ?)', (help_embed_id, message.created_by)) #we insert the message id and the author id into the database, so we can later check if the user is allowed to edit the message. Page is not needed, as we set it to 1 by default.
        connection.commit() #committing the changes to the database, so we can access them later.
        bot.create_message_reaction(message.channel_id, help_embed_id, emotes['arrow_left']) #adding the left arrow reaction to the message.
        bot.create_message_reaction(message.channel_id, help_embed_id, emotes['arrow_right']) #adding the right arrow reaction to the message.


#now we'll listen for the reactions, and edit the help embed accordingly. We'll also check if the user is allowed to edit the message and if the reaction is valid.
@events.on_channel_message_reaction_create
async def help_reaction(reaction):
    if reaction.created_by == bot_id: #we check if the reaction was sent by the bot, so we don't get an infinite loop.
        return

    cursor.execute('SELECT id, page, owner FROM helpembeds WHERE id=?', (reaction.message_id,)) #we select the row containing the message id.
    result = cursor.fetchone() #we all of the data for that embed and store it in a variable.
    if result:
        id, page, owner = result #we unpack the data into variables, so we can use them easier later
        if reaction.created_by == owner: #we check if the user is allowed to edit the message.
            if reaction.id == emotes['arrow_left'] and page > 1: #we check if the reaction is the left arrow, and if the page is greater than 1.
                page -= 1 #we decrease the page by 1.
                bot.edit_message(reaction.channel_id, reaction.message_id, embed=help_embed(page)) #we edit the message with the new page.
                cursor.execute('UPDATE helpembeds SET page=? WHERE id=?', (page, id)) #we update the page in the database.
                connection.commit() #committing the changes to the database, so we can access them later.
            elif reaction.id == emotes['arrow_right'] and page < totalpages: #we check if the reaction is the right arrow, and if the page is less than the total amount of pages.
                page += 1 #we increase the page by 1.
                bot.edit_message(reaction.channel_id, reaction.message_id, embed=help_embed(page)) #we edit the message with the new page.
                cursor.execute('UPDATE helpembeds SET page=? WHERE id=?', (page, id)) #we update the page in the database.
                connection.commit() #committing the changes to the database, so we can access them later.
        bot.delete_message_reaction(reaction.channel_id, reaction.message_id, reaction.id, reaction.created_by) #we delete the reaction, so the message doesn't get spammed with reactions.
        

events.run()
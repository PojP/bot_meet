from email import message
from re import T
from aiogram import Dispatcher, types
from init_bot import bot
from keyboards import keyboard_cl_registration
from keyboards import none_kb, keyboard_cl_edit_interests, keyboard_cl_settings, keyboard_cl_settings_age, keyboard_cl_settings_gender
from keyboards import keyboard_cl_start
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from backend import check_user,update,check_user_search,del_user_from_search


#REGISTRATION
#funcs to import 
from .registration import start_register
from .registration import get_gender
from .registration import get_age
from .registration import get_interests
#objects
from .registration import gender
from .registration import interests
from .registration import ClientRegistrationState, EditState

#SEARCH
#funcs to import
from .search import search
from .search import chatting
from .search import stop
from .search import next_user
from .search import share_contact
from .search import dont_share_contact
#objects to import
from .search import ClientSearchState
#AUTH
from .auth import IsAuthorized

#Basic func
async def start_bot(message : types.Message, state : FSMContext):
    user_id=message.from_user.id
    await bot.send_message(user_id, "Hi! It's a bot for meeting")
    if check_user(user_id):
        await bot.send_message(user_id,
        "Hi! This is a dating bot. You find a user by your interests\n"+
        "Current Interest options:\n"+
        "Flood\n"+
        "Investment\n"+
        "Meetings\n"+
        "\n"
        "To start searching for interlocutors, enter /search\n"+
        "To change your personal information, enter /settings\n"+
        "To change interests, enter /edit_interests",
        reply_markup=keyboard_cl_start)
        await IsAuthorized.is_auth.set()
    else:
        await bot.send_message(user_id, "To use the bot, you need to be registered. To do this, simply enter /registration",reply_markup=keyboard_cl_registration)
async def edit_interests(message : types.Message):
    await bot.send_message(message.from_user.id, "Here you can change the interests.\nTo cancel, write 'cancel'", reply_markup=keyboard_cl_edit_interests)
    await EditState.interests.set()
async def get_edited_interests(message : types.Message):
    try:
        update(message.from_user.id, message.text.split(" ")[0].lower(), "interest")
    except:
        await bot.send_message(message.from_user.id,"Interest not added :(")
    finally:
        await IsAuthorized.is_auth.set()
    await bot.send_message(message.from_user.id,"Interest added :)", reply_markup=keyboard_cl_start)
async def settings(message : types.Message):
    await bot.send_message(message.from_user.id, "Here you can change the gender or age.\nTo cancel, write 'cancel'", reply_markup=keyboard_cl_settings)
    await EditState.settings.set()
async def get_settings_gender(message : types.Message):
    gender=""
    if message.text.lower() in ["male 👨", "male"]:
        gender="male"
    else:
        gender="female"
    try:
        update(message.from_user.id, gender, "gender")
    except:
        await bot.send_message(message.from_user.id,"Gender not added :(")
    finally:
        await IsAuthorized.is_auth.set()
    await bot.send_message(message.from_user.id,"Gender added successfully!",reply_markup=keyboard_cl_start)
async def get_settings_age(message: types.Message):
    if int(message.text) <99 and int(message.text) >0:
        try:
            update(message.from_user.id, message.text, "age")
        except:
            await bot.send_message(message.from_user.id,"Age not added :(")
        finally:
            await IsAuthorized.is_auth.set()
        await bot.send_message(message.from_user.id,"Age added successfully",reply_markup=keyboard_cl_start)
async def get_settings(message: types.Message):
    if message.text.lower() in ["age", "age 📈"]:
        await bot.send_message(message.from_user.id, "Enter your age.\nTo cancel, write 'cancel'", reply_markup=keyboard_cl_settings_age)
        await EditState.age.set()
    else:
        await bot.send_message(message.from_user.id, "Enter your gender.\nTo cancel, write 'cancel'", reply_markup=keyboard_cl_settings_gender)
        await EditState.gender.set()

async def cancel(message : types.Message, state : FSMContext):
    if await state.get_state()==ClientSearchState.Active.state:
        await state.set_state(IsAuthorized.is_auth)
        if check_user_search(message.from_user.id):
            del_user_from_search(message.from_user.id)
        await bot.send_message(message.from_user.id, "You cancelled searching", reply_markup=keyboard_cl_start)
    
    elif await state.get_state()==EditState.age.state:
        await bot.send_message(message.from_user.id, "You cancelled editing age", reply_markup=keyboard_cl_settings)
        await state.set_state(EditState.settings)
    
    elif await state.get_state()==EditState.settings.state:
        await bot.send_message(message.from_user.id, "You exited from settings", reply_markup=keyboard_cl_start)
        await state.set_state(IsAuthorized.is_auth)
    
    elif await state.get_state()==EditState.gender.state:
        await bot.send_message(message.from_user.id, "You cancelled editing gender", reply_markup=keyboard_cl_settings)
        await state.set_state(EditState.settings)

    elif await state.get_state()==EditState.interests.state:
        await bot.send_message(message.from_user.id, "You cancelled editing interests", reply_markup=keyboard_cl_start)
        await state.set_state(IsAuthorized.is_auth)

def register_handlers(dp : Dispatcher):
    #basic commands
    dp.register_message_handler(cancel, lambda msg: msg.text.lower() in ["cancel","/cancel", "cancel 🚫"],state="*")
    dp.register_message_handler(start_bot, commands=["start", "help"],state=[IsAuthorized.is_auth, None])
    dp.register_message_handler(edit_interests,lambda msg: msg.text.lower() in ["interests 💡","interests","/edit_interests"],state=IsAuthorized.is_auth)
    dp.register_message_handler(settings,lambda msg: msg.text.lower() in ["settings ⚙️","settings", "/settings"],state=IsAuthorized.is_auth)
    #edit command
    dp.register_message_handler(get_edited_interests, lambda msg: msg.text.lower() in interests, state = EditState.interests)
    dp.register_message_handler(get_settings, lambda msg: msg.text.lower() in ["age", "age 📈", "gender","gender 👤"], state= EditState.settings)
    dp.register_message_handler(get_settings_age, lambda msg: msg.text.isdigit(), state=EditState.age)
    dp.register_message_handler(get_settings_gender, lambda msg: msg.text.lower() in gender,state=EditState.gender)
    #registrate commands
    dp.register_message_handler(start_register, lambda msg: msg.text.lower() in ["/registration", "registration"],state=None)
    dp.register_message_handler(get_gender, lambda msg: msg.text.lower() in gender, state=ClientRegistrationState.gender)
    dp.register_message_handler(get_age, lambda msg: msg.text.isdigit(), state=ClientRegistrationState.age)
    dp.register_message_handler(get_interests, lambda msg: msg.text.lower() in interests, state=ClientRegistrationState.interests)
    #search commandsSearch🔎
    dp.register_message_handler(search,lambda msg: msg.text.lower() in ["search 🔎","search", "/search"], state=IsAuthorized.is_auth)
    dp.register_message_handler(stop, lambda msg: msg.text.lower() in ["/stop","stop ❌"],state=ClientSearchState.Chating)
    dp.register_message_handler(next_user, lambda msg: msg.text.lower() in ["/next", "next ➡️"],state=ClientSearchState.Chating)
    dp.register_message_handler(chatting, lambda msg: msg.text.lower() not in ["/stop","/next", "next ➡️","stop ❌"], state=ClientSearchState.Chating, content_types=types.message.ContentType.TEXT)
    dp.register_message_handler(chatting,lambda msg: msg.text is None, state=ClientSearchState.Chating, content_types=types.message.ContentType.ANY)
    dp.register_callback_query_handler(share_contact,lambda callback: callback.data=="share_contact", state=ClientSearchState.Sharing)
    dp.register_callback_query_handler(dont_share_contact,lambda callback: callback.data=="dont_share_contact", state=ClientSearchState.Sharing)
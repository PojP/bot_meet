from aiogram import types
from init_bot import bot
from keyboards import keyboard_cl_interests
from keyboards import keyboard_cl_gender
from keyboards import none_kb
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from backend import add_user, check_user
from .auth import IsAuthorized


interests =["flood", "investments", "meetings","flood 👋", "investments 💰", "meetings ❤️"]
gender    =["male 👨", "female 👩","male", "female"]

#Registration
class ClientRegistrationState(StatesGroup):
    gender = State()
    age = State()
    interests = State()
class EditState(StatesGroup):
    gender=State()
    age=State()
    interests=State()
    settings=State()

async def start_register(message : types.Message,state : FSMContext):
    if state==IsAuthorized.is_auth:
        await bot.send_message(message.from_user.id, "You already registered",reply_markup=none_kb)
    else:
        await bot.send_message(message.from_user.id, "Let's fill out the information about you\nWho are you by gender?", reply_markup=keyboard_cl_gender)
        await ClientRegistrationState.gender.set()
async def get_gender(message : types.Message, state : FSMContext):
    answer = message.text.lower().split(" ")[0]
    if answer in gender:
        async with state.proxy() as data:
            data["gender"] = answer
        await bot.send_message(message.from_user.id, "Whats your age? Enter number from 1 to 99", reply_markup=none_kb) 
        await ClientRegistrationState.next()
async def get_age(message : types.Message, state : FSMContext):
    answer = message.text
    answer=int(answer)
    if answer>0 and answer<100:
        async with state.proxy() as data:
            data["age"] = answer
        await bot.send_message(message.from_user.id, "Now, enter your interests", reply_markup=keyboard_cl_interests) 
        await ClientRegistrationState.next()
    else:
        await bot.send_message(message.from_user.id, "It's not correct! Please retry")
async def get_interests(message : types.Message, state : FSMContext):
    data = await state.get_data()
    a=(message.from_user.id,data.get("age"),message.text.lower().split(" ")[0],data.get("gender"))
    add_user(a)
    await bot.send_message(message.from_user.id, "You successfully registered\nNow, enter /start", reply_markup=none_kb) 
    await state.reset_state()
    await IsAuthorized.is_auth.set()




    
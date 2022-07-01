from aiogram import types
from handlers.auth import IsAuthorized
from init_bot import dp, bot
from keyboards import keyboard_cl_start, share_button, keyboard_cl_chatting, keyboard_cl_settings_age
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from asyncio import sleep
from random import randint
from backend import get_user, del_user_from_search, add_user_to_search, get_users,check_user_search


class ClientSearchState(StatesGroup):
    Active = State()
    Chating = State()
    Sharing = State()


###CLIENT FUNCS
async def search(message : types.Message, state : FSMContext):
    my_id=message.from_user.id
    await bot.send_message(my_id, "Searching for interlocutors...", reply_markup=keyboard_cl_settings_age)
    await state.reset_state()
    await ClientSearchState.Active.set()
    data=get_user(my_id)[2]
    arr=[int]
    arr = get_users(data)
    ln=len(arr)
    while ln>0:
        uid=arr.pop(randint(0,ln-1))[0]
        if await set_chat(uid, my_id):
            break
        else:
            arr = get_users(data)
            ln=len(arr)
    if ln==0:
        a=(my_id,data)
        add_user_to_search(a)

                


async def chatting(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        fstate=dp.current_state(chat=data["uid"],user=data["uid"])
        if message.content_type!="command":
            f=message.reply_to_message
            g=None
            async with fstate.proxy() as fdata:
                if f is None:
                    g=await message.copy_to(data["uid"])

                else:

                    if f.from_user.is_bot is False:
                        index_msg=data["messages"].index(f.message_id)
                        repl_msg=None
                        try:
                            repl_msg=fdata["messages"][index_msg].message_id
                        except AttributeError:
                            repl_msg=fdata["messages"][index_msg]
                        g=  await message.copy_to(data["uid"],reply_to_message_id=repl_msg)
                    else:
                        index_msg=data["messages"].index(f.message_id)
                        g=  await message.copy_to(data["uid"],reply_to_message_id=fdata["messages"][index_msg])

                if g != None:
                    data["messages"].append(message.message_id)
                    if (m_id:=g.message_id) is not None:
                        fdata["messages"].append(m_id)
                    else:
                        fdata["messages"].append(g)


                
        
async def stop(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        uid= data["uid"]
        fstate=dp.current_state(user=uid, chat=uid)
        stop_mess="Communication stopped by interlocutor. Send /search to search new interlocutors or /start to open main menu\n\nIf you want to share you contacts press on button"
        await fstate.set_state(ClientSearchState.Sharing.state)
        await state.set_state(ClientSearchState.Sharing.state)
        await bot.send_message(uid, stop_mess, reply_markup=share_button)
        await bot.send_message(message.from_user.id, "Communication stopped by you. Send /search to search new interlocutors or /start to open main menu\n\nIf you want to share you contacts press on button", reply_markup=share_button)
async def next_user(message : types.Message, state : FSMContext):
    await stop(message, state)
    while await state.get_state() == ClientSearchState.Sharing.state:
        await sleep(1)
    await search(message, state)



###BUTTONS###
async def share_contact(callback : types.CallbackQuery, state : FSMContext):
    async with state.proxy() as data:
        uid=data["uid"]
        fg_state=dp.current_state(user=uid, chat=uid)
        await bot.send_message(data["uid"], f"User shows own contact data!\nUsername is: @{callback.from_user.username}\nFull name is: {callback.from_user.full_name}", reply_markup=keyboard_cl_start)
        await callback.message.answer("Contact details are displayed", reply_markup=keyboard_cl_start)
        await fg_state.reset_state()
        await state.reset_state()
        await fg_state.set_state(IsAuthorized.is_auth)
        await state.set_state(IsAuthorized.is_auth)
        await callback.answer()

async def dont_share_contact(callback : types.CallbackQuery, state : FSMContext):
    async with state.proxy() as data:
        uid=data["uid"]
        fg_state=dp.current_state(user=uid, chat=uid)
        await bot.send_message(data["uid"], f"The interlocutor decided not to show his contacts :(", reply_markup=keyboard_cl_start)
        await callback.message.answer("Contact details are hidden", reply_markup=keyboard_cl_start)
        await fg_state.reset_state()
        await state.reset_state()
        await fg_state.set_state(IsAuthorized.is_auth)
        await state.set_state(IsAuthorized.is_auth)
        await callback.answer()

###BACKEND FUNCS###
async def timer_to_close(fid: int, sid: int):
    fstate = dp.current_state(user=fid,chat=fid)
    sstate = dp.current_state(user=sid,chat=sid)

    is_chatting=True
    await sleep(300)
    async with fstate.proxy() as data:
        if data["uid"] != sid:
            is_chatting=False
    if await fstate.get_state() == ClientSearchState.Chating.state and is_chatting:
        await bot.send_message(fid, "BOT MESSAGE: You have 5 minutes to chat")
        await bot.send_message(sid, "BOT MESSAGE: You have 5 minutes to chat")
    await sleep(240)
    async with fstate.proxy() as data:
        if data["uid"] != sid:
            is_chatting=False
    if await fstate.get_state() == ClientSearchState.Chating.state and is_chatting:
        await bot.send_message(fid, "BOT MESSAGE: You have 1 minutes to chat!")
        await bot.send_message(sid, "BOT MESSAGE: You have 1 minutes to chat!")
    await sleep(60)
    async with fstate.proxy() as data:
        if data["uid"] != sid:
            is_chatting=False
    if await fstate.get_state() == ClientSearchState.Chating.state and is_chatting:
        stop_mess="Communication stopped. 10 minutes are passed⏱\n Send /search to search new interlocutors or /start to open main menu\n\nIf you want to share you contacts press on button"
        await fstate.set_state(ClientSearchState.Sharing.state)
        await sstate.set_state(ClientSearchState.Sharing.state)
        await bot.send_message(fid, stop_mess, reply_markup=share_button)
        await bot.send_message(sid, stop_mess, reply_markup=share_button)





async def set_chat(fid: int, sid : int):
    fstate = dp.current_state(chat=fid, user=fid)
    sstate = dp.current_state(chat=sid, user=sid)
    if await fstate.get_state() == await sstate.get_state():
        await fstate.set_state(ClientSearchState.Chating)
        await sstate.set_state(ClientSearchState.Chating)

        del_user_from_search(sid)
        del_user_from_search(fid)
        f_mess="The interlocutor was found!!! You have 10 minutes to chat\n You can write to him\n\nTo stop communication send /next or /stop"
        fid_msg=await bot.send_message(fid, f_mess,reply_markup=keyboard_cl_chatting)
        sid_msg=await bot.send_message(sid, f_mess,reply_markup=keyboard_cl_chatting)


        async with fstate.proxy() as data:
            data["repl_msg"]=0
            data["my_id"]=sid_msg.message_id+1
            data["uid"] = sid
            data["messages"]=[types.Message]
        async with sstate.proxy() as data:
            data["repl_msg"]=0
            data["my_id"]=sid_msg.message_id+1
            data["uid"] = fid
            data["messages"]=[types.Message]

        await timer_to_close(fid, sid)
        return True
    return False

from telethon import Button

def split(arr, size):
     arrs = []
     while len(arr) > size:
         pice = arr[:size]
         arrs.append(pice)
         arr   = arr[size:]
     arrs.append(arr)
     return arrs


def get_buttons(my_list):
    buttons = []
    for item in my_list:
        # print(item)
        buttons.append(Button.inline(item, item))
    return buttons
    

async def downloadpic(client, event): 
    # downloads the current profile photo into a file
    path = await client.download_profile_photo(event.sender_id)
    print(f"downloaded profile pic: {path}")



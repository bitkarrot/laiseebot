import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv';

// python library does not have auth methods yet, temp use the js library
async function del_user(uuid) {
    const dot = dotenv.config()
    //console.log(process.env.SUPABASE_URL)
    const supa_url = process.env['SUPABASE_URL']
    const supa_pub = process.env['SUPABASE_TEST_KEY']
    const supabase = createClient(supa_url, supa_pub)
    //console.log('supa url', supa_url)

    const supa_key = process.env['SUPABASE_KEY']  // service key
    const { user, error } = await supabase.auth.api.deleteUser(uuid, supa_key)
    if (user) {
       console.log(user)
    } 
    if (error) {
        console.log(error)
    }
}

const args = process.argv.slice(2)
const uuid = args[0]
//console.log("uuid given: ", uuid)
//const uuid = "02176c55-ef63-4275-a699-4277b8c4b24c"

await del_user(uuid)

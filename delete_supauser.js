import { createClient } from '@supabase/supabase-js'
import yaml from 'js-yaml'
import fs from 'fs'

// python library does not have auth methods yet, temp use the js library

async function del_user(uuid) {
    try {
        let fileContents = fs.readFileSync('./config.yml', 'utf8');
        let data = yaml.load(fileContents);
        const supa_url = data['SUPABASE_URL']
        const supa_pub = data['SUPABASE_PUB_KEY']
        const supa_key = data['SUPABASE_KEY']
        console.log("supabase url: " , supa_url)
        const supabase = createClient(supa_url, supa_pub)
        const { user, error } = await supabase.auth.api.deleteUser(uuid, supa_key)
        if (user) {
           console.log(user)
        } 
        if (error) {
            console.log(error)
        }
    } catch (e) {
        console.log(e);
    }
}

const args = process.argv.slice(2)
const uuid = args[0]
//console.log("uuid given: ", uuid)
//const uuid = "02176c55-ef63-4275-a699-4277b8c4b24c"

await del_user(uuid)

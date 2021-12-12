const shellJs = require('shelljs')
const fs = require('fs')
const path = require('path');
require('dotenv').config();

// no error checking, use at your own risk. 
const git_repo_path = 'public/.well-known/lnurlp/'
const repo_name = '/laisee-frontpage'

const USER = 'bitkarrot';
const REPO = 'github.com/bitkarrot' + repo_name;
const dirPath = path.join(__dirname,  "../" + repo_name);
console.log("dirPath: ", dirPath)

const PASS = process.env.GITPASS
console.log('PASS TOKEN: ', process.env.GITPASS)

const git = require('simple-git')();
const remote = `https://${USER}:${PASS}@${REPO}`;

console.log('Remote:', remote)
git.addConfig('user.email', 'send@laisee.org');
git.addConfig('user.name', 'sendlaisee');


// update file in the target github repo
async function gitRmSeq(filePath){
    git.cwd(dirPath)
    console.log("status: ", git.status());
    console.log(">> Attempting to Delete file: ", filePath)

    await git.rm(filePath)
        .then(
            (rmSuccess) => {
                console.log("Rm Success: ", rmSuccess);
            }, (failedRm) => {
                console.log('removing files failed');
            });
}

async function gitAddSeq(filePath) {
    // Add file for commit and push
    git.cwd(dirPath)
    console.log("status: ", git.status());
    console.log(">> Attempting to add file: ", filePath)

    await git.add(filePath)
        .then(
            (addSuccess) => {
                console.log("Add Success: ", addSuccess);
            }, (failedAdd) => {
                console.log('adding files failed');
            });
}

async function gitCommitPush(msg_header) {
    const d = new Date().toUTCString()
    const msg = msg_header + d
    console.log("commit message", msg)

    // Commit files as Initial Commit
    await git.commit(msg)
        .then(
            (successCommit) => {
                console.log("Commit success: ", successCommit);
            }, (failed) => {
                console.log('failed commmit');
            });
    // Finally push to online repository
    await git.push('origin', 'main') // make sure correct branch!
        .then((success) => {
            console.log('repo successfully pushed', success);
        }, (failed) => {
            console.log('repo push failed', failed);
        });
}


// start here, check if repo exists, else clone it
async function main() {
    console.log("starting git update ")
    if (fs.existsSync(dirPath)) {
        console.log("check if file exists", dirPath)
        shellJs.cd(dirPath);
        console.log(shellJs.ls())
        const status = await git.checkIsRepo()
        console.log("is repo? ", status)
    } else {
        const rest = await git.clone(remote, dirPath)
        console.log("is repo cloned? ", rest)
        shellJs.cd(dirPath);
        console.log(shellJs.ls())
    }
    git.cwd(dirPath)
    console.log("dirpath", dirPath)
    console.log("direname", __dirname)
}

async function processAction(action, filePath) { 
    if (action === '-a') {
        const result = git.pull()
        console.log("git pull: ", result)
        await gitAddSeq(filePath)
        console.log("-a flag to add file", result)
        await gitCommitPush("Added on: ")

    } else if (action === '-d') {
        const result = git.pull()
        console.log("git pull: ", result)
        await gitRmSeq(filePath)
        console.log("-d flag to delete file", result)
        await gitCommitPush("Deleted on: ")

    } else if (action === '-p') { 
        const result = git.pull()
        console.log("git pull: ", result)
        const status = await git.status();
        console.log('git status: ', status)
    } else if (action === '-m') {
        try {
            const mergeSummary = await git.merge();
            console.log(`Merged ${ mergeSummary.merges.length } files`);
          }
          catch (err) {
            // err.message - the string summary of the error
            // err.stack - some stack trace detail
            // err.git - where a parser was able to run, this is the parsed content          
            console.error(`Merge resulted in ${ err.git } conflicts`);
            console.log(`error message: ${err.message}`);
          }
          
    }
}

// target_file = "newuser123" // test example

// todo: check args and process
const args = process.argv.slice(2)
const action = args[0]
const target_file = args[1]
const filePath = git_repo_path + target_file

const res = main()
console.log('Result from main() : ', res)

processAction(action, filePath)
console.log("=== Process Action End ===")

//  $ node update_git.cjs -a test1234
//  $ node update_git.cjs -d test1234
//  $ node update_git.cjs -p

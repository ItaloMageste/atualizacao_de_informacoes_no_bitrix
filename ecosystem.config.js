require("dotenv").config()

const restartDelay = process.env.SECONDS_TO_RESTART * 1000
const interpreter = process.env.PYTHON_INTERPRETER_PATH
const botName = process.env.BOT_NAME

module.exports = {
    apps: [
        {
            name: botName,
            script: "main.py",
            restart_delay: restartDelay,
            interpreter: interpreter
        },
    ]
}

const { exec } = require('child_process');

function ShutDown() {
    exec('shutdown /s /t 0', (error) => {
        if (error) {
            return { success: false, message: error.message };
        }
        return { success: true };
    });
    return { success: true };
}

module.exports = { ShutDown };
const { exec } = require('child_process');

function ShutDown() {
    exec('shutdown /s /t 0', (error) => {
        if (error) {
            console.error(JSON.stringify({ success: false, error: error.message }));
            process.exit(1);
        }
        console.log(JSON.stringify({ success: true }));
    });
}

if (require.main === module) {
    try {
        const params = JSON.parse(process.argv[2] || '{}');
        ShutDown(params);
    } catch (e) {
        console.error(JSON.stringify({ success: false, error: e.message }));
        process.exit(1);
    }
}

module.exports = { ShutDown };

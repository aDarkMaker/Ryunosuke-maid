process.stdout.setEncoding('utf8');

class TimeQuery {
    constructor() {
        // Init
    }

    getCurrentTime() {
        const now = new Date();

        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');

        const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
        const weekday = weekdays[now.getDay()];

        const dateStr = `${year}年${month}月${day}日`;
        const timeStr = `${hours}:${minutes}:${seconds}`;
        const fullTimeStr = `${dateStr} ${weekday} ${timeStr}`;

        return {
            success: true,
            data: {
                year: year,
                month: month,
                day: day,
                weekday: weekday,
                hours: hours,
                minutes: minutes,
                seconds: seconds,
                timestamp: now.getTime(),
                iso_string: now.toISOString(),
                date_string: dateStr,
                time_string: timeStr,
                full_string: fullTimeStr
            },
            message: `现在是${fullTimeStr}`
        };
    }

    getTimeByFormat(format = 'full') {
        const now = new Date();

        switch (format.toLowerCase()) {
            case 'date':
                return `${now.getFullYear()}年${String(now.getMonth() + 1).padStart(2, '0')}月${String(now.getDate()).padStart(2, '0')}日`;
            case 'time':
                return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
            case 'datetime':
                return now.toLocaleString('zh-CN');
            case 'iso':
                return now.toISOString();
            case 'timestamp':
                return now.getTime().toString();
            default:
                return this.getCurrentTime();
        }
    }
}

const timeQuery = new TimeQuery();

// MCP 
async function main() {
    try {
        const args = process.argv.slice(2);
        let format = 'full';

        if (args.length > 0) {
            try {
                const params = JSON.parse(args[0]);
                format = params.format || params.type || 'full';
            } catch (e) {
                format = args[0] || 'full';
            }
        }

        let result;
        if (format === 'full') {
            result = timeQuery.getCurrentTime();
        } else {
            const timeStr = timeQuery.getTimeByFormat(format);
            result = {
                success: true,
                data: {
                    format: format,
                    time: timeStr
                },
                message: `当前${format === 'date' ? '日期' : format === 'time' ? '时间' : '时间'}是${timeStr}`
            };
        }

        console.log(JSON.stringify(result));

    } catch (error) {
        console.error('[Time] 执行失败:', error);
        const errorResult = {
            success: false,
            error: error.message || String(error),
            message: '很抱歉，时间查询服务暂时不可用。'
        };
        console.log(JSON.stringify(errorResult));
    }
}

function time(params = {}) {
    const format = params.format || 'full';
    if (format === 'full') {
        return timeQuery.getCurrentTime();
    } else {
        const timeStr = timeQuery.getTimeByFormat(format);
        return {
            success: true,
            data: {
                format: format,
                time: timeStr
            },
            message: `当前${format === 'date' ? '日期' : format === 'time' ? '时间' : '时间'}是${timeStr}`
        };
    }
}

if (require.main === module) {
    main();
}

module.exports = { time, TimeQuery };
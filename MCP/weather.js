process.stdout.setEncoding('utf8');

const crypto = require('crypto');
const https = require('https');
const fs = require('fs');
const path = require('path');

// 城市名称到拼音的映射
const CITY_PINYIN_MAP = {
    '北京': 'beijing',
    '上海': 'shanghai',
    '广州': 'guangzhou',
    '深圳': 'shenzhen',
    '杭州': 'hangzhou',
    '南京': 'nanjing',
    '武汉': 'wuhan',
    '成都': 'chengdu',
    '西安': 'xian',
    '重庆': 'chongqing',
    '天津': 'tianjin',
    '苏州': 'suzhou',
    '青岛': 'qingdao',
    '大连': 'dalian',
    '厦门': 'xiamen',
    '宁波': 'ningbo',
    '无锡': 'wuxi',
    '福州': 'fuzhou',
    '济南': 'jinan',
    '长沙': 'changsha',
    '郑州': 'zhengzhou',
    '沈阳': 'shenyang',
    '哈尔滨': 'haerbin',
    '长春': 'changchun',
    '石家庄': 'shijiazhuang',
    '太原': 'taiyuan',
    '合肥': 'hefei',
    '南昌': 'nanchang',
    '南宁': 'nanning',
    '昆明': 'kunming',
    '贵阳': 'guiyang',
    '兰州': 'lanzhou',
    '西宁': 'xining',
    '银川': 'yinchuan',
    '乌鲁木齐': 'wulumuqi',
    '拉萨': 'lasa',
    '海口': 'haikou',
    '三亚': 'sanya'
};

// 天气代码映射
const WEATHER_CODES = {
    0: '晴',
    1: '晴',
    2: '晴',
    3: '晴',
    4: '多云',
    5: '晴间多云',
    6: '晴间多云',
    7: '大部多云',
    8: '大部多云',
    9: '阴',
    10: '阵雨',
    11: '雷阵雨',
    12: '雷阵雨伴有冰雹',
    13: '小雨',
    14: '中雨',
    15: '大雨',
    16: '暴雨',
    17: '大暴雨',
    18: '特大暴雨',
    19: '冻雨',
    20: '雨夹雪',
    21: '阵雪',
    22: '小雪',
    23: '中雪',
    24: '大雪',
    25: '暴雪',
    26: '浮尘',
    27: '扬沙',
    28: '沙尘暴',
    29: '强沙尘暴',
    30: '雾',
    31: '霾',
    32: '风',
    33: '大风',
    34: '飓风',
    35: '热带风暴',
    36: '龙卷风',
    37: '冷',
    38: '热',
    99: '未知'
};

class WeatherQuery {
    constructor() {
        // 默认配置
        this.uid = "";
        this.key = "";
        this.api = "https://api.seniverse.com/v3/weather/now.json";

        // 读取配置文件
        this.loadConfig();
    }

    loadConfig() {
        try {
            const configPath = path.join(__dirname, 'weather.conf');
            if (fs.existsSync(configPath)) {
                const configContent = fs.readFileSync(configPath, 'utf8');
                const lines = configContent.split('\n');

                let currentSection = '';
                for (const line of lines) {
                    const trimmedLine = line.trim();
                    if (trimmedLine.startsWith('[') && trimmedLine.endsWith(']')) {
                        currentSection = trimmedLine.slice(1, -1);
                    } else if (trimmedLine.includes('=') && currentSection === 'api') {
                        const [key, value] = trimmedLine.split('=').map(s => s.trim());
                        if (key === 'UID') {
                            this.uid = value;
                        } else if (key === 'KEY') {
                            this.key = value;
                        }
                    }
                }
            }
        } catch (error) {
            console.error('[Weather] 读取配置文件失败:', error.message);
        }
    }

    extractCityFromText(text) {

        // 从用户输入中提取城市名称
        for (const [city, pinyin] of Object.entries(CITY_PINYIN_MAP)) {
            if (text.includes(city)) {
                return { city, pinyin };
            }
        }
        return { city: '北京', pinyin: 'beijing' };
    }

    generateSignature(ts) {
        // 生成API签名
        const strToSign = `ts=${ts}&uid=${this.uid}`;
        const signature = crypto.createHmac('sha1', this.key)
            .update(strToSign)
            .digest('base64');
        return encodeURIComponent(signature);
    }

    async queryWeather(locationPinyin) {
        return new Promise((resolve, reject) => {
            const ts = Math.floor(Date.now() / 1000);
            const sig = this.generateSignature(ts);
            const url = `${this.api}?location=${locationPinyin}&ts=${ts}&uid=${this.uid}&sig=${sig}`;

            https.get(url, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    try {
                        const result = JSON.parse(data);
                        resolve(result);
                    } catch (error) {
                        console.error('[Weather] 解析JSON失败:', error);
                        reject({
                            success: false,
                            error: '解析天气数据失败',
                            raw_data: data
                        });
                    }
                });
            }).on('error', (error) => {
                console.error('[Weather] API请求失败:', error);
                reject({
                    success: false,
                    error: `网络请求失败: ${error.message}`
                });
            });
        });
    }

    formatWeatherResponse(weatherData, cityName) {
        try {
            if (weatherData.status_code && weatherData.status_code !== 0) {
                return {
                    success: false,
                    error: `API错误: ${weatherData.status || '未知错误'}`,
                    message: `很抱歉，无法获取${cityName}的天气信息。`
                };
            }

            if (!weatherData.results || weatherData.results.length === 0) {
                return {
                    success: false,
                    error: '没有找到天气数据',
                    message: `很抱歉，没有找到${cityName}的天气信息。`
                };
            }

            const result = weatherData.results[0];
            const now = result.now;
            const location = result.location;

            // 获取天气描述
            const weatherCode = parseInt(now.code);
            const weatherDesc = WEATHER_CODES[weatherCode] || now.text || '未知';

            // 格式化回复 - 修复体感温度显示问题
            let message = `${location.name}现在的天气是${weatherDesc}，温度${now.temperature}度`;

            // 只有当体感温度存在且不为undefined时才显示
            if (now.feels_like && now.feels_like !== 'undefined') {
                message += `，体感温度${now.feels_like}度`;
            }
            message += '。';

            return {
                success: true,
                data: {
                    city: location.name,
                    weather: weatherDesc,
                    temperature: now.temperature,
                    feels_like: now.feels_like || null,
                    humidity: now.humidity || null,
                    visibility: now.visibility || null,
                    pressure: now.pressure || null,
                    wind_direction: now.wind_direction || null,
                    wind_speed: now.wind_speed || null,
                    code: now.code,
                    last_update: result.last_update
                },
                message: message
            };
        } catch (error) {
            console.error('[Weather] 格式化天气数据失败:', error);
            return {
                success: false,
                error: `格式化数据失败: ${error.message}`,
                message: `很抱歉，处理${cityName}的天气信息时出现错误。`
            };
        }
    }
}

const weatherQuery = new WeatherQuery();

// MCP
async function main() {
    try {
        const args = process.argv.slice(2);
        let userInput = '';

        if (args.length > 0) {
            try {
                const params = JSON.parse(args[0]);
                userInput = params.userInput || params.text || '';
            } catch (e) {
                userInput = args[0];
            }
        }

        const { city, pinyin } = weatherQuery.extractCityFromText(userInput);

        const weatherData = await weatherQuery.queryWeather(pinyin);

        const result = weatherQuery.formatWeatherResponse(weatherData, city);

        console.log(JSON.stringify(result));

    } catch (error) {
        console.error('[Weather] 执行失败:', error);
        const errorResult = {
            success: false,
            error: error.message || String(error),
            message: '很抱歉，天气查询服务暂时不可用。'
        };
        console.log(JSON.stringify(errorResult));
    }
}

if (require.main === module) {
    main();
}

module.exports = { WeatherQuery };
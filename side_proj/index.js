const latToCyrTransliterationList = [
    // Сначала трёхбуквенные комбинации
    ["SCH", "Щ"],
    ["IEV", "ИЕВ"],
    
    // Двухбуквенные комбинации
    ["YO", "Ё"],
    ["YU", "Ю"],
    ["YA", "Я"],
    ["KH", "Х"],
    ["ZH", "Ж"],
    ["TS", "Ц"],
    ["CH", "Ч"],
    ["SH", "Ш"],
    ["AI", "АЙ"],
    ["EI", "ЕЙ"],
    ["YI", "ЫЙ"],
    ["YY", "ЫЙ"],
    ["YE", "ЫЕ"],
    ["EY", "ЕЙ"],
    ["AE", "АЕ"],
    ["IE", "ИЕ"],
    ["EV", "ЕВ"],
    
    // Однобуквенные комбинации
    ["A", "А"],
    ["B", "Б"],
    ["V", "В"],
    ["G", "Г"],
    ["D", "Д"],
    ["E", "Е"], // По умолчанию E -> Е
    ["Z", "З"],
    ["I", "И"],
    ["Y", "Ы"],
    ["K", "К"],
    ["L", "Л"],
    ["M", "М"],
    ["N", "Н"],
    ["O", "О"],
    ["P", "П"],
    ["R", "Р"],
    ["S", "С"],
    ["T", "Т"],
    ["U", "У"],
    ["F", "Ф"]
]

const transalitLatToCyr = (str) => {
    // Преобразуем входную строку в верхний регистр
    str = str.toUpperCase();
    
    let result = "";
    let i = 0;
    
    while (i < str.length) {
        let matched = false;
        
        // Проверяем трёхбуквенные комбинации
        if (i + 2 < str.length) {
            const threeChars = str.substring(i, i + 3);
            const threeCharMatch = latToCyrTransliterationList.find(([lat]) => lat === threeChars);
            
            if (threeCharMatch) {
                result += threeCharMatch[1];
                i += 3;
                matched = true;
                continue;
            }
        }
        
        // Проверяем двухбуквенные комбинации
        if (i + 1 < str.length) {
            const twoChars = str.substring(i, i + 2);
            const twoCharMatch = latToCyrTransliterationList.find(([lat]) => lat === twoChars);
            
            if (twoCharMatch) {
                result += twoCharMatch[1];
                i += 2;
                matched = true;
                continue;
            }
        }
        
        // Специальная обработка буквы E
        if (str[i] === 'E') {
            // E в начале слова или после гласных становится Э
            if (i === 0 || str[i-1] === ' ' || /[AEIOUY]/.test(str[i-1])) {
                result += 'Э';
            } else {
                result += 'Е';
            }
            i++;
            continue;
        }
        
        // Проверяем однобуквенные комбинации
        if (!matched) {
            const oneChar = str[i];
            const oneCharMatch = latToCyrTransliterationList.find(([lat]) => lat === oneChar);
            
            if (oneCharMatch) {
                result += oneCharMatch[1];
            } else {
                // Если символ не найден в таблице транслитерации, оставляем его без изменений
                result += oneChar;
            }
            i++;
        }
    }
    
    return result;
};

function runTests() {
    const tests = [
        // Реальные тест-кейсы с именами
        ["Bakeev Taalay Dzhaparbekovich", "БАКЕЕВ ТААЛАЙ ДЖАПАРБЕКОВИЧ"],
        ["Karmyshakova Gulsara Aytmamatovna", "КАРМЫШАКОВА ГУЛЬСАРА АЙТМАМАТОВНА"],
        ["Bykovets Andrei Anatolievich", "БЫКОВЕЦ АНДРЕЙ АНАТОЛЬЕВИЧ"],
        ["Pilipenko Malelya Igorevna", "ПИЛИПЕНКО МАЛЕЛЯ ИГОРЕВНА"],
        ["Ibraev Ruslan Kubatovich", "ИБРАЕВ РУСЛАН КУБАТОВИЧ"],
        ["Park Ki Suk", "ПАРК КИСОК"],
        ["Alieva Nurzat", "АЛИЕВА НУРЗАТ"],
        ["Zhyrgalbekov Adilet Zhyrgalbekovich", "ЖЫРГАЛБЕКОВ АДИЛЕТ ЖЫРГАЛБЕКОВИЧ"],
        ["Kubatbekova Kanykey Kubatbekovna", "КУБАТБЕКОВА КАНЫКЕЙ КУБАТБЕКОВНА"],
        ["Ashymkozhoeva Zhiidegul Ishenbekovn", "АШЫМКОЖОЕВА ЖИЙДЕГУЛ ИШЕНБЕКОВНА"],
        ["Abdyldaev Maksat Tursunbaevich", "АБДЫЛДАЕВ МАКСАТ ТУРСУНБАЕВИЧ"],
        ["Sultanova Diana", "СУЛТАНОВА ДИАНА"],
        ["Akiev Aydar Emilbekovich", "АКИЕВ АЙДАР ЭМИЛБЕКОВИЧ"],
        ["Mambetov Adilet Kamchybekovich", "МАМБЕТОВ АДИЛЕТ КАМЧЫБЕКОВИЧ"],
        ["Aitbaev Rashid Egemberdievich", "АЙТБАЕВ РАШИД ЭГЕМБЕРДИЕВИЧ"],
        ["Turgunbekov Eldiyar Baktiyarovich", "ТУРГУНБЕКОВ ЭЛДИЯР БАКТИЯРОВИЧ"],
        ["Golubaeva Aziza Anvarbekovna", "ГОЛУБАЕВА АЗИЗА АНВАРБЕКОВНА"],
        ["Beyshenbekov Dastan Beyshenbekovich", "БЕЙШЕНБЕКОВ ДАСТАН БЕЙШЕНБЕКОВИЧ"],
        ["Shamshiev Mederbek Asildinovich", "ШАМШИЕВ МЕДЕРБЕК АСИЛДИНОВИЧ"],
        ["Kochkonova Roza Zhanibekovna", "КОЧКОНОВА РОЗА ЖАНИБЕКОВНА"],
        ["Abdinasir Uulu Bektursun", "АБДИНАСИР УУЛУ БЕКТУРСУН"],
        ["Sydykova Tinatin Turatbekovna", "СЫДЫКОВА ТИНАТИН ТУРАТБЕКОВНА"],
        ["Kerimbekova Aigerim Kutmanovna", "КЕРИМБЕКОВА АЙГЕРИМ КУТМАНОВНА"],
        ["Zhenishbek Uulu Azamat", "ЖЕНИШБЕК УУЛУ АЗАМАТ"],
        ["Talypova Asel Kubatbekovna", "ТАЛЫПОВА АСЕЛЬ КУБАТБЕКОВНА"],
        ["Mambetova Tumar Kalybekovna", "МАМБЕТОВА ТУМАР КАЛЫБЕКОВНА"]
    ];

    let allPassed = true;
    tests.forEach(([input, expected], index) => {
        const result = transalitLatToCyr(input);
        const passed = result === expected;
        console.log(
            `Тест ${index + 1}: ${passed ? '✅' : '❌'} ` +
            `Вход: "${input}" => Ожидается: "${expected}" => Получено: "${result}"`
        );
        if (!passed) allPassed = false;
    });

    console.log('\nИтог:', allPassed ? '✅ Все тесты пройдены' : '❌ Есть ошибки');
}

// Запуск тестов
runTests();
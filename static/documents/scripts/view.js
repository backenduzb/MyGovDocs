var foiz = 100;
const menuBtn = document.getElementById('menu-btn');
menuBtn.onclick = () => {
    document.body.classList.remove('pg');

    document.body.classList.remove('save-as-open');
    document.body.classList.remove('others-open');
    document.body.classList.remove('zp');
    document.body.classList.toggle('sidebar-open');
};

const othersBtn = document.getElementById('other-btn');
othersBtn.onclick = () => {
    document.body.classList.remove('pg');

    document.body.classList.remove('sidebar-open');
    document.body.classList.remove('others-open');
    document.body.classList.remove('save-as-open');
    document.body.classList.remove('zp');
    document.body.classList.toggle('others-open');
};
const openZoomTools = document.getElementById('open-zoom-tools');

openZoomTools.onclick = () => {
    document.body.classList.remove('pg');
    document.body.classList.remove('sidebar-open');
    document.body.classList.remove('others-open');
    document.body.classList.remove('save-as-open');
    document.body.classList.toggle('zp');
};
const pgSettings = document.getElementById('pg-settings');

pgSettings.onclick = () => {
    document.body.classList.remove('sidebar-open');
    document.body.classList.remove('others-open');
    document.body.classList.remove('save-as-open');
    document.body.classList.toggle('pg');
    document.body.classList.remove('zp');

};
const cleaner = document.querySelectorAll('.clear-all');

cleaner.forEach(btn => {
    btn.onclick = () => {
        document.body.classList.remove('pg');
        document.body.classList.remove('others-open');
        document.body.classList.remove('save-as-open');
        document.body.classList.remove('zp');
    };
});



const saveAsBtn = document.getElementById('save-as-btn');
if (saveAsBtn) {
    saveAsBtn.onclick = () => {
        document.body.classList.remove('others-open');
        document.body.classList.toggle('save-as-open');
    };
}

const closeSaveBtn = document.getElementById('close-save-btn');
if (closeSaveBtn) {
    closeSaveBtn.onclick = () => {
        document.body.classList.remove('save-as-open');
    };
}

const fsBtn = document.getElementById('fullscreen-btn');
fsBtn.onclick = () => {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch((err) => {
            alert(`Fullscreen rejimga o'tilmadi: ${err.message}`);
        });
    } else {
        document.exitFullscreen();
    }
};

const fsBtn2 = document.getElementById('fullscreen-btn-2');
fsBtn2.onclick = () => {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch((err) => {
            alert(`Fullscreen rejimga o'tilmadi: ${err.message}`);
        });
    } else {
        document.exitFullscreen();
    }
};

const settingsBtn = document.getElementById('settings');

settingsBtn.onclick = () =>{
    document.body.classList.remove(
            'sidebar-open',
            'others-open',
            'save-as-open',
            'zoom-open',
            'page-open',
            'pg',
            'zp',
            'settings-opened'
    );
    document.body.classList.toggle('settings-opened');
}

const asides = [
    document.getElementById('sidebar'),
    document.getElementById('others'),
    document.getElementById('save-as'),
    document.getElementById('zoom-tools'),
    document.getElementById('page-control'),
    document.getElementById('pg'),
    document.getElementById('zp'),
    document.getElementById('settings-opened'),
];

const openButtons = [
    document.getElementById('menu-btn'),
    document.getElementById('other-btn'),
    document.getElementById('save-as-btn'),
    document.getElementById('open-zoom-tools'),
    document.getElementById('pg-settings'),
    document.getElementById('settings'),
    document.getElementById('language-select'),
];

document.addEventListener('click', (e) => {
    const clickedInsideAside = asides.some(
        aside => aside && aside.contains(e.target)
    );

    const clickedOpenButton = openButtons.some(
        btn => btn && btn.contains(e.target)
    );

    if (!clickedInsideAside && !clickedOpenButton) {
        document.body.classList.remove(
            'sidebar-open',
            'others-open',
            'save-as-open',
            'zoom-open',
            'page-open',
            'pg',
            'zp',
            'settings-opened'
        );
    }
});


const img = document.getElementById('pdf-img');
let scale = 1;
let rotation = 0;
let translateX = 0;
let translateY = 0;
let isDragging = false;
let startX = 0;
let startY = 0;
let rafId = null;

function applyTransform() {
    img.style.transform = `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale}) rotate(${rotation}deg)`;
    rafId = null;
}

function requestUpdate() {
    if (rafId) return;
    rafId = requestAnimationFrame(applyTransform);
}
const zoomPercentElement = document.getElementById('zoom-percent');

function updateZoomPercent() {
    const percent = Math.round(scale * 100);
    zoomPercentElement.textContent = `${percent}%`;
}
function updateLabel(foiz) {
    document.getElementById('zoom-percent').innerHTML = `${foiz}%`
}
updateZoomPercent();
document.getElementById('zoom-in').onclick = () => {
    scale += 0.1;
    foiz += 25;
    requestUpdate();
    updateLabel(foiz);
};

document.getElementById('zoom-out').onclick = () => {
    scale = Math.max(0.1, scale - 0.1);
    foiz -= 25;
    updateLabel(foiz);
    requestUpdate();
};

document.getElementById('rotate-cw').onclick = () => {
    rotation += 90;
    requestUpdate();
};

document.getElementById('rotate-ccw').onclick = () => {
    rotation -= 90;
    requestUpdate();
};

img.addEventListener('dragstart', e => e.preventDefault());

img.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX - translateX;
    startY = e.clientY - translateY;
    img.style.cursor = 'grabbing';
});

document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    translateX = e.clientX - startX;
    translateY = e.clientY - startY;
    requestUpdate();
});

document.addEventListener('mouseup', () => {
    isDragging = false;
    img.style.cursor = 'grab';
});

document.getElementById('save-file-btn').onclick = async () => {
    const nameInput = document.querySelector('.text-input');
    const type = document.getElementById('file-select').value;

    let fileName = nameInput.value.trim();
    if (!fileName) {
        alert("Имя файла не указано");
        return;
    }

    let fileUrl = "";
    let ext = "";

    if (type === "pdf") {
        fileUrl = "{{ doc.file.url }}";
        ext = ".pdf";
    } else if (type === "jpg") {
        fileUrl = "{{ pdf_preview }}";
        ext = ".jpg";
    }

    try {
        const response = await fetch(fileUrl);
        const blob = await response.blob();

        const blobUrl = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = fileName + ext;

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        URL.revokeObjectURL(blobUrl);
    } catch (e) {
        alert("Faylni yuklab bo‘lmadi");
        console.error(e);
    }
};

const translations = {
    ru: {
        // Header
        system_name: "Ижро интизоми",
        system_desc: "Идоралараро ягона электрон тизими",

        // Sidebar (Документ маълумотлари)
        signed_by: "Ким томонидан имзоланган",
        executor: "Ҳужжат ижрочиси",
        eri_issuer: "ЭРИ берган ташкилот",
        eri_validity: "ЭРИ амал қилиш муддати",
        signed_doc: "Имзоланган ҳужжат",

        // Others menu
        download: "Скачать",
        fullscreen: "Полно экранный",
        save_as: "Сохранить как",
        print: "Распечатать",
        settings: "Настройки",

        // Save As modal
        save_as_title: "Сохранить как",
        file_name: "Имя файла",
        file_type: "Тип файла",
        page_range: "Диапазон страниц",
        all_pages: "Все",
        current_page: "Текущая страница",
        specify_pages: "Укажите страницы",
        properties: "Характеристики",
        include_annotations: "Включить аннотации",
        include_comments: "Включить комментарии",
        save_file: "Сохранить файл",

        // Zoom tools
        zoom_percent: "100%", // dinamik o'zgaradi
        zoom_out: "Уменьшить",
        zoom_in: "Увеличить",
        fit_width: "Уместить по ширине",

        // Page control
        page_navigation: "Переход страниц",
        continuous: "Непрерывный",
        page_by_page: "Страница за страницей",
        rotate: "Повернуть",
        full_screen: "Полный экран",

        // Control panel
        continuous_short: "Непрерывный",
        page_by_page_short: "Страница за страницей"
    },

    en: {
        // Header
        system_name: "Execution Discipline",
        system_desc: "Interagency Unified Electronic System",

        // Sidebar
        signed_by: "Signed by",
        executor: "Document executor",
        eri_issuer: "ERI issuing organization",
        eri_validity: "ERI validity period",
        signed_doc: "Signed document",

        // Others menu
        download: "Download",
        fullscreen: "Full screen",
        save_as: "Save as",
        print: "Print",
        settings: "Settings",

        // Save As modal
        save_as_title: "Save as",
        file_name: "File name",
        file_type: "File type",
        page_range: "Page range",
        all_pages: "All",
        current_page: "Current page",
        specify_pages: "Specify pages",
        properties: "Properties",
        include_annotations: "Include annotations",
        include_comments: "Include comments",
        save_file: "Save file",

        zoom_percent: "100%",
        zoom_out: "Zoom out",
        zoom_in: "Zoom in",
        fit_width: "Fit to width",

        page_navigation: "Page navigation",
        continuous: "Continuous",
        page_by_page: "Page by page",
        rotate: "Rotate",
        full_screen: "Full screen",

        continuous_short: "Continuous",
        page_by_page_short: "Page by page"
    },

    uz_latin: {
        system_name: "Ijro intizomi",
        system_desc: "Idoralararo yagona elektron tizim",
        signed_by: "Kim tomonidan imzolangan",
        executor: "Hujjat ijrochisi",
        eri_issuer: "ERI bergan tashkilot",
        eri_validity: "ERI amal qilish muddati",
        signed_doc: "Imzolangan hujjat",
        download: "Yuklab olish",
        fullscreen: "To'liq ekran",
        save_as: "Saqlash nomi bilan",
        print: "Chop etish",
        settings: "Sozlamalar",

        save_as_title: "Saqlash nomi bilan",
        file_name: "Fayl nomi",
        file_type: "Fayl turi",
        page_range: "Sahifalar diapazoni",
        all_pages: "Barchasi",
        current_page: "Joriy sahifa",
        specify_pages: "Sahifalarni belgilang",
        properties: "Xususiyatlari",
        include_annotations: "Izohlarni qo'shish",
        include_comments: "Sharhlarni qo'shish",
        save_file: "Faylni saqlash",

        zoom_percent: "100%",
        zoom_out: "Kichraytirish",
        zoom_in: "Kattalashtirish",
        fit_width: "Kenglik bo'yicha moslash",

        page_navigation: "Sahifalar o'tish",
        continuous: "Doimiy",
        page_by_page: "Sahifama-sahifa",
        rotate: "Aylantirish",
        full_screen: "To'liq ekran",

        continuous_short: "Doimiy",
        page_by_page_short: "Sahifama-sahifa"
    },

    uz_cyrillic: {
        system_name: "Ижро интизоми",
        system_desc: "Идоралараро ягона электрон тизим",

        signed_by: "Ким томонидан имзоланган",
        executor: "Ҳужжат ижрочиси",
        eri_issuer: "ЭРИ берган ташкилот",
        eri_validity: "ЭРИ амал қилиш муддати",
        signed_doc: "Имзоланган ҳужжат",

        download: "Юклаб олиш",
        fullscreen: "Тўлиқ экран",
        save_as: "Ном билан сақлаш",
        print: "Чоп этиш",
        settings: "Созламалар",

        save_as_title: "Ном билан сақлаш",
        file_name: "Файл номи",
        file_type: "Файл тури",
        page_range: "Саҳифалар диапозони",
        all_pages: "Барчаси",
        current_page: "Жорий саҳифа",
        specify_pages: "Саҳифаларни белгиланг",
        properties: "Хусусиятлари",
        include_annotations: "Изоҳларни қўшиш",
        include_comments: "Шарҳларни қўшиш",
        save_file: "Файлни сақлаш",

        zoom_percent: "100%",
        zoom_out: "Кичиклаштириш",
        zoom_in: "Катталаштириш",
        fit_width: "Кенглик бўйича мослаш",

        page_navigation: "Саҳифалар ўтиш",
        continuous: "Доимий",
        page_by_page: "Саҳифама-саҳифа",
        rotate: "Айлантириш",
        full_screen: "Тўлиқ экран",

        continuous_short: "Доимий",
        page_by_page_short: "Саҳифама-саҳифа"
    }
};

function setLanguage(lang) {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        el.textContent = translations[lang][key];
    });
}

const savedLang = localStorage.getItem('lang') || 'uz_cyrillic';
setLanguage(savedLang);

function changeLang(lang) {
    localStorage.setItem('lang', lang);
    setLanguage(lang);
}


// Theme toggle functionality
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const htmlElement = document.documentElement;

// Load saved theme from localStorage
const savedTheme = localStorage.getItem('theme') || 'light';
htmlElement.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

// Theme toggle event
themeToggle.addEventListener('click', () => {
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

// Update icon based on theme
function updateThemeIcon(theme) {
    if (theme === 'dark') {
        // Moon icon for dark mode
        themeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
        `;
    } else {
        // Sun icon for light mode
        themeIcon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
        `;
    }
}
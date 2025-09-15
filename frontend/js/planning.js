// frontend\js\planning.js

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Зум изображения
    const img = document.querySelector('main img');
    if (img) {
        let isZoomed = false;
        img.addEventListener('click', () => {
            isZoomed = !isZoomed;
            img.style.transform = isZoomed ? 'scale(1.2)' : 'scale(1)';
            img.style.transition = 'transform 0.3s ease';
        });
    }

    // 2. Загружаем данные
    await loadUserOrfoData();

    // 3. Слушатели на textarea
    const textareas = document.querySelectorAll('textarea[name^="user-input-orf-"]');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', () => {
            saveOrfoData(textarea.name, textarea.value);
        });
    });
});

async function loadUserOrfoData() {
    try {
        const response = await fetch('/api/load-orfo', {
            method: 'GET',
            credentials: 'same-origin'
        });

        if (!response.ok) throw new Error("Ошибка загрузки данных");

        const data = await response.json();

        for (const [fieldName, content] of Object.entries(data)) {
            const textarea = document.querySelector(`textarea[name="${fieldName}"]`);
                if (textarea) {
                    textarea.value = content || '';
                }
            }
        } catch (error) {
            console.error("Ошибка:", error);
        }
    }

async function saveOrfoData(field, content) {
    try {
        // Отправляем только одно поле — как в /api/save-orfo
        const response = await fetch('/api/save-orfo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ field, content })
        });

        if (!response.ok) throw new Error("Ошибка сохранения");
    } catch (error) {
        console.error("Ошибка сохранения:", error);
    }
}
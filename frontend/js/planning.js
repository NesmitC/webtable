document.addEventListener('DOMContentLoaded', () => {
    const img = document.querySelector('main img');
    let isZoomed = false;

    img.addEventListener('click', () => {
        isZoomed = !isZoomed;
        img.style.transform = isZoomed ? 'scale(1.2)' : 'scale(1)';
        img.style.transition = 'transform 0.3s ease';
    });
});
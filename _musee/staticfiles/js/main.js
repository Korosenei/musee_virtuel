// ============================================
// Main JavaScript - Musée Virtuel
// ============================================

document.addEventListener('DOMContentLoaded', function() {

    // ============================================
    // Navigation Mobile
    // ============================================
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });
    }

    // Fermer le menu mobile lors du clic sur un lien
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                navMenu.classList.remove('active');
                mobileMenuBtn.classList.remove('active');
            }
        });
    });


    // ============================================
    // User Dropdown Menu
    // ============================================
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');

    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });

        // Fermer le dropdown en cliquant ailleurs
        document.addEventListener('click', function(e) {
            if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('show');
            }
        });
    }


    // ============================================
    // Search Modal
    // ============================================
    const searchBtn = document.getElementById('search-btn');
    const searchModal = document.getElementById('search-modal');
    const searchClose = document.getElementById('search-close');

    if (searchBtn && searchModal) {
        searchBtn.addEventListener('click', function() {
            searchModal.classList.add('active');
            const searchInput = searchModal.querySelector('input');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        });

        if (searchClose) {
            searchClose.addEventListener('click', function() {
                searchModal.classList.remove('active');
            });
        }

        // Fermer avec Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && searchModal.classList.contains('active')) {
                searchModal.classList.remove('active');
            }
        });

        // Fermer en cliquant sur le fond
        searchModal.addEventListener('click', function(e) {
            if (e.target === searchModal) {
                searchModal.classList.remove('active');
            }
        });
    }


    // ============================================
    // Messages Flash - Auto-dismiss
    // ============================================
    const messages = document.querySelectorAll('.message');

    messages.forEach(message => {
        const closeBtn = message.querySelector('.message-close');

        // Auto-dismiss après 5 secondes
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => message.remove(), 300);
        }, 5000);

        // Fermeture manuelle
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                message.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => message.remove(), 300);
            });
        }
    });


    // ============================================
    // Smooth Scroll pour les ancres
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });


    // ============================================
    // Lazy Loading Images
    // ============================================
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }


    // ============================================
    // Favoris - Toggle
    // ============================================
    const favoriteButtons = document.querySelectorAll('.btn-favorite');

    favoriteButtons.forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();

            const oeuvreId = this.dataset.oeuvreId;
            const isFavorite = this.classList.contains('is-favorite');
            const url = isFavorite
                ? `/oeuvre/${oeuvreId}/retirer-favori/`
                : `/oeuvre/${oeuvreId}/ajouter-favori/`;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    this.classList.toggle('is-favorite');

                    // Changer l'icône
                    const icon = this.querySelector('svg');
                    if (icon) {
                        if (this.classList.contains('is-favorite')) {
                            icon.innerHTML = '<path d="M8 3L9.5 6.5L13 7L10.5 9.5L11 13L8 11L5 13L5.5 9.5L3 7L6.5 6.5L8 3Z" fill="currentColor"/>';
                        } else {
                            icon.innerHTML = '<path d="M8 3L9.5 6.5L13 7L10.5 9.5L11 13L8 11L5 13L5.5 9.5L3 7L6.5 6.5L8 3Z" stroke="currentColor" stroke-width="1.5"/>';
                        }
                    }

                    // Message de confirmation
                    showNotification(
                        isFavorite ? 'Retiré des favoris' : 'Ajouté aux favoris',
                        'success'
                    );
                }
            } catch (error) {
                console.error('Erreur:', error);
                showNotification('Une erreur est survenue', 'error');
            }
        });
    });


    // ============================================
    // Enregistrement des visites
    // ============================================
    const detailPage = document.querySelector('[data-oeuvre-id]');

    if (detailPage) {
        const oeuvreId = detailPage.dataset.oeuvreId;
        const startTime = Date.now();

        // Enregistrer la visite au départ de la page
        window.addEventListener('beforeunload', function() {
            const duree = Math.floor((Date.now() - startTime) / 1000);

            // Utiliser sendBeacon pour un envoi fiable
            const formData = new FormData();
            formData.append('duree', duree);
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

            navigator.sendBeacon(
                `/oeuvre/${oeuvreId}/enregistrer-visite/`,
                formData
            );
        });
    }


    // ============================================
    // Formulaires AJAX
    // ============================================
    const ajaxForms = document.querySelectorAll('.ajax-form');

    ajaxForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const submitBtn = this.querySelector('[type="submit"]');

            // Désactiver le bouton
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Envoi...';
            }

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();

                if (data.success) {
                    showNotification(data.message || 'Opération réussie', 'success');
                    this.reset();
                } else {
                    showNotification(data.message || 'Une erreur est survenue', 'error');
                }
            } catch (error) {
                console.error('Erreur:', error);
                showNotification('Une erreur est survenue', 'error');
            } finally {
                // Réactiver le bouton
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Envoyer';
                }
            }
        });
    });


    // ============================================
    // Filtres dynamiques
    // ============================================
    const filterForm = document.querySelector('.filter-form');

    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('select, input[type="checkbox"]');

        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }


    // ============================================
    // Confirmation de suppression
    // ============================================
    const deleteButtons = document.querySelectorAll('.btn-delete');

    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const message = this.dataset.confirmMessage || 'Êtes-vous sûr de vouloir supprimer cet élément ?';

            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });


    // ============================================
    // Animation au scroll
    // ============================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const animateObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';

                setTimeout(() => {
                    entry.target.style.transition = 'all 0.6s ease-out';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);

                animateObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        animateObserver.observe(el);
    });

});


// ============================================
// Fonctions Utilitaires
// ============================================

// Récupérer le CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Afficher une notification
function showNotification(message, type = 'info') {
    const container = document.querySelector('.messages-container') || createMessagesContainer();

    const notification = document.createElement('div');
    notification.className = `message message-${type}`;

    const icons = {
        success: '<path d="M7 10L9 12L13 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>',
        error: '<path d="M7 7L13 13M7 13L13 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>',
        info: '<circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/><path d="M10 6V10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="10" cy="14" r="1" fill="currentColor"/>'
    };

    notification.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            ${icons[type] || icons.info}
        </svg>
        <span>${message}</span>
        <button class="message-close">&times;</button>
    `;

    container.appendChild(notification);

    // Auto-dismiss
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => notification.remove(), 300);
    }, 5000);

    // Fermeture manuelle
    notification.querySelector('.message-close').addEventListener('click', function() {
        notification.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => notification.remove(), 300);
    });
}

// Créer le conteneur de messages s'il n'existe pas
function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    document.body.appendChild(container);
    return container;
}

// Animation CSS pour slideOut
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(120%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

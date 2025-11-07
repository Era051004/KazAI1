// Простой и надежный менеджер чата
class SimpleChatManager {
    constructor() {
        this.init();
    }

    init() {
        console.log('💫 KazAI Chat инициализирован');
        this.setupEventListeners();
        this.scrollToBottom();
        this.autoResizeTextarea();
    }

    setupEventListeners() {
        const form = document.getElementById('chatForm');
        const textarea = document.querySelector('.message-input');

        // Обработка отправки формы
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Обработка клавиш в textarea
        if (textarea) {
            textarea.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    form.dispatchEvent(new Event('submit'));
                }
            });

            // Автофокус
            setTimeout(() => textarea.focus(), 100);
        }

        // Языковой переключатель
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }

    handleSubmit(e) {
        e.preventDefault();

        const textarea = document.querySelector('.message-input');
        const message = textarea.value.trim();

        if (!message) return;

        // Показываем индикатор загрузки
        this.showLoadingState();

        // Отправляем форму
        const form = document.getElementById('chatForm');
        const formData = new FormData(form);

        fetch('/send', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                // Перезагружаем страницу для показа нового сообщения
                window.location.reload();
            } else {
                throw new Error('Ошибка сервера');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            this.hideLoadingState();
            alert('Ошибка при отправке сообщения. Пожалуйста, попробуйте еще раз.');
        });
    }

    showLoadingState() {
        const textarea = document.querySelector('.message-input');
        const button = document.querySelector('.send-button');

        if (textarea) textarea.disabled = true;
        if (button) {
            button.disabled = true;
            button.innerHTML = '⏳';
        }
    }

    hideLoadingState() {
        const textarea = document.querySelector('.message-input');
        const button = document.querySelector('.send-button');

        if (textarea) {
            textarea.disabled = false;
            textarea.focus();
        }
        if (button) {
            button.disabled = false;
            button.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z"/>
                </svg>
            `;
        }
    }

    autoResizeTextarea() {
        const textarea = document.querySelector('.message-input');
        if (textarea) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
        }
    }

    scrollToBottom() {
        const container = document.getElementById('chatContainer');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new SimpleChatManager();
});